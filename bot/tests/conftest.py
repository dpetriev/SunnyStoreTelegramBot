import pytest
from unittest.mock import AsyncMock, MagicMock, create_autospec
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes
from bot.services.database import DatabaseService
from bot.services.storage import StorageService

@pytest.fixture
def mock_db():
    """Create a properly configured mock database service."""
    db = create_autospec(DatabaseService)
    db.get_next_code.return_value = "000001"
    db.clothes = MagicMock()
    db.clothes.count_documents.return_value = 0
    return db

@pytest.fixture
def mock_storage():
    """Create a properly configured mock storage service."""
    storage = create_autospec(StorageService)
    storage.upload_file = AsyncMock()
    storage.get_file = AsyncMock()
    storage.delete_file = AsyncMock()
    return storage

@pytest.fixture
def mock_update():
    """Create a properly configured mock update."""
    update = create_autospec(Update)
    message = create_autospec(Message)
    chat = create_autospec(Chat)
    user = create_autospec(User)
    
    # Configure message
    message.message_id = 123
    message.chat = chat
    message.from_user = user
    message.reply_text = AsyncMock()
    message.text = "Test message"
    
    # Configure chat
    chat.id = 456
    chat.type = "private"
    
    # Configure user
    user.id = 789
    user.is_bot = False
    user.first_name = "Test"
    
    update.message = message
    update.effective_chat = chat
    update.effective_user = user
    
    return update

@pytest.fixture
def mock_context():
    """Create a properly configured mock context."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    context.bot.send_photo = AsyncMock()
    return context