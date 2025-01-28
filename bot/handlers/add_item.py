import os
import uuid
import logging
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
    get_skip_keyboard,
    get_yes_no_keyboard,
    get_size_keyboard,
)

logger = logging.getLogger(__name__)

class AddItemHandler(BaseHandler):
    """Handler for adding new items."""

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the add item conversation."""
        context.user_data.clear()  # Clear any previous data
        context.user_data['new_item'] = {}
        context.user_data['current_state'] = STATES['ADD_NAME']
        await update.message.reply_text(
            "Enter the item name:",
            reply_markup=get_cancel_keyboard()
        )
        return STATES['ADD_NAME']

    async def handle_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle item name input."""
        text = update.message.text
        context.user_data['new_item']['name'] = text
        context.user_data['current_state'] = STATES['ADD_WHOLESALE_PRICE']
        await update.message.reply_text(
            "Enter the wholesale price (or tap 'Skip'):",
            reply_markup=get_skip_keyboard()
        )
        return STATES['ADD_WHOLESALE_PRICE']

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries."""
        query = update.callback_query
        await query.answer()
        data = query.data
        current_state = context.user_data.get('current_state')

        if data == 'cancel':
            await self.cancel(update, context)
            return ConversationHandler.END
        elif data == 'skip':
            if current_state == STATES['ADD_WHOLESALE_PRICE']:
                context.user_data['new_item']['wholesalePrice'] = None
                await query.edit_message_text(
                    "Enter the selling price (or tap 'Skip'):",
                    reply_markup=get_skip_keyboard()
                )
                return STATES['ADD_SELLING_PRICE']
            elif current_state == STATES['ADD_SELLING_PRICE']:
                context.user_data['new_item']['sellingPrice'] = None
                await query.edit_message_text(
                    "Enter the item description (or tap 'Skip'):",
                    reply_markup=get_skip_keyboard()
                )
                return STATES['ADD_DESCRIPTION']
            elif current_state == STATES['ADD_DESCRIPTION']:
                context.user_data['new_item']['description'] = None
                await query.edit_message_text(
                    "Please send a photo of the item (or tap 'Skip'):",
                    reply_markup=get_skip_keyboard()
                )
                return STATES['ADD_PHOTO']
            elif current_state == STATES['ADD_PHOTO']:
                context.user_data['new_item']['photo_key'] = None
                await query.edit_message_text(
                    "Do you want to add parameters?",
                    reply_markup=get_yes_no_keyboard()
                )
                return STATES['ADD_PARAMS']

    async def handle_wholesale_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle wholesale price input."""
        text = update.message.text
        try:
            context.user_data['new_item']['wholesalePrice'] = float(text)
        except ValueError:
            await update.message.reply_text(
                "Please enter a valid number for the wholesale price or tap 'Skip':",
                reply_markup=get_skip_keyboard()
            )
            return STATES['ADD_WHOLESALE_PRICE']

        await update.message.reply_text(
            "Enter the selling price (or tap 'Skip'):",
            reply_markup=get_skip_keyboard()
        )
        return STATES['ADD_SELLING_PRICE']

    async def handle_selling_price(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle selling price input."""
        text = update.message.text
        try:
            context.user_data['new_item']['sellingPrice'] = float(text)
        except ValueError:
            await update.message.reply_text(
                "Please enter a valid number for the selling price or tap 'Skip':",
                reply_markup=get_skip_keyboard()
            )
            return STATES['ADD_SELLING_PRICE']

        await update.message.reply_text(
            "Enter the item description (or tap 'Skip'):",
            reply_markup=get_skip_keyboard()
        )
        return STATES['ADD_DESCRIPTION']

    async def handle_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle description input."""
        text = update.message.text
        context.user_data['new_item']['description'] = text
        await update.message.reply_text(
            "Please send a photo of the item (or tap 'Skip'):",
            reply_markup=get_skip_keyboard()
        )
        return STATES['ADD_PHOTO']

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo input."""
        if update.message.photo:
            try:
                # Get the largest photo (best quality)
                photo_file = await update.message.photo[-1].get_file()
                unique_filename = f"{uuid.uuid4()}.jpg"
                temp_path = os.path.join("/tmp", unique_filename)
                
                try:
                    # Download photo
                    await photo_file.download_to_drive(temp_path)
                    
                    # Upload to S3
                    self.storage.upload_file(temp_path, unique_filename)
                    context.user_data['new_item']['photo_key'] = unique_filename
                    
                    logger.info(f"Successfully uploaded photo {unique_filename}")
                    
                except Exception as e:
                    logger.error(f"Error handling photo: {e}")
                    await update.message.reply_text(
                        "Sorry, there was an error processing your photo. Please try again or tap 'Skip':",
                        reply_markup=get_skip_keyboard()
                    )
                    return STATES['ADD_PHOTO']
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
            except Exception as e:
                logger.error(f"Error getting photo file: {e}")
                await update.message.reply_text(
                    "Sorry, there was an error with your photo. Please try again or tap 'Skip':",
                    reply_markup=get_skip_keyboard()
                )
                return STATES['ADD_PHOTO']
        else:
            await update.message.reply_text(
                "Please send a photo or tap 'Skip':",
                reply_markup=get_skip_keyboard()
            )
            return STATES['ADD_PHOTO']

        await update.message.reply_text(
            "Do you want to add parameters?",
            reply_markup=get_yes_no_keyboard()
        )
        return STATES['ADD_PARAMS']

    async def handle_params(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle parameters choice."""
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == 'yes':
            context.user_data['current_param'] = {}
            await query.edit_message_text(
                "Enter the color:",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['ADD_COLOR']
        else:
            code_str = self.db.get_next_code()
            context.user_data['new_item']['code'] = code_str
            self.db.add_item(context.user_data['new_item'])
            await query.edit_message_text(
                f"Item added successfully with code {code_str}!"
            )
            return ConversationHandler.END

    async def handle_color(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle color input."""
        text = update.message.text
        context.user_data['current_param']['color'] = text
        context.user_data['current_param']['stock'] = []
        await update.message.reply_text(
            "Please send a photo for this color (or tap 'Skip'):",
            reply_markup=get_skip_keyboard()
        )
        return STATES['ADD_COLOR_PHOTO']

    async def handle_color_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle color photo input."""
        if update.message.photo:
            try:
                # Get the largest photo (best quality)
                photo_file = await update.message.photo[-1].get_file()
                unique_filename = f"{uuid.uuid4()}.jpg"
                temp_path = os.path.join("/tmp", unique_filename)
                
                try:
                    # Download photo
                    await photo_file.download_to_drive(temp_path)
                    
                    # Upload to S3
                    self.storage.upload_file(temp_path, unique_filename)
                    context.user_data['current_param']['photo_key'] = unique_filename
                    
                    logger.info(f"Successfully uploaded color photo {unique_filename}")
                    
                except Exception as e:
                    logger.error(f"Error handling color photo: {e}")
                    await update.message.reply_text(
                        "Sorry, there was an error processing your photo. Please try again or tap 'Skip':",
                        reply_markup=get_skip_keyboard()
                    )
                    return STATES['ADD_COLOR_PHOTO']
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
            except Exception as e:
                logger.error(f"Error getting color photo file: {e}")
                await update.message.reply_text(
                    "Sorry, there was an error with your photo. Please try again or tap 'Skip':",
                    reply_markup=get_skip_keyboard()
                )
                return STATES['ADD_COLOR_PHOTO']
        else:
            await update.message.reply_text(
                "Please send a photo or tap 'Skip':",
                reply_markup=get_skip_keyboard()
            )
            return STATES['ADD_COLOR_PHOTO']

        await update.message.reply_text(
            "Select the size:",
            reply_markup=get_size_keyboard()
        )
        return STATES['ADD_STOCK_SIZE_RESPONSE']

    async def handle_stock_size_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle size selection."""
        query = update.callback_query
        await query.answer()
        size = query.data

        if size == 'Other':
            await query.edit_message_text(
                "Please enter the size:",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['ADD_STOCK_SIZE_RESPONSE_OTHER']
        else:
            context.user_data['current_stock'] = {'size': size}
            await query.edit_message_text(
                "Enter the quantity:",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['ADD_STOCK_QUANTITY']

    async def handle_stock_size_response_other(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle custom size input."""
        text = update.message.text
        context.user_data['current_stock'] = {'size': text}
        await update.message.reply_text(
            "Enter the quantity:",
            reply_markup=get_cancel_keyboard()
        )
        return STATES['ADD_STOCK_QUANTITY']

    async def handle_stock_quantity(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quantity input."""
        try:
            quantity = int(update.message.text)
            context.user_data['current_stock']['quantity'] = quantity
            context.user_data['current_param']['stock'].append(
                context.user_data['current_stock']
            )
            await update.message.reply_text(
                "Do you want to add another size?",
                reply_markup=get_yes_no_keyboard()
            )
            return STATES['ADD_MORE_STOCK']
        except ValueError:
            await update.message.reply_text(
                "Please enter a valid number for the quantity:",
                reply_markup=get_cancel_keyboard()
            )
            return STATES['ADD_STOCK_QUANTITY']

    async def handle_more_stock(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle more stock choice."""
        query = update.callback_query
        await query.answer()
        data = query.data

        if data == 'yes':
            await query.edit_message_text(
                "Select the size:",
                reply_markup=get_size_keyboard()
            )
            return STATES['ADD_STOCK_SIZE_RESPONSE']
        else:
            context.user_data['new_item'].setdefault('params', []).append(
                context.user_data['current_param']
            )
            await query.edit_message_text(
                "Do you want to add another color?",
                reply_markup=get_yes_no_keyboard()
            )
            return STATES['ADD_PARAMS']

    def get_handler(self):
        """Get the conversation handler for adding items."""
        handler = create_conversation_handler(
            entry_points=[CommandHandler('add', self.start)],
            states={
                STATES['ADD_NAME']: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_name),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
                STATES['ADD_WHOLESALE_PRICE']: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_wholesale_price),
                    CallbackQueryHandler(self.handle_callback, pattern='^(cancel|skip)$'),
                ],
                STATES['ADD_SELLING_PRICE']: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_selling_price),
                    CallbackQueryHandler(self.handle_callback, pattern='^(cancel|skip)$'),
                ],
                STATES['ADD_DESCRIPTION']: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_description),
                    CallbackQueryHandler(self.handle_callback, pattern='^(cancel|skip)$'),
                ],
                STATES['ADD_PHOTO']: [
                    MessageHandler((filters.PHOTO | filters.TEXT) & ~filters.COMMAND, self.handle_photo),
                    CallbackQueryHandler(self.handle_callback, pattern='^(cancel|skip)$'),
                ],
                STATES['ADD_PARAMS']: [
                    CallbackQueryHandler(self.handle_params, pattern='^(yes|no)$'),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
                STATES['ADD_COLOR']: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_color),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
                STATES['ADD_COLOR_PHOTO']: [
                    MessageHandler((filters.PHOTO | filters.TEXT) & ~filters.COMMAND, self.handle_color_photo),
                    CallbackQueryHandler(self.handle_callback, pattern='^(cancel|skip)$'),
                ],
                STATES['ADD_STOCK_SIZE_RESPONSE']: [
                    CallbackQueryHandler(self.handle_stock_size_response),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
                STATES['ADD_STOCK_SIZE_RESPONSE_OTHER']: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_stock_size_response_other),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
                STATES['ADD_STOCK_QUANTITY']: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_stock_quantity),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
                STATES['ADD_MORE_STOCK']: [
                    CallbackQueryHandler(self.handle_more_stock, pattern='^(yes|no)$'),
                    CallbackQueryHandler(self.cancel, pattern='^cancel$'),
                ],
            },
            fallbacks=[
                CommandHandler('cancel', self.cancel),
                CallbackQueryHandler(self.cancel, pattern='^cancel$'),
            ],
            name='add_item_conversation'  # Add a name for better logging
        )
        self.logger.info("Add item conversation handler created")
        return handler