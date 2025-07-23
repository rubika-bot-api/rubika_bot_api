import aiohttp
import asyncio
import inspect
import time
from typing import List, Optional, Dict, Any, Literal, Callable, Awaitable
import aiofiles

from .exceptions import APIRequestError
from .logger import logger
from .context import Message, InlineMessage

API_URL = "https://botapi.rubika.ir/v3"

class Robot:
    def __init__(self, token: str):
        """
        Initialize the bot with a token.

        Parameters
        ----------
        token : str
            The bot token obtained from Rubika Bot Developer panel.

        Attributes
        ----------
        token : str
            The bot token.
        session : Optional[aiohttp.ClientSession]
            The aiohttp session used for making requests to the API.
        _offset_id : Optional[int]
            The last offset ID received from the API.
        _message_handler : Optional[Dict[str, Any]]
            The message handler function. See `on_message` decorator.
        _edited_message_handler : Optional[Dict[str, Any]]
            The edited message handler function. See `on_edited_message` decorator.
        _inline_query_handler : Optional[Callable[[Any, InlineMessage], Awaitable[None]]]
            The inline query handler function. See `on_inline_query` decorator.
        _started_bot_handler : Optional[Callable[[Any, Any], Awaitable[None]]]
            The started bot handler function. See `on_started_bot` decorator.
        _stopped_bot_handler : Optional[Callable[[Any, Any], Awaitable[None]]]
            The stopped bot handler function. See `on_stopped_bot` decorator.
        _on_callback_handler : Dict[str, Callable]
            The on_callback handlers by button_id. See `on_callback` decorator.
        offset_file : str
            The file name to store the last offset ID.

        Notes
        -----
        The bot will start at the last offset ID stored in the offset file.
        If the offset file does not exist, the bot will start from the beginning.
        """
        self.token = token
        self._offset_id = None
        self.session: Optional[aiohttp.ClientSession] = None
        self._message_handler: Optional[Dict[str, Any]] = None 
        self._edited_message_handler: Optional[Dict[str, Any]] = None
        self._inline_query_handler: Optional[Callable[[Any, InlineMessage], Awaitable[None]]] = None 
        self._started_bot_handler: Optional[Callable[[Any, Any], Awaitable[None]]] = None 
        self._stopped_bot_handler: Optional[Callable[[Any, Any], Awaitable[None]]] = None 
        self._on_callback_handler: Dict[str, Callable] = {} 
        self.offset_file = f"offset_{self.token[:10]}.txt"

        logger.info(
            f"Starting ON offset: {self._read_offset()}"
        )

    def _read_offset(self) -> Optional[str]:
        try:
            with open(self.offset_file, "r") as f:
                return f.read().strip()
        except FileNotFoundError: return None

    def _save_offset(self, offset_id: str):
        with open(self.offset_file, "w") as f:
            f.write(str(offset_id))

    def _post_sync(self, method: str, data: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        import requests 
        url = f"{API_URL}/{self.token}/{method}"
        try:
            response = requests.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise APIRequestError(f"API request failed: {e}") from e

    async def _post(self, method: str, data: Dict[str, Any], timeout: int = 20) -> Dict[str, Any]:
        if not self.session:
            raise RuntimeError("The bot session is not running. Please use 'await bot.run()'.")
        
        url = f"{API_URL}/{self.token}/{method}"
        try:
            async with self.session.post(url, json=data, timeout=timeout) as response:
                response.raise_for_status()
                try:
                    json_resp = await response.json()
                except aiohttp.ContentTypeError:
                    response_text = await response.text()
                    logger.error(f"Invalid JSON response from {method}: {response_text}")
                    raise APIRequestError(f"Invalid JSON response: {response_text}")

                if method != "getUpdates":
                    logger.debug(f"API Response from {method}: {json_resp}")
                return json_resp

        except asyncio.TimeoutError:
            logger.error(f"Request to {method} timed out after {timeout} seconds.")
            raise APIRequestError(f"Request timed out: {method}")
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {e}")
            raise APIRequestError(f"API request failed: {e}") from e

    def on_message(self, filters: Optional[Callable[[Message], bool]] = None, commands: Optional[List[str]] = None):
        def decorator(func: Callable[[Any, Message], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The message handler function must be a coroutine (using async def).")
            self._message_handler = {
                "func": func,
                "filters": filters,
                "commands": commands
            }
            return func
        return decorator

    def on_edited_message(self, filters: Optional[Callable[[Message], bool]] = None):
        def decorator(func: Callable[[Any, Message], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The edited message handler function must be a coroutine (using async def).")
            self._edited_message_handler = {
                "func": func,
                "filters": filters
            }
            return func
        return decorator

    def on_inline_query(self): 
        def decorator(func: Callable[[Any, InlineMessage], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The inline query handler function must be a coroutine (using async def).")
            self._inline_query_handler = func
            return func
        return decorator

    def on_started_bot(self): 
        def decorator(func: Callable[[Any, Any], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The bot started handler function must be a coroutine (using async def).")
            self._started_bot_handler = func
            return func
        return decorator

    def on_stopped_bot(self):
        """
        Decorator to register a function that will be called when the bot is stopped.
    
        The decorated function must be an asynchronous function (defined using `async def`).
        It should accept two positional arguments, which will be provided by the event
        that triggers the stop handler.
    
        Raises:
            TypeError: If the decorated function is not a coroutine.
        """
    
        def decorator(func: Callable[[Any, Any], Awaitable[None]]):
            if not inspect.iscoroutinefunction(func):
                raise TypeError("The bot stopped handler function must be a coroutine (using async def).")
            self._stopped_bot_handler = func
            return func
        return decorator

    # New: Decorator for on_callback (similar to rubka)
    def on_callback(self, button_id: str) -> Callable:
        """Decorator to register a function that will be called when a button with the specified ID is clicked.

        The decorated function must be an asynchronous function (defined using `async def`).
        It should accept one positional argument, a `Message` object, which will be the message context of the button click event.

        Args:
            button_id: The unique ID of the button to be handled. This ID should match the value passed to `button_id` when creating the button.

        Raises:
            TypeError: If the decorated function is not a coroutine.
        """

        def decorator(func: Callable[[Any, Message], Awaitable[None]]): # Changed to Message context for uniformity
            if not inspect.iscoroutinefunction(func):
                raise TypeError("Callback handler must be a coroutine (using async def).")
            self._on_callback_handler[button_id] = func
            return func
        return decorator

    async def _process_update(self, update: Dict[str, Any]):
        event_type = update.get('type')
        
        if event_type == 'NewMessage':
            # Check for specific button callbacks first (on_callback decorator)
            msg = update.get("new_message", {})
            if msg.get('aux_data') and msg['aux_data'].get('button_id'):
                button_id = msg['aux_data']['button_id']
                if button_id in self._on_callback_handler:
                    context = Message(bot=self, chat_id=update.get('object_guid') or update.get('chat_id'),
                                      message_id=msg.get('message_id'), sender_id=msg.get('sender_id'),
                                      text=msg.get('text'), raw_data=msg)
                    await self._on_callback_handler[button_id](self, context)
                    return # Handle callback, don't pass to general message handler

            # If not a callback, proceed to general message handler
            if self._message_handler:
                chat_id = update.get('object_guid') or update.get('chat_id')
                if not chat_id: return
                context = Message(bot=self, chat_id=chat_id, message_id=msg.get('message_id'), 
                                  sender_id=msg.get('sender_id'), text=msg.get('text'), raw_data=msg)
                
                handler_info = self._message_handler
                if handler_info.get("filters") and not handler_info["filters"](context): return
                if handler_info.get("commands"):
                    if not context.text or not context.text.startswith("/"): return
                    parts = context.text.split()
                    cmd = parts[0][1:]
                    if cmd not in handler_info["commands"]: return
                    context.args = parts[1:]
                await handler_info["func"](self, context)
        
        elif event_type == 'UpdatedMessage':
            if self._edited_message_handler:
                msg = update.get("updated_message", {})
                chat_id = update.get('object_guid') or update.get('chat_id')
                if not chat_id: return

                context = Message(
                    bot=self,
                    chat_id=chat_id,
                    message_id=msg.get('message_id'),
                    sender_id=msg.get('sender_id'),
                    text=msg.get('text'),
                    raw_data=msg
                )
                await self._edited_message_handler["func"](self, context)
        elif event_type == 'ReceiveQuery': 
             if self._inline_query_handler:
                msg = update.get("inline_message", {})
                context = InlineMessage(bot=self, raw_data=msg)
                await self._inline_query_handler(self, context)
                return
        elif event_type == 'StartedBot' and self._started_bot_handler:
            chat_id = update.get('chat_id') 
            await self._started_bot_handler(self, chat_id)
        elif event_type == 'StoppedBot' and self._stopped_bot_handler:
            chat_id = update.get('chat_id')
            await self._stopped_bot_handler(self, chat_id)
        elif event_type == 'RemovedMessage':
            removed_id = update.get('removed_message_id')
            logger.info(f"Message {removed_id} was removed in a chat.")
        else:
            logger.debug(f"Received an unhandled event type: {event_type}")

    async def run(self):
        """
        Continuously fetch and process updates for the bot.

        This asynchronous method starts the bot's main loop, which continuously
        polls for new updates (messages, events, etc.) from the server. It manages
        the session life cycle with `aiohttp.ClientSession` and processes each update
        using the `_process_update` method. The method handles exceptions gracefully
        by logging errors and retrying after a short delay.

        Attributes
        ----------
        _offset_id : int
            The current offset ID to keep track of processed updates.
        session : aiohttp.ClientSession
            The HTTP session used for making requests to the API.

        Notes
        -----
        The loop polls the server every 0.5 seconds for updates and adjusts the
        offset ID based on the responses to ensure continuity in message processing.
        Errors in the update loop are logged, and the loop pauses for 5 seconds
        before retrying in case of an error.
        """

        print("🟢 BOT IS WAKING UP ✅")
        self._offset_id = self._read_offset()
        async with aiohttp.ClientSession() as session:
            self.session = session
            print("OFSET UPDATED . LISENNING FOR NEW MESSAGES ♻")

            while True:
                try:
                    updates_response = await self.get_updates(offset_id=self._offset_id, limit=50)
                    if updates_response and updates_response.get('data'):
                        update_list = updates_response['data'].get('updates', [])
                        
                        for update in update_list:
                            asyncio.create_task(self._process_update(update))

                        next_offset = updates_response['data'].get('next_offset_id')
                        if next_offset:
                            self._offset_id = next_offset
                            self._save_offset(next_offset)
                    
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.error(f"An unexpected error occurred in run loop: {e}")
                    await asyncio.sleep(5)
    
    def send_message_sync(
        self,
        chat_id: str,
        text: str,
        chat_keypad: Optional[Dict[str, Any]] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: Optional[Literal["New", "Removed"]] = None
    ) -> Dict[str, Any]:
        import requests 
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_notification": disable_notification
        }
        if chat_keypad: payload["chat_keypad"] = chat_keypad
        if inline_keypad: payload["inline_keypad"] = inline_keypad
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type: payload["chat_keypad_type"] = chat_keypad_type
        return self._post_sync("sendMessage", payload)

    async def send_message(
        self,
        chat_id: str,
        text: str,
        chat_keypad: Optional[Dict[str, Any]] = None,
        inline_keypad: Optional[Dict[str, Any]] = None,
        disable_notification: bool = False,
        reply_to_message_id: Optional[str] = None,
        chat_keypad_type: Optional[Any] = None, 
        auto_delete: Optional[float] = None
    ) -> Dict[str, Any]:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_notification": disable_notification
        }
        if chat_keypad: payload["chat_keypad"] = chat_keypad
        if inline_keypad: payload["inline_keypad"] = inline_keypad
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        if chat_keypad_type: payload["chat_keypad_type"] = chat_keypad_type.value if hasattr(chat_keypad_type, 'value') else chat_keypad_type

        result = await self._post("sendMessage", payload)
        
        if auto_delete and result and result.get('data', {}).get('message_update', {}).get('message_id'):
            sent_message_id = result['data']['message_update']['message_id']
            asyncio.create_task(
                self.auto_delete_message(
                    chat_id=chat_id,
                    message_id=sent_message_id,
                    delay=auto_delete
                )
            )
        return result

    async def auto_delete_message(self, chat_id: str, message_id: str, delay: float):
        await asyncio.sleep(delay)
        try:
            await self.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            logger.warning(f"Could not auto-delete message {message_id}: {e}")

    def send_poll_sync(self, chat_id: str, question: str, options: List[str]) -> Dict[str, Any]:
        import requests
        return self._post_sync("sendPoll", {"chat_id": chat_id, "question": question, "options": options})
    
    async def send_poll(self, chat_id: str, question: str, options: List[str]) -> Dict[str, Any]:
        return await self._post("sendPoll", {"chat_id": chat_id, "question": question, "options": options})

    def send_location_sync(self, chat_id: str, latitude: str, longitude: str, disable_notification: bool = False, inline_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, chat_keypad_type: Optional[Literal["New", "Removed"]] = None) -> Dict[str, Any]:
        import requests
        payload = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude, "disable_notification": disable_notification, "inline_keypad": inline_keypad, "reply_to_message_id": reply_to_message_id, "chat_keypad_type": chat_keypad_type}
        payload = {k: v for k, v in payload.items() if v is not None}
        return self._post_sync("sendLocation", payload)
    
    async def send_location(self, chat_id: str, latitude: str, longitude: str, disable_notification: bool = False, inline_keypad: Optional[Dict[str, Any]] = None, reply_to_message_id: Optional[str] = None, chat_keypad_type: Optional[Literal["New", "Removed"]] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "latitude": latitude, "longitude": longitude, "disable_notification": disable_notification, "inline_keypad": inline_keypad, "reply_to_message_id": reply_to_message_id, "chat_keypad_type": chat_keypad_type}
        payload = {k: v for k, v in payload.items() if v is not None}
        return await self._post("sendLocation", payload)

    def send_contact_sync(self, chat_id: str, first_name: str, last_name: str, phone_number: str) -> Dict[str, Any]:
        import requests
        return self._post_sync("sendContact", {"chat_id": chat_id, "first_name": first_name, "last_name": last_name, "phone_number": phone_number})

    async def send_contact(self, chat_id: str, first_name: str, last_name: str, phone_number: str, chat_keypad: Optional[Dict[str, Any]] = None, inline_keypad: Optional[Dict[str, Any]] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "first_name": first_name, "last_name": last_name, "phone_number": phone_number, "disable_notification": disable_notification}
        if chat_keypad: payload["chat_keypad"] = chat_keypad
        if inline_keypad: payload["inline_keypad"] = inline_keypad
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return await self._post("sendContact", payload)

    def get_chat_sync(self, chat_id: str) -> Dict[str, Any]:
        import requests
        return self._post_sync("getChat", {"chat_id": chat_id})
        
    async def get_chat(self, chat_id: str) -> Dict[str, Any]:
        return await self._post("getChat", {"chat_id": chat_id})

    # New method: get_name (based on rubka)
    async def get_name(self, user_id: str) -> Optional[str]:
        """Gets the first name of a user from their user_id."""
        chat_info_response = await self.get_chat(user_id)
        return chat_info_response.get("data", {}).get("first_name")

    # New method: get_username (based on rubka)
    async def get_username(self, user_id: str) -> Optional[str]:
        """Gets the username of a user from their user_id."""
        chat_info_response = await self.get_chat(user_id)
        return chat_info_response.get("data", {}).get("username")

    # New method: check_join (placeholder for rubka)
    async def check_join(self, chat_id: str, user_id: str) -> bool:
        """
        PLACEHOLDER: Checks if a user is a member of a channel/group.
        Rubika API docs do not provide a direct method for this.
        """
        logger.warning(f"check_join called for chat_id: {chat_id}, user_id: {user_id}. This method is a placeholder and always returns False.")
        return False

    # New method: get_all_member (placeholder for rubka)
    async def get_all_member(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        PLACEHOLDER: Gets a list of all members in a group/channel.
        Rubika API docs do not provide a direct method for this.
        """
        logger.warning(f"get_all_member called for chat_id: {chat_id}. This method is a placeholder and always returns an empty list.")
        return []

    def get_updates_sync(self, offset_id: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        import requests
        data = {}
        if offset_id: data["offset_id"] = offset_id
        if limit: data["limit"] = limit
        return self._post_sync("getUpdates", data)
    
    async def get_updates(self, offset_id: Optional[str] = None, limit: Optional[int] = None, timeout: int = 20) -> Dict[str, Any]:
        data = {}
        if offset_id: data["offset_id"] = offset_id
        if limit: data["limit"] = limit
        return await self._post("getUpdates", data, timeout=timeout)

    def forward_message_sync(self, from_chat_id: str, message_id: str, to_chat_id: str, disable_notification: bool = False) -> Dict[str, Any]:
        import requests
        return self._post_sync("forwardMessage", {"from_chat_id": from_chat_id, "message_id": message_id, "to_chat_id": to_chat_id, "disable_notification": disable_notification})

    async def forward_message(self, from_chat_id: str, message_id: str, to_chat_id: str, disable_notification: bool = False) -> Dict[str, Any]:
        return await self._post("forwardMessage", {"from_chat_id": from_chat_id, "message_id": message_id, "to_chat_id": to_chat_id, "disable_notification": disable_notification})

    def edit_message_text_sync(self, chat_id: str, message_id: str, text: str) -> Dict[str, Any]:
        import requests
        return self._post_sync("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    async def edit_message_text(self, chat_id: str, message_id: str, text: str) -> Dict[str, Any]:
        return await self._post("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text})

    def edit_inline_keypad_sync(self, chat_id: str, message_id: str, inline_keypad: Dict[str, Any]) -> Dict[str, Any]:
        import requests
        return self._post_sync("editInlineKeypad", {"chat_id": chat_id, "message_id": message_id, "inline_keypad": inline_keypad})

    async def edit_inline_keypad(self,chat_id: str,message_id: str,inline_keypad: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("editMessageKeypad", {"chat_id": chat_id,"message_id": message_id, "inline_keypad": inline_keypad})

    def delete_message_sync(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        import requests
        return self._post_sync("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    async def delete_message(self, chat_id: str, message_id: str) -> Dict[str, Any]:
        return await self._post("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

    def set_commands_sync(self, bot_commands: List[Dict[str, str]]) -> Dict[str, Any]:
        import requests
        return self._post_sync("setCommands", {"bot_commands": bot_commands})

    async def set_commands(self, bot_commands: List[Dict[str, str]]) -> Dict[str, Any]:
        return await self._post("setCommands", {"bot_commands": bot_commands})

    def update_bot_endpoint_sync(self, url: str, type: str) -> Dict[str, Any]:
        import requests
        return self._post_sync("updateBotEndpoints", {"url": url, "type": type})

    async def update_bot_endpoint(self, url: str, type: str) -> Dict[str, Any]:
        return await self._post("updateBotEndpoints", {"url": url, "type": type})

    def remove_keypad_sync(self, chat_id: str) -> Dict[str, Any]:
        import requests
        return self._post_sync("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "Removed"})

    async def remove_keypad(self, chat_id: str) -> Dict[str, Any]:
        return await self._post("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "Removed"})

    def edit_chat_keypad_sync(self, chat_id: str, chat_keypad: Dict[str, Any]) -> Dict[str, Any]:
        import requests
        return self._post_sync("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "New", "chat_keypad": chat_keypad})

    async def edit_chat_keypad(self, chat_id: str, chat_keypad: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("editChatKeypad", {"chat_id": chat_id, "chat_keypad_type": "New", "chat_keypad": chat_keypad})

    async def send_photo_sync(self, chat_id: str, photo: str, caption: Optional[str] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        import requests
        payload = {"chat_id": chat_id, "photo": photo, "disable_notification": disable_notification}
        if caption: payload["caption"] = caption
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return self._post_sync("sendPhoto", payload)

    async def send_photo(self, chat_id: str, photo: str, caption: Optional[str] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "photo": photo, "disable_notification": disable_notification}
        if caption: payload["caption"] = caption
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return await self._post("sendPhoto", payload)

    def send_video_sync(self, chat_id: str, video: str, caption: Optional[str] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        import requests
        payload = {"chat_id": chat_id, "video": video, "disable_notification": disable_notification}
        if caption: payload["caption"] = caption
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return self._post_sync("sendVideo", payload)

    async def send_video(self, chat_id: str, video: str, caption: Optional[str] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "video": video, "disable_notification": disable_notification}
        if caption: payload["caption"] = caption
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return await self._post("sendVideo", payload)

    def send_document_sync(self, chat_id: str, document: str, caption: Optional[str] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        import requests
        payload = {"chat_id": chat_id, "document": document, "disable_notification": disable_notification}
        if caption: payload["caption"] = caption
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return self._post_sync("sendDocument", payload)

    async def send_document(self, chat_id: str, document: str, caption: Optional[str] = None, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "document": document, "disable_notification": disable_notification}
        if caption: payload["caption"] = caption
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return await self._post("sendDocument", payload)

    def send_sticker_sync(self, chat_id: str, sticker_id: str, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        import requests
        payload = {"chat_id": chat_id, "sticker_id": sticker_id, "disable_notification": disable_notification}
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return self._post_sync("sendSticker", payload)

    async def send_sticker(self, chat_id: str, sticker_id: str, disable_notification: bool = False, reply_to_message_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "sticker_id": sticker_id, "disable_notification": disable_notification}
        if reply_to_message_id: payload["reply_to_message_id"] = reply_to_message_id
        return await self._post("sendSticker", payload)

    def send_file_sync(self, chat_id: str, file_id: str, **kwargs) -> Dict[str, Any]:
        import requests
        payload = {"chat_id": chat_id, "file_id": file_id, **kwargs}
        return self._post_sync("sendFile", payload)

    async def send_file(self, chat_id: str, file_id: str, **kwargs) -> Dict[str, Any]:
        payload = {"chat_id": chat_id, "file_id": file_id, **kwargs}
        return await self._post("sendFile", payload)

    async def _upload_file(self, file_bytes: bytes, file_name: str) -> str:
        # Note: 'requests' module is used here for its simplicity in synchronous parts
        # For a pure async _upload_file, you'd use aiohttp with multipart.
        import aiofiles # aiofiles for async file ops
        
        upload_url = "https://botapi.rubika.ir/v3/SOME_UPLOAD_ENDPOINT"
        form_data = aiohttp.FormData()
        form_data.add_field('file', file_bytes, filename=file_name, content_type='application/octet-stream')
        async with self.session.post(upload_url, data=form_data) as response:
            if response.status == 200:
                data = await response.json()
                return data['file_id']
            else:
                raise APIRequestError("File upload failed.")

    async def send_photo_from_path_sync(self, chat_id: str, path: str, caption: Optional[str] = None, **kwargs):
        import requests
        try:
            with open(path, 'rb') as f:
                photo_bytes = f.read()
            # This would typically involve a synchronous upload
            # For now, let's assume _upload_file_sync exists or handle directly.
            # As a placeholder, we will just use send_photo directly
            logger.warning("Synchronous file upload from path is not fully implemented. Consider using async version.")
            # Dummy call to illustrate. You would replace this with actual sync upload logic.
            return self._post_sync("sendPhoto", {"chat_id": chat_id, "photo": "dummy_file_id", "caption": caption, **kwargs})
        except FileNotFoundError:
            logger.error(f"File not found at path: {path}")
            raise APIRequestError(f"File not found at path: {e}")
        except Exception as e:
            logger.error(f"Failed to send photo from path synchronously: {e}")
            raise APIRequestError(f"Failed to send photo from path synchronously: {e}")

    async def send_photo_from_path(self, chat_id: str, path: str, caption: Optional[str] = None, **kwargs):
        try:
            # aiofiles imported at the top
            async with aiofiles.open(path, 'rb') as f:
                photo_bytes = await f.read()
            file_name = path.split('/')[-1]
            photo_file_id = await self._upload_file(photo_bytes, file_name)
            return await self.send_photo(chat_id=chat_id, photo=photo_file_id, caption=caption, **kwargs)
        except FileNotFoundError:
            logger.error(f"File not found at path: {path}")
        except Exception as e:
            logger.error(f"Failed to send photo from path: {e}")