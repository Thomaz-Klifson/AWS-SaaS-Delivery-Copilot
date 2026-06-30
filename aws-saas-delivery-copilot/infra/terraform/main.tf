
Terraform AWS Blueprint - Skeleton

terraform {
required_version = ">= 1.6.0"

required_providers {
aws = {
source = "hashicorp/aws"
version = "~> 5.0"
}
}
}

provider "aws" {
region = var.aws_region
}

variable "aws_region" {
type = string
default = "us-east-1"
}

Planned resources:
- S3 bucket for tenant documents and feedback files
- SQS queue for async feedback summarization jobs
- DynamoDB table for tenant/job metadata
- IAM role for Bedrock invocation
- CloudWatch log group
- ECS Fargate or Lambda deployment for FastAPI

