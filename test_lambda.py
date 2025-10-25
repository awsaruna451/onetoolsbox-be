"""
Simple test to verify Lambda dependencies are working
"""
import json

def lambda_handler(event, context):
    """
    Simple test handler to verify Lambda is working
    """
    try:
        # Test if we can import the required modules
        import mangum
        import fastapi
        import pydantic
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'All dependencies loaded successfully',
                'modules': {
                    'mangum': mangum.__version__,
                    'fastapi': fastapi.__version__,
                    'pydantic': pydantic.__version__
                }
            })
        }
    except ImportError as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': f'Import error: {str(e)}',
                'message': 'Failed to import required modules'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': str(e),
                'message': 'Unexpected error'
            })
        }
