import pytest
from unittest.mock import AsyncMock, MagicMock, create_autospec
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes
from bot.handlers.add_item import AddItemHandler
from bot.handlers.list_items import ListItemsHandler
from bot.handlers.search import SearchHandler
from bot.handlers.stats import StatsHandler
from bot.handlers.delete_item import DeleteItemHandler
from bot.handlers.change_item import ChangeItemHandler
from bot.utils.states import STATES
from bot.services.database import DatabaseService

def create_mock_update():
    """Create a mock update with all required attributes."""
    update = create_autospec(Update)
    message = create_autospec(Message)
    chat = create_autospec(Chat)
    user = create_autospec(User)
    
    # Configure message
    message.message_id = 123
    message.chat = chat
    message.from_user = user
    message.reply_text = AsyncMock()
    
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

def create_mock_context():
    """Create a mock context with all required attributes."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    return context

@pytest.mark.asyncio
async def test_add_item_start():
    """Test starting add item conversation."""
    update = create_mock_update()
    context = create_mock_context()
    
    handler = AddItemHandler()
    result = await handler.start(update, context)

    assert update.message.reply_text.called
    assert result == STATES['ADD_NAME']
    assert 'new_item' in context.user_data

@pytest.mark.asyncio
async def test_add_item_name():
    """Test handling item name input."""
    update = create_mock_update()
    context = create_mock_context()
    context.user_data['new_item'] = {}
    update.message.text = "Test Item"

    handler = AddItemHandler()
    result = await handler.handle_name(update, context)

    assert update.message.reply_text.called
    assert result == STATES['ADD_WHOLESALE_PRICE']
    assert context.user_data['new_item']['name'] == "Test Item"

@pytest.mark.asyncio
async def test_list_items_empty():
    """Test listing items when database is empty."""
    update = create_mock_update()
    context = create_mock_context()
    
    # Create mock database
    mock_db = create_autospec(DatabaseService)
    mock_db.clothes = MagicMock()
    mock_db.clothes.count_documents.return_value = 0
    
    # Configure callback query
    update.callback_query = None

    handler = ListItemsHandler()
    handler.db = mock_db

    await handler.handle_command(update, context)

    assert update.message.reply_text.called
    update.message.reply_text.assert_called_once_with(
        "No items found in the database."
    )

@pytest.mark.asyncio
async def test_search_no_args():
    """Test search command without arguments."""
    update = create_mock_update()
    context = create_mock_context()
    context.args = []

    handler = SearchHandler()
    await handler.handle_command(update, context)

    assert update.message.reply_text.called
    update.message.reply_text.assert_called_once_with(
        "Please provide a search term after /search command.\\n"
        "Example: /search blue shirt"
    )

@pytest.mark.asyncio
async def test_stats():
    """Test statistics command."""
    update = create_mock_update()
    context = create_mock_context()
    
    # Create mock database
    mock_db = create_autospec(DatabaseService)
    mock_db.get_statistics.return_value = {
        'total_items': 10,
        'items_with_photos': 5,
        'total_stock': 100,
        'colors': [
            {'_id': 'blue', 'count': 3},
            {'_id': 'red', 'count': 2}
        ]
    }

    handler = StatsHandler()
    handler.db = mock_db

    await handler.handle_command(update, context)

    assert update.message.reply_text.called

@pytest.mark.asyncio
async def test_delete_item_invalid_code():
    """Test delete item with invalid code format."""
    update = create_mock_update()
    context = create_mock_context()
    update.message.text = "12345"  # Invalid 6-digit code

    handler = DeleteItemHandler()
    result = await handler.handle_confirm(update, context)

    assert update.message.reply_text.called
    assert result == STATES['DELETE_CONFIRM']

@pytest.mark.asyncio
async def test_change_item_not_found():
    """Test change item with non-existent code."""
    update = create_mock_update()
    context = create_mock_context()
    update.message.text = "000001"
    
    # Create mock database
    mock_db = create_autospec(DatabaseService)
    mock_db.get_item.return_value = None

    handler = ChangeItemHandler()
    handler.db = mock_db

    result = await handler.handle_choice(update, context)

    assert update.message.reply_text.called
    assert result == STATES['CHANGE_CHOICE']
