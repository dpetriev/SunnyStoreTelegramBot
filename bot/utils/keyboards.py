from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import SIZE_OPTIONS

# Button texts
CANCEL_BUTTON = 'Cancel'
SKIP_BUTTON = 'Skip'
YES_BUTTON = 'Yes'
NO_BUTTON = 'No'

# Create buttons
cancel_button = InlineKeyboardButton(CANCEL_BUTTON, callback_data='cancel')
skip_button = InlineKeyboardButton(SKIP_BUTTON, callback_data='skip')
yes_button = InlineKeyboardButton(YES_BUTTON, callback_data='yes')
no_button = InlineKeyboardButton(NO_BUTTON, callback_data='no')

def get_cancel_keyboard():
    """Get keyboard with only cancel button."""
    return InlineKeyboardMarkup([[cancel_button]])

def get_skip_keyboard():
    """Get keyboard with cancel and skip buttons."""
    return InlineKeyboardMarkup([[cancel_button, skip_button]])

def get_yes_no_keyboard():
    """Get keyboard with yes and no buttons."""
    return InlineKeyboardMarkup([[yes_button, no_button]])

def get_size_keyboard():
    """Get keyboard with size options."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(size, callback_data=size) for size in SIZE_OPTIONS]
    ])

def get_field_keyboard(fields):
    """Get keyboard with field options and cancel button."""
    field_buttons = [InlineKeyboardButton(f.capitalize(), callback_data=f) for f in fields]
    return InlineKeyboardMarkup([field_buttons, [cancel_button]])