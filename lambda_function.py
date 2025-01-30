import json
import os
from bot.bot import Bot

# Initialize bot
bot = Bot(
    token=os.environ['TELEGRAM_BOT_TOKEN'],
    mongodb_conn_string=os.environ['MONGODB_CONN_STRING'],
    s3_bucket_name=os.environ['S3_BUCKET_NAME']
)

def lambda_handler(event, context):
    try:
        # Parse the incoming update
        if 'body' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No body in request'})
            }

        update = json.loads(event['body'])
        
        # Process the update
        bot.process_update(update)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'ok'})
        }
        
    except Exception as e:
        print(f"Error processing update: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }