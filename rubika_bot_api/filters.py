from .context import Message
from typing import Callable, Any, List

class Filter:
    def __call__(self, message: Message) -> bool:
        raise NotImplementedError

    def __and__(self, other: 'Filter') -> 'Filter':
        return AndFilter(self, other)

    def __or__(self, other: 'Filter') -> 'Filter':
        return OrFilter(self, other)

    def __invert__(self) -> 'Filter':
        return InvertFilter(self)

class AndFilter(Filter):
    def __init__(self, filter1: Filter, filter2: Filter):
        self.filter1 = filter1
        self.filter2 = filter2

    def __call__(self, message: Message) -> bool:
        return self.filter1(message) and self.filter2(message)

class OrFilter(Filter):
    def __init__(self, filter1: Filter, filter2: Filter):
        self.filter1 = filter1
        self.filter2 = filter2

    def __call__(self, message: Message) -> bool:
        return self.filter1(message) or self.filter2(message)

class InvertFilter(Filter):
    def __init__(self, original_filter: Filter):
        self.original_filter = original_filter

    def __call__(self, message: Message) -> bool:
        return not self.original_filter(message)

def create(func: Callable[[Message], bool]) -> Filter:
    class CustomFilter(Filter):
        def __call__(self, message: Message) -> bool:
            return func(message)
    return CustomFilter()

all = create(lambda m: True)

# --- Filters for Message Content ---
text = create(lambda m: m.text is not None and m.text != "") 

# Filters for File Types (based on file extension as 'type' is not always in raw_data)
photo = create(lambda m: m.file is not None and m.file.file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')))
video = create(lambda m: m.file is not None and m.file.file_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')))
voice = create(lambda m: m.file is not None and m.file.file_name.lower().endswith(('.ogg', '.oga', '.opus'))) 
audio = create(lambda m: m.file is not None and m.file.file_name.lower().endswith(('.mp3', '.wav', '.flac'))) 
sticker = create(lambda m: m.sticker is not None) 

document = create(lambda m: m.file is not None and \
                              not photo(m) and \
                              not video(m) and \
                              not voice(m) and \
                              not audio(m) and \
                              not sticker(m))

contact = create(lambda m: m.contact_message is not None)
poll = create(lambda m: m.poll is not None)
location = create(lambda m: m.location is not None)

# --- Filters for Chat Type ---
group = create(lambda m: m.chat_type == 'Group')
private = create(lambda m: m.chat_type == 'User') 
pv = private 
channel = create(lambda m: m.chat_type == 'Channel')

# --- Filters for Message Properties ---
is_reply = create(lambda m: m.is_reply)
is_forward = create(lambda m: m.is_forward)



def command(*command_names: str) -> Filter:

    """Returns a filter that matches messages with the given command name(s).
    
    If the message text starts with a '/', it is split into a command name and
    arguments. The command name is checked against the given list of names.
    
    If the command name matches, the message is marked as a command and the
    message.args attribute is set to a list of the arguments, split by space.
    
    Example:
        @bot.on_message(filters.command('start', 'help'))
        async def handle_command(message: Message):
            if message.args:
                # Handle the command with arguments
                pass
            else:
                # Handle the command with no arguments
                pass
    """
    
    def _check(message: Message) -> bool:
        if not message.text or not message.text.startswith('/'):
            return False
        
        parts = message.text.split(maxsplit=1)
        cmd_text = parts[0][1:] # Remove the '/' prefix from command
        
        if cmd_text in command_names:
            # Extract arguments: anything after the command, split by space
            message.args = parts[1].split() if len(parts) > 1 else []
            return True
        return False
    return create(_check)