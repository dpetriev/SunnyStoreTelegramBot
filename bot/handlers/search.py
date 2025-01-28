import io
from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.base import BaseHandler
from bot.utils.formatters import format_item_caption

class SearchHandler(BaseHandler):
    """Handler for searching items."""

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /search command."""
        if not context.args:
            await update.message.reply_text(
                "Please provide a search term after /search command.\n"
                "Example: /search blue shirt"
            )
            return

        search_term = ' '.join(context.args).lower()
        items = self.db.search_items(search_term)

        if not items:
            await update.message.reply_text(
                f"No items found matching '{search_term}'."
            )
            return

        # Send results
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
                        chat_id=update.effective_chat.id,
                        photo=image_stream,
                        caption=caption,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    self.logger.error(f"Error sending photo: {e}")
                    await update.message.reply_text(
                        caption,
                        parse_mode='Markdown'
                    )
            else:
                await update.message.reply_text(
                    caption,
                    parse_mode='Markdown'
                )