import logging
import signal
from typing import Callable
from bot.services.database import DatabaseService
from bot.services.storage import StorageService

logger = logging.getLogger(__name__)

def cleanup_services():
    """Cleanup all services."""
    try:
        # Close MongoDB connection
        db = DatabaseService()
        db.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

def setup_signal_handlers(stop_callback: Callable):
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        sig_name = signal.Signals(signum).name
        logger.info(f"Received {sig_name} signal")
        cleanup_services()
        if stop_callback:
            stop_callback()

    # Handle SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)