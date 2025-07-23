import re
from typing import List, Dict, Any

# --- Validation Functions ---
def is_valid_phone_number(phone: str) -> bool:
    """
    Validates a simple phone number string.

    Args:
        phone (str): The phone number to validate.

    Returns:
        bool: True if the phone number is a digit-only string with a length between 10 and 15, otherwise False.
    """
    return phone.isdigit() and (10 <= len(phone) <= 15)


RUBIKA_LINK_PATTERN = re.compile(r'(?:https?://)?rubika\.ir/\S*')
GROUP_LINK_PATTERN = re.compile(r'https://rubika\.ir/joing/[A-Za-z0-9]+')
CHANNEL_LINK_PATTERN = re.compile(r'https://rubika\.ir/[A-Za-z0-9_]+')
USERNAME_PATTERN = re.compile(r'@([a-zA-Z0-9_]{3,32})')

def is_rubika_link(text: str) -> bool:
    """Checks if the given text contains a generic Rubika link."""
    return bool(RUBIKA_LINK_PATTERN.search(text))

def is_group_link(text: str) -> bool:
    """Checks if the given text contains a Rubika group join link."""
    return bool(GROUP_LINK_PATTERN.search(text))

def is_channel_link(text: str) -> bool:
    """Checks if the given text contains a Rubika channel link."""
    return bool(CHANNEL_LINK_PATTERN.search(text))

def is_username(text: str) -> bool:
    """Checks if the given text contains a Rubika username."""
    return bool(USERNAME_PATTERN.search(text))

# --- Extraction Functions ---
def get_rubika_links(text: str) -> List[str]:
    """
    Extracts all Rubika links from a given text.

    Args:
        text (str): The input string to search.

    Returns:
        List[str]: A list of all matched links.
    """
    return RUBIKA_LINK_PATTERN.findall(text)

def get_group_links(text: str) -> List[str]:
    """
    Extracts all Rubika group join links from a given text.

    Args:
        text (str): The input string to search.

    Returns:
        List[str]: A list of all matched group links.
    """
    return GROUP_LINK_PATTERN.findall(text)

def get_channel_links(text: str) -> List[str]:
    """
    Extracts all Rubika channel links from a given text.

    Args:
        text (str): The input string to search.

    Returns:
        List[str]: A list of all matched channel links.
    """
    return CHANNEL_LINK_PATTERN.findall(text)

def get_usernames(text: str) -> List[str]:
    """
    Extracts all Rubika usernames (including the @) from a given text.

    Args:
        text (str): The input string to search.

    Returns:
        List[str]: A list of all matched usernames.
    """
    return [match.group(0) for match in USERNAME_PATTERN.finditer(text)]

# --- Text Formatting Functions ---

def Bold(text: str) -> str:
    """Formats text as bold using Markdown."""
    return f'**{text.strip()}**'

def Italic(text: str) -> str:
    """Formats text as italic using Markdown."""
    return f'_{text.strip()}'

def Underline(text: str) -> str:
    """Formats text with an underline using Markdown."""
    return f'--{text.strip()}--'

def Strike(text: str) -> str:
    """Formats text with a strikethrough using Markdown."""
    return f'~~{text.strip()}~~'

def Spoiler(text: str) -> str:
    """Formats text as a spoiler using Markdown."""
    return f'||{text.strip()}||'

def Code(text: str) -> str:
    """Formats text as inline code using Markdown."""
    return f'`{text.strip()}`'

def Mention(text: str, object_guid: str) -> str:
    """
    Formats a text mention for a user with a specific object GUID.

    Args:
        text (str): The text to display for the mention.
        object_guid (str): The GUID of the user to mention.

    Returns:
        str: The formatted mention string.
    """
    return f'[{text.strip()}]({object_guid.strip()})'

def HyperLink(text: str, link: str) -> str:
    """
    Creates a hyperlink with the provided text and URL.

    Args:
        text (str): The text to display for the hyperlink.
        link (str): The URL for the hyperlink.

    Returns:
        str: The formatted hyperlink string.
    """
    return f'[{text.strip()}]({link.strip()})'