from typing import Any, Dict, List, Optional, TYPE_CHECKING, Union
import enum

if TYPE_CHECKING:
    from .api import Robot

class File:
    def __init__(self, data: dict):
        self.file_id: str = data.get("file_id")
        self.file_name: str = data.get("file_name")
        self.size: str = data.get("size")

class Sticker:
    def __init__(self, data: dict):
        self.sticker_id: str = data.get("sticker_id")
        self.emoji_character: str = data.get("emoji_character")
        self.file = File(data.get("file", {}))

class PollStatus:
    def __init__(self, data: dict):
        self.state: str = data.get("state")
        self.selection_index: int = data.get("selection_index")
        self.percent_vote_options: List[int] = data.get("percent_vote_options", [])
        self.total_vote: int = data.get("total_vote")
        self.show_total_votes: bool = data.get("show_total_votes")

class Poll:
    def __init__(self, data: dict):
        self.question: str = data.get("question")
        self.options: List[str] = data.get("options", [])
        self.poll_status = PollStatus(data.get("poll_status", {}))

class Location:
    def __init__(self, data: dict):
        self.latitude: str = data.get("latitude")
        self.longitude: str = data.get("longitude")

class LiveLocation:
    def __init__(self, data: dict):
        self.start_time: str = data.get("start_time")
        self.live_period: int = data.get("live_period")
        self.current_location = Location(data.get("current_location", {}))
        self.user_id: str = data.get("user_id")
        self.status: str = data.get("status")
        self.last_update_time: str = data.get("last_update_time")

class ContactMessage:
    def __init__(self, data: dict):
        self.phone_number: str = data.get("phone_number")
        self.first_name: str = data.get("first_name")
        self.last_name: str = data.get("last_name")

class ForwardedFrom:
    def __init__(self, data: dict):
        self.type_from: str = data.get("type_from")
        self.message_id: str = data.get("message_id")
        self.from_chat_id: str = data.get("from_chat_id")
        self.from_sender_id: str = data.get("from_sender_id")

class AuxData:
    def __init__(self, data: dict):
        self.start_id: str = data.get("start_id")
        self.button_id: str = data.get("button_id")

class ButtonTextbox:
    def __init__(self, data: dict):
        self.type_line: str = data.get("type_line")
        self.type_keypad: str = data.get("type_keypad")
        self.place_holder: Optional[str] = data.get("place_holder")
        self.title: Optional[str] = data.get("title")
        self.default_value: Optional[str] = data.get("default_value")

class ButtonNumberPicker:
    def __init__(self, data: dict):
        self.min_value: str = data.get("min_value")
        self.max_value: str = data.get("max_value")
        self.default_value: Optional[str] = data.get("default_value")
        self.title: str = data.get("title")

class ButtonStringPicker:
    def __init__(self, data: dict):
        self.items: List[str] = data.get("items", [])
        self.default_value: Optional[str] = data.get("default_value")
        self.title: Optional[str] = data.get("title")

class ButtonCalendar:
    def __init__(self, data: dict):
        self.default_value: Optional[str] = data.get("default_value")
        self.type: str = data.get("type")
        self.min_year: str = data.get("min_year")
        self.max_year: str = data.get("max_year")
        self.title: str = data.get("title")

class ButtonLocation:
    def __init__(self, data: dict):
        self.default_pointer_location = Location(data.get("default_pointer_location", {}))
        self.default_map_location = Location(data.get("default_map_location", {}))
        self.type: str = data.get("type")
        self.title: Optional[str] = data.get("title")
        self.location_image_url: str = data.get("location_image_url")

class ButtonSelectionItem:
    def __init__(self, data: dict):
        self.text: str = data.get("text")
        self.image_url: str = data.get("image_url")
        self.type: str = data.get("type")

class ButtonSelection:
    def __init__(self, data: dict):
        self.selection_id: str = data.get("selection_id")
        self.search_type: str = data.get("search_type")
        self.get_type: str = data.get("get_type")
        self.items: List[ButtonSelectionItem] = [ButtonSelectionItem(i) for i in data.get("items", [])]
        self.is_multi_selection: bool = data.get("is_multi_selection")
        self.columns_count: str = data.get("columns_count")
        self.title: str = data.get("title")

class Button:
    def __init__(self, data: dict):
        self.id: str = data.get("id")
        self.type: str = data.get("type")
        self.button_text: str = data.get("button_text")
        self.button_selection = ButtonSelection(data.get("button_selection", {})) if "button_selection" in data else None
        self.button_calendar = ButtonCalendar(data.get("button_calendar", {})) if "button_calendar" in data else None
        self.button_number_picker = ButtonNumberPicker(data.get("button_number_picker", {})) if "button_number_picker" in data else None
        self.button_string_picker = ButtonStringPicker(data.get("button_string_picker", {})) if "button_string_picker" in data else None
        self.button_location = ButtonLocation(data.get("button_location", {})) if "button_location" in data else None
        self.button_textbox = ButtonTextbox(data.get("button_textbox", {})) if "button_textbox" in data else None

class KeypadRow:
    def __init__(self, data: dict):
        self.buttons: List[Button] = [Button(btn) for btn in data.get("buttons", [])]

class Keypad:
    def __init__(self, data: dict):
        self.rows: List[KeypadRow] = [KeypadRow(r) for r in data.get("rows", [])]
        self.resize_keyboard: bool = data.get("resize_keyboard", False)
        self.on_time_keyboard: bool = data.get("on_time_keyboard", False)

class Chat:
    def __init__(self, data: dict):
        self.chat_id: str = data.get("chat_id")
        self.chat_type: str = data.get("chat_type")
        self.user_id: str = data.get("user_id")
        self.first_name: str = data.get("first_name")
        self.last_name: str = data.get("last_name")
        self.title: str = data.get("title")
        self.username: str = data.get("username")

class Bot:
    def __init__(self, data: dict):
        self.bot_id: str = data.get("bot_id")
        self.bot_title: str = data.get("bot_title")
        self.avatar = File(data.get("avatar", {}))
        self.description: str = data.get("description")
        self.username: str = data.get("username")
        self.start_message: str = data.get("start_message")
        self.share_url: str = data.get("share_url")

class ChatKeypadType(enum.Enum):
    NEW = "New"
    REMOVED = "Removed"

class UpdateEndpointType(enum.Enum):
    RECEIVE_UPDATE = "ReceiveUpdate"
    RECEIVE_INLINE_MESSAGE = "ReceiveInlineMessage"
    GET_SELECTION_ITEM = "GetSelectionItem"

class BotCommand:
    def __init__(self, command: str, description: str):
        self.command = command
        self.description = description

    def to_dict(self) -> Dict[str, str]:
        return {"command": self.command, "description": self.description}

class Message:
    def __init__(self, bot: 'Robot', chat_id: str, message_id: str, sender_id: Optional[str], text: Optional[str], raw_data: Dict[str, Any]):
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id
        self.sender_id = sender_id
        self.text = text
        self.raw_data = raw_data or {}
        self.args: List[str] = []
        self.time: Optional[str] = raw_data.get("time") 
        self.is_edited: bool = raw_data.get("is_edited", False)
        self.sender_type: str = raw_data.get("sender_type")

        # Added sender's info directly from raw_data for convenience
        self.sender_first_name: Optional[str] = raw_data.get("first_name") # From sender's profile in raw_data
        self.sender_last_name: Optional[str] = raw_data.get("last_name")   # From sender's profile in raw_data
        self.sender_username: Optional[str] = raw_data.get("username")     # From sender's profile in raw_data


        self.reply_to_message_id: Optional[str] = self.raw_data.get("reply_to_message_id")
        self.forwarded_from = ForwardedFrom(self.raw_data.get("forwarded_from", {})) if "forwarded_from" in self.raw_data else None
        self.file = File(self.raw_data.get("file", {})) if "file" in self.raw_data else None
        self.sticker = Sticker(self.raw_data.get("sticker", {})) if "sticker" in self.raw_data else None
        self.contact_message = ContactMessage(self.raw_data.get("contact_message", {})) if "contact_message" in self.raw_data else None
        self.poll = Poll(self.raw_data.get("poll", {})) if "poll" in self.raw_data else None
        self.location = Location(self.raw_data.get("location", {})) if "location" in self.raw_data else None
        self.live_location = LiveLocation(self.raw_data.get("live_location", {})) if "live_location" in self.raw_data else None
        self.aux_data = AuxData(self.raw_data.get("aux_data", {})) if "aux_data" in self.raw_data else None

    @property
    def chat_type(self) -> str:
        if self.chat_id.startswith('g'):
            return 'Group'
        elif self.chat_id.startswith('c'):
            return 'Channel'
        elif self.chat_id.startswith('u'):
            return 'User'
        elif self.chat_id.startswith('b'):
            if self.sender_id and self.sender_id.startswith('u'): 
                return 'User' 
            return 'Bot' 
        return 'Unknown'
        
    @property
    def session(self) -> Dict[str, Any]:
        if self.chat_id not in self.bot.sessions:
            self.bot.sessions[self.chat_id] = {}
        return self.bot.sessions[self.chat_id]

    @property
    def is_reply(self) -> bool:
        return self.reply_to_message_id is not None

    @property
    def is_forward(self) -> bool:
        return self.forwarded_from is not None

    async def reply(self, text: str, **kwargs) -> Dict[str, Any]:
        return await self.bot.send_message(
            self.chat_id,
            text,
            reply_to_message_id=self.message_id,
            **kwargs
        )

    async def edit(self, new_text: str) -> Dict[str, Any]:
        return await self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=new_text
        )

    async def delete(self) -> Dict[str, Any]:
        return await self.bot.delete_message(
            chat_id=self.chat_id,
            message_id=self.message_id
        )

    async def forward(self, to_chat_id: str) -> Dict[str, Any]:
        return await self.bot.forward_message(
            from_chat_id=self.chat_id,
            message_id=self.message_id,
            to_chat_id=to_chat_id
        )

    async def reply_poll(self, question: str, options: List[str], **kwargs) -> Dict[str, Any]:
        return await self.bot.send_poll(
            chat_id=self.chat_id,
            question=question,
            options=options,
            reply_to_message_id=self.message_id,
            **kwargs
        )

    async def reply_contact(self, first_name: str, last_name: str, phone_number: str, **kwargs) -> Dict[str, Any]:
        return await self.bot.send_contact(
            chat_id=self.chat_id,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            reply_to_message_id=self.message_id,
            **kwargs
        )

    async def reply_location(self, latitude: str, longitude: str, **kwargs) -> Dict[str, Any]:
        return await self.bot.send_location(
            chat_id=self.chat_id,
            latitude=latitude,
            longitude=longitude,
            reply_to_message_id=self.message_id,
            **kwargs
        )

    async def reply_sticker(self, sticker_id: str, **kwargs) -> Dict[str, Any]:
        return await self.bot.send_sticker(
            chat_id=self.chat_id,
            sticker_id=sticker_id,
            reply_to_message_id=self.message_id,
            **kwargs
        )

    async def reply_file(self, file_id: str, **kwargs) -> Dict[str, Any]:
        return await self.bot.send_file(
            chat_id=self.chat_id,
            file_id=file_id,
            reply_to_message_id=self.message_id,
            **kwargs
        )

    async def reply_photo(self, photo: str, **kwargs) -> Dict[str, Any]:
        return await self.bot.send_photo(
            chat_id=self.chat_id,
            photo=photo,
            reply_to_message_id=self.message_id,
            **kwargs
        )

    async def reply_video(self, video: str, **kwargs) -> Dict[str, Any]:
        return await self.bot.send_video(
            chat_id=self.chat_id,
            video=video,
            reply_to_message_id=self.message_id,
            **kwargs
        )
    
    async def reply_document(self, document: str, **kwargs) -> Dict[str, Any]:
        return await self.bot.send_document(
            chat_id=self.chat_id,
            document=document,
            reply_to_message_id=self.message_id,
            **kwargs
        )

class InlineMessage:
    def __init__(self, bot: 'Robot', raw_data: dict):
        self.bot = bot
        self.raw_data = raw_data

        self.chat_id: str = raw_data.get("chat_id")
        self.message_id: str = raw_data.get("message_id")
        self.sender_id: str = raw_data.get("sender_id")
        self.text: str = raw_data.get("text")
        self.aux_data = AuxData(raw_data.get("aux_data", {})) if "aux_data" in raw_data else None

    async def reply(self, text: str, **kwargs) -> Dict[str, Any]:
        return await self.bot.send_message(
            chat_id=self.chat_id,
            text=text,
            reply_to_message_id=self.message_id,
            **kwargs
        )

    async def edit(self, new_text: str) -> Dict[str, Any]:
        return await self.bot.edit_message_text(
            chat_id=self.chat_id,
            message_id=self.message_id,
            text=new_text
        )

    async def delete(self) -> Dict[str, Any]:
        return await self.bot.delete_message(
            chat_id=self.chat_id,
            message_id=self.message_id
        )