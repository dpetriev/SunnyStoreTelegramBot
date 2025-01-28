from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.base import BaseHandler
from bot.utils.formatters import format_statistics

class StatsHandler(BaseHandler):
    """Handler for showing statistics."""

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /stats command."""
        stats = self.db.get_statistics()
        message = format_statistics(stats)
        
        await update.message.reply_text(
            message,
            parse_mode='Markdown'
        )