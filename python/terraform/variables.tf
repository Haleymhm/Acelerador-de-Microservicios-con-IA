variable "aws_region" {
  description = "The AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "s3_bucket_name" {
  description = "The name of the S3 bucket for storing uploaded documents"
  type        = string
  default     = "risk-analysis-docs-bucket"
}

variable "dynamodb_table_name" {
  description = "The name of the DynamoDB table for analysis results"
  type        = string
  default     = "risk-analysis-results"
}
