from enum import Enum, auto

class State(Enum):
    # Add Item States
    ADD_NAME = auto()
    ADD_WHOLESALE_PRICE = auto()
    ADD_SELLING_PRICE = auto()
    ADD_DESCRIPTION = auto()
    ADD_PHOTO = auto()
    ADD_PARAMS = auto()
    ADD_COLOR = auto()
    ADD_COLOR_CODE_CHOICE = auto()  # Choose between auto or manual code for color
    ADD_COLOR_CODE_MANUAL = auto()  # Enter color code manually
    ADD_COLOR_PHOTO = auto()
    ADD_STOCK_SIZE = auto()
    ADD_STOCK_SIZE_RESPONSE = auto()
    ADD_STOCK_SIZE_RESPONSE_OTHER = auto()
    ADD_STOCK_QUANTITY = auto()
    ADD_MORE_STOCK = auto()

    # Change Item States
    CHANGE_CHOICE = auto()
    CHANGE_FIELD = auto()
    CHANGE_UPDATE = auto()

    # Delete Item States
    DELETE_CONFIRM = auto()
    DELETE_CONFIRMATION = auto()

# Convert enum to dict for easier access
STATES = {state.name: state.value for state in State}