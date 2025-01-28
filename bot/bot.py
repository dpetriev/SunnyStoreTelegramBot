import logging
from telegram import BotCommand, MenuButtonCommands, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

from bot.config import BOT_TOKEN, BOT_COMMANDS
from bot.handlers.base import BaseHandler
from bot.handlers.add_item import AddItemHandler
from bot.handlers.change_item import ChangeItemHandler
from bot.handlers.delete_item import DeleteItemHandler
from bot.handlers.list_items import ListItemsHandler
from bot.handlers.search import SearchHandler
from bot.handlers.stats import StatsHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def create_application():
    """Create and configure the application."""
    # Create application with proper token and settings
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .pool_timeout(30)
        .build()
    )

    # Add error handler
    application.add_error_handler(error_handler)

    # Create handlers
    add_handler = AddItemHandler()
    change_handler = ChangeItemHandler()
    delete_handler = DeleteItemHandler()
    list_handler = ListItemsHandler()
    search_handler = SearchHandler()
    stats_handler = StatsHandler()

    # Add handlers in order of priority (group 0)
    application.add_handler(CommandHandler('start', start))
    
    # Add conversation handlers (group 0)
    application.add_handler(add_handler.get_handler())
    application.add_handler(change_handler.get_handler())
    application.add_handler(delete_handler.get_handler())
    
    # Add simple command handlers (group 0)
    application.add_handler(CommandHandler('list', list_handler.handle_command))
    application.add_handler(CallbackQueryHandler(list_handler.list_items, pattern='^list_'))
    application.add_handler(CommandHandler('search', search_handler.handle_command))
    application.add_handler(CommandHandler('stats', stats_handler.handle_command))
    
    # Add global cancel command (group 1)
    application.add_handler(
        CommandHandler('cancel', add_handler.cancel),
        group=1
    )
    
    # Add fallback handler for unknown commands (group 2)
    application.add_handler(
        MessageHandler(
            filters.COMMAND & ~filters.Regex('^/(start|add|change|delete|list|search|stats|cancel)$'),
            unknown_command
        ),
        group=2
    )

    # Set bot commands
    commands = [BotCommand(command, description) for command, description in BOT_COMMANDS]
    await application.bot.set_my_commands(commands)

    # Set the Menu Button to display commands
    await application.bot.set_chat_menu_button(menu_button=MenuButtonCommands())

    return application

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    commands_text = "\n".join(
        f"/{command} - {description}"
        for command, description in BOT_COMMANDS
    )
    await update.message.reply_text(
        f"Welcome to the Sunny Store Shop management Bot!\n\n"
        f"Available commands:\n{commands_text}"
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}", exc_info=context.error)
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "Sorry, an error occurred while processing your request."
        )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unknown commands."""
    await update.message.reply_text(
        "Sorry, I don't know that command. Use /start to see available commands."
    )

async def run_polling():
    """Run the bot in polling mode (for development)."""
    application = await create_application()
    await application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True
    )