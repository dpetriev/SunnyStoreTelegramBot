import re
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from bot.utils.conversation import create_conversation_handler

from bot.handlers.base import BaseHandler
from bot.utils.states import STATES
from bot.utils.keyboards import (
    get_cancel_keyboard,
    get_yes_no_keyboard,
)

class DeleteItemHandler(BaseHandler):
    """Handler for deleting items."""

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the delete item conversation."""
        await update.message.reply_text(
            "Enter the 6-digit code of the item you want to delete:",
            reply_markup=get_cancel_keyboard()
        )
        return STATES['DELETE_CONFIRM']

    async def handle_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle item code input and ask for confirmation."""
        item_code = update.message.text.strip()
        
        # Validate code format
        if not re.fullmatch(r'\d{6}', item_code):
            await update.message.reply_text(
                "Invalid code format. Please enter a 6-digit code (e.g., '000001'):",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['DELETE_CONFIRM']

        item = self.db.get_item(item_code)
        if item:
            context.user_data['delete_item'] = item
            await update.message.reply_text(
                f"Are you sure you want to delete the item '{item.get('name', 'N/A')}' "
                f"with code '{item_code}'?",
                reply_markup=get_yes_no_keyboard()
            )
            return STATES['DELETE_CONFIRMATION']
        else:
            await update.message.reply_text(
                "Item not found. Please enter a valid 6-digit item code:",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['DELETE_CONFIRM']

    async def handle_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle deletion confirmation."""
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == 'yes':
            item = context.user_data.get('delete_item')
            if item:
                # Delete photo from S3 if exists
                photo_key = item.get('photo_key')
                if photo_key:
                    try:
                        self.storage.delete_file(photo_key)
                    except Exception as e:
                        self.logger.error(f"Error deleting photo from S3: {e}")

                # Delete item from database
                result = self.db.delete_item(item['_id'])
                if result.deleted_count > 0:
                    await query.edit_message_text(
                        f"Item '{item.get('name', 'N/A')}' with code "
                        f"'{item.get('code', 'N/A')}' deleted successfully!"
                    )
                else:
                    await query.edit_message_text("Failed to delete the item.")
            return ConversationHandler.END
        else:
            await query.edit_message_text("Deletion cancelled.")
            return ConversationHandler.END

    def get_handler(self):
        """Get the conversation handler for deleting items."""
        return create_conversation_handler(
            entry_points=[CommandHandler('delete', self.start)],
            states={
                STATES['DELETE_CONFIRM']: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_confirm),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
                STATES['DELETE_CONFIRMATION']: [
                    CallbackQueryHandler(self.handle_confirmation, pattern='^(yes|no)$'),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel),
                CallbackQueryHandler(self.cancel, pattern='^cancel$'),
            ]
        )