import os
from dotenv import load_dotenv

load_dotenv()

def get_required_env(name: str, default=None) -> str:
    value = os.getenv(name)
    if not value and default is None:
        raise ValueError(f"Missing required environment variable: {name}")
    return value or default

# Bot Configuration
BOT_TOKEN = get_required_env('TELEGRAM_BOT_TOKEN_TEST')
ITEMS_PER_PAGE = int(get_required_env('ITEMS_PER_PAGE', '5'))

# MongoDB Configuration
MONGODB_CONNECTION_STRING = get_required_env('MONGODB_CONN_STRING')
DB_NAME = get_required_env('DB_NAME', 'clothing_store')
CLOTHES_COLLECTION = get_required_env('CLOTHES_COLLECTION', 'clothes')
COUNTERS_COLLECTION = get_required_env('COUNTERS_COLLECTION', 'counters')
MONGODB_TIMEOUT_MS = int(get_required_env('MONGODB_TIMEOUT_MS', '5000'))
MONGODB_MAX_RETRIES = int(get_required_env('MONGODB_MAX_RETRIES', '3'))

# AWS Configuration
AWS_ACCESS_KEY = get_required_env('AWS_ACCESS_KEY')
AWS_SECRET_KEY = get_required_env('AWS_SECRET_KEY')
AWS_REGION = get_required_env('AWS_REGION')
S3_BUCKET_NAME = get_required_env('S3_BUCKET_NAME')
AWS_TIMEOUT = int(get_required_env('AWS_TIMEOUT', '30'))
AWS_MAX_RETRIES = int(get_required_env('AWS_MAX_RETRIES', '3'))

# Bot Commands
BOT_COMMANDS = [
    ('start', 'Start the bot and get help'),
    ('add', 'Add a new item'),
    ('change', 'Change an existing item'),
    ('delete', 'Delete an item'),
    ('list', 'List all items'),
    ('search', 'Search for items'),
    ('stats', 'Show store statistics'),
    ('cancel', 'Cancel the current operation'),
]

# Constants
SIZE_OPTIONS = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'Other']