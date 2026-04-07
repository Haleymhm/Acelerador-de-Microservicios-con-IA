output "s3_bucket_name" {
  description = "The name of the S3 bucket"
  value       = aws_s3_bucket.documents_bucket.bucket
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.analysis_results.name
}

output "app_execution_role_arn" {
  description = "The ARN of the IAM role to attach to the execution environment"
  value       = aws_iam_role.app_execution_role.arn
}
