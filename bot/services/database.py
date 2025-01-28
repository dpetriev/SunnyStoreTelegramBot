import logging
from functools import wraps
from typing import Any, Callable
from pymongo import MongoClient, errors
from pymongo.collection import ReturnDocument
from bot.config import (
    MONGODB_CONNECTION_STRING,
    DB_NAME,
    CLOTHES_COLLECTION,
    COUNTERS_COLLECTION,
    MONGODB_TIMEOUT_MS,
    MONGODB_MAX_RETRIES
)

logger = logging.getLogger(__name__)

def with_retry(max_retries: int = MONGODB_MAX_RETRIES) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except errors.PyMongoError as e:
                    last_error = e
                    logger.warning(f"MongoDB operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        continue
            raise last_error
        return wrapper
    return decorator

class DatabaseService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self.client = MongoClient(
                MONGODB_CONNECTION_STRING,
                serverSelectionTimeoutMS=MONGODB_TIMEOUT_MS,
                connectTimeoutMS=MONGODB_TIMEOUT_MS,
                socketTimeoutMS=MONGODB_TIMEOUT_MS
            )
            self.db = self.client[DB_NAME]
            self.clothes = self.db[CLOTHES_COLLECTION]
            self.counters = self.db[COUNTERS_COLLECTION]
            
            # Test connection
            self.client.admin.command('ping')
            
            # Initialize the counter if it doesn't exist
            if self.counters.count_documents({'_id': 'itemid'}) == 0:
                self.counters.insert_one({'_id': 'itemid', 'sequence_value': 0})
                
            logger.info("Successfully connected to MongoDB")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB connection: {e}")
            raise

    @with_retry()
    def get_next_code(self):
        result = self.counters.find_one_and_update(
            {'_id': 'itemid'},
            {'$inc': {'sequence_value': 1}},
            return_document=ReturnDocument.AFTER,
            upsert=True
        )
        return f"{result['sequence_value']:06d}"

    @with_retry()
    def add_item(self, item_data):
        return self.clothes.insert_one(item_data)

    @with_retry()
    def get_item(self, code):
        return self.clothes.find_one({'code': code})

    @with_retry()
    def update_item(self, item_id, update_data):
        return self.clothes.update_one(
            {'_id': item_id},
            {'$set': update_data}
        )

    @with_retry()
    def delete_item(self, item_id):
        return self.clothes.delete_one({'_id': item_id})

    @with_retry()
    def get_items(self, skip=0, limit=None, sort_by='code'):
        try:
            cursor = self.clothes.find().sort(sort_by, 1)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Error fetching items: {e}")
            raise

    @with_retry()
    def search_items(self, query, limit=5):
        try:
            search_query = {
                '$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}},
                    {'code': {'$regex': query, '$options': 'i'}},
                    {'params.color': {'$regex': query, '$options': 'i'}}
                ]
            }
            return list(self.clothes.find(search_query).limit(limit))
        except Exception as e:
            logger.error(f"Error searching items: {e}")
            raise

    @with_retry()
    def get_statistics(self):
        try:
            total_items = self.clothes.count_documents({})
            items_with_photos = self.clothes.count_documents(
                {"photo_key": {"$exists": True, "$ne": None}}
            )

            # Get total stock
            pipeline = [
                {"$unwind": "$params"},
                {"$unwind": "$params.stock"},
                {"$group": {
                    "_id": None,
                    "total_stock": {"$sum": "$params.stock.quantity"}
                }}
            ]
            stock_result = list(self.clothes.aggregate(pipeline))
            total_stock = stock_result[0]["total_stock"] if stock_result else 0

            # Get items by color
            pipeline = [
                {"$unwind": "$params"},
                {"$group": {
                    "_id": "$params.color",
                    "count": {"$sum": 1}
                }}
            ]
            colors = list(self.clothes.aggregate(pipeline))

            return {
                'total_items': total_items,
                'items_with_photos': items_with_photos,
                'total_stock': total_stock,
                'colors': colors
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            raise

    def close(self):
        self.client.close()