import uuid
import os
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from bot.utils.conversation import create_conversation_handler

from bot.handlers.base import BaseHandler
from bot.utils.states import STATES
from bot.utils.keyboards import (
    get_cancel_keyboard,
    get_field_keyboard,
)

class ChangeItemHandler(BaseHandler):
    """Handler for changing existing items."""

    EDITABLE_FIELDS = ['name', 'wholesalePrice', 'sellingPrice', 'description', 'photo']

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the change item conversation."""
        await update.message.reply_text(
            "Enter the 6-digit code of the item you want to change:",
            reply_markup=get_cancel_keyboard()
        )
        return STATES['CHANGE_CHOICE']

    async def handle_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle item code input."""
        item_code = update.message.text.strip()
        item = self.db.get_item(item_code)

        if item:
            context.user_data['edit_item'] = item
            await update.message.reply_text(
                f"Item found: {item.get('name', 'N/A')}\n"
                "What do you want to change?",
                reply_markup=get_field_keyboard(self.EDITABLE_FIELDS)
            )
            return STATES['CHANGE_FIELD']
        else:
            await update.message.reply_text(
                "Item not found. Please enter a valid 6-digit item code:",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['CHANGE_CHOICE']

    async def handle_field_choice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle field selection."""
        query = update.callback_query
        await query.answer()
        field = query.data
        context.user_data['edit_field'] = field

        if field in ['name', 'wholesalePrice', 'sellingPrice', 'description']:
            await query.edit_message_text(
                f"Enter the new value for {field}:",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['CHANGE_UPDATE']
        elif field == 'photo':
            await query.edit_message_text(
                "Please send the new photo:",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['CHANGE_UPDATE']
        else:
            await query.edit_message_text(
                "Invalid field selected. Please choose a valid field.",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['CHANGE_FIELD']

    async def handle_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle field update."""
        try:
            field = context.user_data.get('edit_field')
            item = context.user_data.get('edit_item')
            
            if not field or not item:
                await update.message.reply_text(
                    "Error: Missing field or item data. Please try again.",
                    reply_markup=get_cancel_keyboard()
                )
                return ConversationHandler.END
                
            item_id = item['_id']

            if field in ['name', 'description']:
                value = update.message.text.strip()
                if not value:
                    await update.message.reply_text(
                        f"Please enter a valid {field}:",
                        reply_markup=get_cancel_keyboard()
                    )
                    return STATES['CHANGE_UPDATE']
                    
                self.db.update_item(item_id, {field: value})
                await update.message.reply_text(f"{field.capitalize()} updated successfully!")
                return ConversationHandler.END

            elif field in ['wholesalePrice', 'sellingPrice']:
                try:
                    value = float(update.message.text.strip())
                    if value < 0:
                        raise ValueError("Price cannot be negative")
                        
                    self.db.update_item(item_id, {field: value})
                    await update.message.reply_text(f"{field.capitalize()} updated successfully!")
                    return ConversationHandler.END
                    
                except ValueError as e:
                    await update.message.reply_text(
                        f"Please enter a valid positive number: {str(e)}",
                        reply_markup=get_cancel_keyboard()
                    )
                    return STATES['CHANGE_UPDATE']

            elif field == 'photo':
                if update.message.photo:
                    try:
                        photo_file = await update.message.photo[-1].get_file()
                        unique_filename = f"{uuid.uuid4()}.jpg"
                        temp_path = os.path.join("/tmp", unique_filename)
                        
                        try:
                            # Download photo
                            await photo_file.download_to_drive(temp_path)
                            
                            # Upload to S3
                            self.storage.upload_file(temp_path, unique_filename)
                            
                            # Delete old photo if exists
                            old_photo = item.get('photo_key')
                            if old_photo:
                                try:
                                    self.storage.delete_file(old_photo)
                                except Exception as e:
                                    logger.warning(f"Failed to delete old photo {old_photo}: {e}")
                            
                            # Update database
                            self.db.update_item(item_id, {'photo_key': unique_filename})
                            await update.message.reply_text("Photo updated successfully!")
                            return ConversationHandler.END
                            
                        finally:
                            # Clean up temp file
                            if os.path.exists(temp_path):
                                os.remove(temp_path)
                                
                    except Exception as e:
                        await update.message.reply_text(
                            f"Error processing photo: {str(e)}. Please try again.",
                            reply_markup=get_cancel_keyboard()
                        )
                        return STATES['CHANGE_UPDATE']
                else:
                    await update.message.reply_text(
                        "Please send a photo:",
                        reply_markup=get_cancel_keyboard()
                    )
                    return STATES['CHANGE_UPDATE']
                    
            else:
                await update.message.reply_text(
                    f"Invalid field '{field}'. Please try again.",
                    reply_markup=get_cancel_keyboard()
                )
                return ConversationHandler.END
                
        except Exception as e:
            logger.error(f"Error in handle_update: {e}", exc_info=True)
            await update.message.reply_text(
                "An error occurred while updating the item. Please try again.",
                reply_markup=get_cancel_keyboard()
            )
            return ConversationHandler.END

    def get_handler(self):
        """Get the conversation handler for changing items."""
        return create_conversation_handler(
            entry_points=[CommandHandler('change', self.start)],
            states={
                STATES['CHANGE_CHOICE']: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_choice),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
                STATES['CHANGE_FIELD']: [
                    CallbackQueryHandler(self.handle_field_choice),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
                STATES['CHANGE_UPDATE']: [
                    MessageHandler(
                        (filters.TEXT | filters.PHOTO) & ~filters.COMMAND,
                        self.handle_update
                    ),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel),
                CallbackQueryHandler(self.cancel, pattern='^cancel$'),
            ]
        )