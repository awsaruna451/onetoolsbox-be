# AWS Lambda Deployment Setup Guide

This guide will help you set up AWS credentials for deploying the YouTube Caption Extractor API to AWS Lambda using GitHub Actions.

## Prerequisites

1. An AWS account
2. AWS CLI installed locally (optional, for testing)
3. GitHub repository with the code

## Step 1: Create AWS IAM User

1. **Log in to AWS Console**
   - Go to [AWS Console](https://console.aws.amazon.com/)
   - Sign in with your AWS account

2. **Navigate to IAM**
   - Search for "IAM" in the AWS services search bar
   - Click on "IAM" to open the Identity and Access Management console

3. **Create a New User**
   - Click on "Users" in the left sidebar
   - Click "Create user"
   - Enter a username (e.g., `youtube-caption-api-deployer`)
   - Click "Next"

4. **Attach Policies**
   - Select "Attach policies directly"
   - Search for and select the following policies:
     - `AWSLambdaFullAccess`
     - `IAMFullAccess`
     - `CloudFormationFullAccess`
     - `S3FullAccess`
     - `APIGatewayAdministrator`
   - Click "Next"
   - Click "Create user"

## Step 2: Create Access Keys

1. **Select the User**
   - Click on the user you just created
   - Go to the "Security credentials" tab
   - Scroll down to "Access keys" section

2. **Create Access Key**
   - Click "Create access key"
   - Select "Application running outside AWS"
   - Click "Next"
   - Add a description (e.g., "GitHub Actions deployment")
   - Click "Create access key"

3. **Save Credentials**
   - **IMPORTANT**: Copy and save both:
     - Access Key ID
     - Secret Access Key
   - You won't be able to see the secret key again!

## Step 3: Configure GitHub Secrets

1. **Go to Your Repository**
   - Navigate to your GitHub repository
   - Click on "Settings" tab

2. **Add Secrets**
   - Click on "Secrets and variables" → "Actions"
   - Click "New repository secret"
   - Add the following secrets:

   | Secret Name | Value | Description |
   |-------------|-------|-------------|
   | `AWS_ACCESS_KEY_ID` | Your Access Key ID | The access key ID from Step 2 |
   | `AWS_SECRET_ACCESS_KEY` | Your Secret Access Key | The secret access key from Step 2 |
   | `AWS_REGION` | `us-east-1` | AWS region (optional, defaults to us-east-1) |

## Step 4: Test the Deployment

1. **Trigger the Workflow**
   - Make a small change to your repository
   - Commit and push the changes
   - This will trigger the GitHub Actions workflow

2. **Monitor the Deployment**
   - Go to the "Actions" tab in your repository
   - Click on the latest workflow run
   - Monitor the deployment progress

## Step 5: Verify Deployment

After successful deployment, you should see:

1. **Lambda Function Created**
   - Go to AWS Lambda console
   - Look for a function named `youtube-caption-extractor-api-dev-api`

2. **API Gateway Created**
   - Go to API Gateway console
   - Look for an API named `youtube-caption-extractor-api-dev`

3. **Test the API**
   - The deployment will output an API endpoint URL
   - Test it with a simple health check: `GET /health`

## Troubleshooting

### Common Issues

1. **"Credentials could not be loaded"**
   - Ensure all three secrets are set in GitHub
   - Check that the secret names match exactly (case-sensitive)

2. **"Access Denied" errors**
   - Verify the IAM user has the required permissions
   - Check that the access keys are correct

3. **Deployment timeout**
   - The deployment might take 5-10 minutes
   - Check the GitHub Actions logs for specific errors

### Security Best Practices

1. **Rotate Access Keys Regularly**
   - Create new access keys every 90 days
   - Delete old access keys after confirming new ones work

2. **Use Least Privilege**
   - Only grant the minimum required permissions
   - Consider using AWS IAM roles instead of access keys for production

3. **Monitor Usage**
   - Set up CloudWatch alarms for unusual activity
   - Review IAM access logs regularly

## Cost Considerations

- **Lambda**: Pay per request (very low cost for most use cases)
- **API Gateway**: Pay per API call
- **CloudWatch**: Logs and monitoring (minimal cost)

For a typical small application, expect costs under $1-5/month.

## Next Steps

After successful deployment:

1. **Configure Custom Domain** (optional)
2. **Set up Monitoring and Alerts**
3. **Configure Environment Variables** for different stages
4. **Set up CI/CD for multiple environments** (dev, staging, prod)

## Support

If you encounter issues:

1. Check the GitHub Actions logs for detailed error messages
2. Verify AWS credentials and permissions
3. Ensure all required secrets are set in GitHub
4. Check AWS CloudFormation console for deployment stack status
