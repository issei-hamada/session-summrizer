# Lambda Document Processing with Claude AI

This project implements a serverless document processing pipeline using AWS Lambda and Claude AI. The system processes documents stored in S3 buckets using the Claude 3 Haiku model.

## Architecture

The application uses the following AWS services:
- AWS Lambda
- Amazon S3 (Source and Temporary buckets)
- Amazon SQS
- AWS IAM
- Claude AI (Anthropic)

## Prerequisites

- AWS Account
- AWS SAM CLI
- Python 3.11
- Appropriate AWS credentials and permissions

## Configuration

The following parameters can be configured in template.yaml:
- InvokeRegion (default: us-west-2)
- MaxTokens (default: 200000)
- ModelId (default: anthropic.claude-3-5-haiku-20241022-v1:0)

## Deployment

1. Install the AWS SAM CLI
2. Clone this repository
3. Run the following commands:
```bash
sam build
sam deploy --guided
```

## Usage

1. Upload a document to the source S3 bucket
2. The system will automatically:
   - Trigger the Lambda function via SQS
   - Process the document using Claude AI
   - Store results in the temporary bucket

## Environment Variables

The Lambda function uses the following environment variables:
- TEMP_BUCKET: Temporary storage bucket
- SOURCE_BUCKET: Source document bucket
- MAX_TOKENS: Maximum tokens for Claude AI
- MODEL_ID: Claude AI model identifier
- REGION_CONFIG: AWS region for invocation

## Security

The application uses IAM roles and policies to manage permissions securely. Make sure to review and adjust the permissions in template.yaml as needed for your use case.

## License

[Add appropriate license information]

## Process Flow

The system processes transcripts (.txt files) as follows:
1. Place input files in the temporary S3 bucket
2. The system automatically summarizes the content
3. Results are output to the target bucket
