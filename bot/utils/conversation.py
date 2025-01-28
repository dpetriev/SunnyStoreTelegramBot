from telegram.ext import ConversationHandler

def create_conversation_handler(
    entry_points,
    states,
    fallbacks,
    name=None,
    persistent=False,
    allow_reentry=False,
    conversation_timeout=None
):
    """Create a conversation handler with consistent settings."""
    return ConversationHandler(
        entry_points=entry_points,
        states=states,
        fallbacks=fallbacks,
        name=name,
        persistent=persistent,
        allow_reentry=allow_reentry,
        conversation_timeout=conversation_timeout,
        per_chat=True,
        per_user=True,
        per_message=False  # Set to False to avoid message tracking issues
    )