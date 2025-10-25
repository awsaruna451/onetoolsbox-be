"""
AWS Lambda handler for YouTube Caption Extractor API
"""
import json
from mangum import Mangum
from app.main import app

# Create ASGI adapter for Lambda
handler = Mangum(app, lifespan="off")


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    
    Args:
        event: Lambda event object
        context: Lambda context object
        
    Returns:
        API Gateway response
    """
    try:
        # Process the request through Mangum
        response = handler(event, context)
        
        # Add CORS headers if not present
        if 'headers' not in response:
            response['headers'] = {}
        
        # Ensure CORS headers are set
        cors_headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Allow-Credentials': 'false'
        }
        
        # Merge with existing headers
        response['headers'].update(cors_headers)
        
        return response
        
    except Exception as e:
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,X-Amz-User-Agent',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Credentials': 'false'
            },
            'body': json.dumps({
                'success': False,
                'error': 'Internal server error',
                'details': str(e)
            })
        }
