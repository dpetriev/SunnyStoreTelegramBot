import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot.services.database import DatabaseService
from bot.services.storage import StorageService

class BaseHandler:
    def __init__(self):
        self.db = DatabaseService()
        self.storage = StorageService()
        self.logger = logging.getLogger(self.__class__.__name__)

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the current operation and clean up."""
        try:
            # Clean up any temporary data
            if 'new_item' in context.user_data:
                # If there's a photo key, try to delete it from S3
                photo_key = context.user_data['new_item'].get('photo_key')
                if photo_key:
                    try:
                        self.storage.delete_file(photo_key)
                        self.logger.info(f"Deleted photo {photo_key} from S3")
                    except Exception as e:
                        self.logger.error(f"Error deleting photo {photo_key}: {e}")

                # If there are params with photos, delete those too
                for param in context.user_data['new_item'].get('params', []):
                    param_photo = param.get('photo_key')
                    if param_photo:
                        try:
                            self.storage.delete_file(param_photo)
                            self.logger.info(f"Deleted param photo {param_photo} from S3")
                        except Exception as e:
                            self.logger.error(f"Error deleting param photo {param_photo}: {e}")

            # Clean up user data
            context.user_data.clear()

            # Send cancellation message
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text("Operation cancelled.")
            else:
                await update.message.reply_text("Operation cancelled.")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            if update.callback_query:
                await update.callback_query.answer()
                await update.callback_query.edit_message_text(
                    "Operation cancelled with some cleanup errors."
                )
            else:
                await update.message.reply_text(
                    "Operation cancelled with some cleanup errors."
                )

        return ConversationHandler.END