import json
import logging
from mangum import Mangum
from telegram import Update
from bot.bot import create_application

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create the application
application = create_application()

async def telegram_webhook(event, context):
    """AWS Lambda handler for Telegram webhook"""
    try:
        # Parse the update
        if 'body' in event:
            update = Update.de_json(json.loads(event['body']), application.bot)
            await application.process_update(update)
            return {'statusCode': 200, 'body': 'ok'}
        return {'statusCode': 400, 'body': 'bad request'}
    except Exception as e:
        logger.error(f"Error processing update: {e}", exc_info=True)
        return {'statusCode': 500, 'body': str(e)}

# Create Mangum handler
handler = Mangum(telegram_webhook)