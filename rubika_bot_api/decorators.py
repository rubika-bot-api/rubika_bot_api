from typing import Callable, Dict, Any, Awaitable, TYPE_CHECKING
import functools
import inspect
# from . import logger

if TYPE_CHECKING:
    from .api import Robot

def on_message(func: Callable[..., Awaitable[Any]]):

    """Decorate a function to be called whenever a new message is received.

    The decorated function should take a keyword argument for each key in the
    `message_data` dictionary, plus an additional `bot` argument. The values of
    these arguments will be passed from the `message_data` dictionary. The
    function should return an awaitable.

    The `message_data` dictionary is constructed as follows:

    - If the `update` is a `NewMessage` update, `message_data` is a dictionary
      containing the `chat_id`, `message_id`, `text`, and `sender_id` of the
      new message.
    - If the `update` is an inline query update, `message_data` is a dictionary
      containing the `chat_id`, `message_id`, `text`, and `sender_id` of the
      inline query.

    If the update is not a `NewMessage` or inline query update, the decorated
    function is not called.

    Note that the decorated function must be a coroutine (defined using `async
    def`).
    """
    
    if not inspect.iscoroutinefunction(func):
        raise TypeError("The decorated function must be a coroutine (using async def).")

    @functools.wraps(func)
    async def wrapper(update: Dict[str, Any], bot: 'Robot'):
        # Use .get() for safer access to nested dictionaries
        update_data = update.get('update', {})
        message_data = None
        
        if update_data.get('type') == 'NewMessage':
            msg = update_data.get('new_message', {})
            message_data = {
                'chat_id': update_data.get('chat_id'),
                'message_id': msg.get('message_id'),
                'text': msg.get('text'),
                'sender_id': msg.get('sender_id')
            }
            
        elif 'inline_message' in update:
            msg = update.get('inline_message', {})
            message_data = {
                'chat_id': msg.get('chat_id'),
                'message_id': msg.get('message_id'),
                'text': msg.get('text'),
                'sender_id': msg.get('sender_id')
            }
            
        if message_data:
            # Await the call to the original async function
            return await func(bot=bot, **message_data)
            
    return wrapper