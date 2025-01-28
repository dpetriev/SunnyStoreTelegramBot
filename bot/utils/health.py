import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from bot.services.database import DatabaseService
from bot.services.storage import StorageService
from bot.config import MONGODB_TIMEOUT_MS, AWS_TIMEOUT

logger = logging.getLogger(__name__)

def check_mongodb():
    """Check MongoDB connection."""
    try:
        db = DatabaseService()
        db.client.admin.command('ping')
        logger.info("MongoDB connection: OK")
        return True
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return False

def check_s3():
    """Check S3 connection."""
    try:
        storage = StorageService()
        storage.s3.list_buckets()
        logger.info("S3 connection: OK")
        return True
    except Exception as e:
        logger.error(f"S3 health check failed: {e}")
        return False

async def check_health():
    """Check the health of all services asynchronously."""
    try:
        # Create a thread pool for running blocking operations
        with ThreadPoolExecutor() as executor:
            # Run health checks concurrently
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, check_mongodb),
                loop.run_in_executor(executor, check_s3)
            ]

            # Wait for all checks with timeout
            timeout = max(MONGODB_TIMEOUT_MS / 1000, AWS_TIMEOUT)
            results = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)

            # All services must be healthy
            all_healthy = all(results)
            if all_healthy:
                logger.info("All services are healthy")
            else:
                logger.error("One or more services are unhealthy")
            return all_healthy

    except asyncio.TimeoutError:
        logger.error("Health check timed out")
        return False
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return False