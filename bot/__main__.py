import os
import sys
import asyncio
import logging
import fcntl
from pathlib import Path
from dotenv import load_dotenv
from bot.bot import create_application
from telegram import Update
from bot.utils.health import check_health
from bot.utils.cleanup import setup_signal_handlers, cleanup_services

LOCK_FILE = "/tmp/telegram_bot.lock"

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot."""
    application = None
    try:
        # Validate environment
        if not os.getenv('TELEGRAM_BOT_TOKEN_TEST'):
            logger.error("TELEGRAM_BOT_TOKEN_TEST environment variable is not set")
            return 1

        # Check services health
        logger.info("Performing health check...")
        if not await check_health():
            logger.error("Health check failed. Exiting...")
            return 1

        # Create and configure the application
        application = await create_application()
        
        logger.info("Bot started successfully!")
        
        # Run the bot until it's stopped
        await application.initialize()
        await application.start()
        await application.updater.start_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
        
        # Keep the bot running
        stop_event = asyncio.Event()
        
        def signal_handler():
            stop_event.set()
            
        # Setup signal handlers
        setup_signal_handlers(signal_handler)
        
        # Wait for stop signal
        await stop_event.wait()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
        return 1
    finally:
        try:
            if application:
                if application.updater.running:
                    await application.updater.stop()
                if application.running:
                    await application.stop()
                await application.shutdown()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
        cleanup_services()

def run():
    """Run the bot."""
    lock_file = None
    try:
        # Try to acquire lock file
        lock_file = open(LOCK_FILE, 'w')
        try:
            fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            logger.error("Another instance is already running")
            sys.exit(1)
            
        # Create new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the main function
        exit_code = loop.run_until_complete(main())
        
        # Clean up
        loop.close()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        if lock_file:
            try:
                fcntl.lockf(lock_file, fcntl.LOCK_UN)
                lock_file.close()
                os.unlink(LOCK_FILE)
            except Exception as e:
                logger.error(f"Error cleaning up lock file: {e}")

if __name__ == '__main__':
    run()