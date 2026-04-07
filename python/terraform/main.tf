terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ── S3 Bucket for Documents ───────────────────────────────────────────
resource "aws_s3_bucket" "documents_bucket" {
  bucket = var.s3_bucket_name
}

resource "aws_s3_bucket_server_side_encryption_configuration" "documents_bucket_sse" {
  bucket = aws_s3_bucket.documents_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# ── DynamoDB Table for Results ────────────────────────────────────────
resource "aws_dynamodb_table" "analysis_results" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "analysis_id"

  attribute {
    name = "analysis_id"
    type = "S"
  }
}

# ── IAM Role for ECS / AppRunner / Lambda ─────────────────────────────
resource "aws_iam_role" "app_execution_role" {
  name = "risk-analysis-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["ecs-tasks.amazonaws.com", "lambda.amazonaws.com"]
        }
      }
    ]
  })
}

# IAM Policy for S3 access
resource "aws_iam_role_policy" "s3_access" {
  name   = "risk-analysis-s3-access"
  role   = aws_iam_role.app_execution_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.documents_bucket.arn}/*"
      }
    ]
  })
}

# IAM Policy for DynamoDB access
resource "aws_iam_role_policy" "dynamodb_access" {
  name   = "risk-analysis-dynamodb-access"
  role   = aws_iam_role.app_execution_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.analysis_results.arn
      }
    ]
  })
}

# IAM Policy for Bedrock and Textract access
resource "aws_iam_role_policy" "bedrock_textract_access" {
  name   = "risk-analysis-ai-access"
  role   = aws_iam_role.app_execution_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = [
          "textract:DetectDocumentText",
          "textract:StartDocumentTextDetection",
          "textract:GetDocumentTextDetection"
        ]
        Resource = "*"
      }
    ]
  })
}
