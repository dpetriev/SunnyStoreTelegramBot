import io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from bot.handlers.base import BaseHandler
from bot.config import ITEMS_PER_PAGE
from bot.utils.formatters import format_item_caption

class ListItemsHandler(BaseHandler):
    """Handler for listing items."""

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /list command."""
        await self.list_items(update, context)

    async def list_items(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List items with pagination."""
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            page = int(query.data.split('_')[1])
            chat_id = query.message.chat_id

            # Delete the previous page navigation message
            try:
                await context.bot.delete_message(
                    chat_id=chat_id,
                    message_id=query.message.message_id
                )
            except Exception as e:
                self.logger.error(f"Failed to delete previous navigation message: {e}")
        else:
            page = 0
            chat_id = update.message.chat_id

        total_items = self.db.clothes.count_documents({})
        total_pages = (total_items - 1) // ITEMS_PER_PAGE + 1

        if total_items == 0:
            await context.bot.send_message(
                chat_id=chat_id,
                text="No items found in the database."
            )
            return

        # Retrieve items for the current page
        items = self.db.get_items(
            skip=page * ITEMS_PER_PAGE,
            limit=ITEMS_PER_PAGE
        )

        # Send each item
        for item in items:
            caption = format_item_caption(item)
            photo_key = item.get('photo_key')

            if photo_key:
                try:
                    s3_response = self.storage.get_file(photo_key)
                    image_data = s3_response['Body'].read()
                    image_stream = io.BytesIO(image_data)
                    image_stream.seek(0)

                    await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=image_stream,
                        caption=caption,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    self.logger.error(f"Error sending photo: {e}")
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=caption,
                        parse_mode='Markdown'
                    )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=caption,
                    parse_mode='Markdown'
                )

        # Prepare navigation buttons
        keyboard = []
        buttons = []
        if page > 0:
            buttons.append(
                InlineKeyboardButton("⬅️ Previous", callback_data=f'list_{page - 1}')
            )
        if page < total_pages - 1:
            buttons.append(
                InlineKeyboardButton("Next ➡️", callback_data=f'list_{page + 1}')
            )
        if buttons:
            keyboard.append(buttons)

        # Send navigation message
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Page {page + 1} of {total_pages}",
            reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None
        )