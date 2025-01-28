import pytest
from bot.services.database import DatabaseService

@pytest.fixture
def db_service():
    service = DatabaseService()
    yield service
    # Clean up test data after each test
    service.clothes.delete_many({})

def test_get_next_code(db_service):
    code1 = db_service.get_next_code()
    code2 = db_service.get_next_code()
    
    assert len(code1) == 6
    assert len(code2) == 6
    assert int(code2) == int(code1) + 1

def test_add_and_get_item(db_service):
    test_item = {
        'code': '000001',
        'name': 'Test Item',
        'description': 'Test Description',
        'wholesalePrice': 10.0,
        'sellingPrice': 20.0
    }
    
    # Add item
    result = db_service.add_item(test_item)
    assert result.inserted_id is not None
    
    # Get item
    item = db_service.get_item('000001')
    assert item is not None
    assert item['name'] == 'Test Item'
    assert item['description'] == 'Test Description'

def test_update_item(db_service):
    # First add an item
    test_item = {
        'code': '000001',
        'name': 'Test Item',
        'description': 'Test Description'
    }
    result = db_service.add_item(test_item)
    item_id = result.inserted_id
    
    # Update the item
    update_result = db_service.update_item(
        item_id,
        {'name': 'Updated Name'}
    )
    assert update_result.modified_count == 1
    
    # Verify the update
    updated_item = db_service.get_item('000001')
    assert updated_item['name'] == 'Updated Name'

def test_delete_item(db_service):
    # First add an item
    test_item = {
        'code': '000001',
        'name': 'Test Item'
    }
    result = db_service.add_item(test_item)
    item_id = result.inserted_id
    
    # Delete the item
    delete_result = db_service.delete_item(item_id)
    assert delete_result.deleted_count == 1
    
    # Verify the deletion
    item = db_service.get_item('000001')
    assert item is None