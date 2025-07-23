from typing import Dict, List, Any

def create_simple_keyboard(buttons: List[List[str]]) -> Dict:
    """
    Create a simple chat keypad (keyboard) structure for Rubika.

    Args:
        BUTTONS: A list of button rows, where each row is a list of button texts.
        Example: [["BUTTON1", "BUTTON2"], ["BUTTON3"]]

    Returns:
        Dict: The keyboard layout as a dictionary.
    """
    keyboard = {"rows": []}
    for row in buttons:
        keyboard["rows"].append({"buttons": [{"text": text} for text in row]})
    return keyboard


class InlineKeyboardBuilder:
    """A helper class to easily build inline keypads using a fluent interface."""
    def __init__(self):
        """Initializes a new instance of the InlineKeyboardBuilder class."""
        self.rows: List[Dict[str, List[Dict[str, str]]]] = []

    def row(self, *buttons: Dict[str, Any]) -> 'InlineKeyboardBuilder':
        """
        Adds a new row of buttons to the keypad.

        Args:
            *buttons: Dictionaries representing the buttons to add to the row.

        Returns:
            InlineKeyboardBuilder: The builder instance for chaining.
        """
        self.rows.append({"buttons": list(buttons)})
        return self

    @staticmethod
    def button(text: str, button_id: str, button_type: str = "Simple") -> Dict[str, Any]:
        """
        Creates a dictionary for a single inline button.

        Args:
            text (str): The text that appears on the button.
            button_id (str): The ID of the button.
            button_type (str, optional): The type of the button. Defaults to "Simple".

        Returns:
            Dict[str, Any]: The inline keyboard button.
        """
        return {"id": button_id, "type": button_type, "button_text": text}

    def build(self) -> Dict[str, Any]:
        """
        Finalizes and returns the constructed keyboard layout.

        Returns:
            Dict[str, Any]: The keyboard layout as a dictionary, containing rows and their button configurations.
        """
        return {"rows": self.rows}


class ChatKeyboardBuilder:
    """A helper class to easily build chat keypads (keyboards) using a fluent interface."""
    def __init__(self, resize: bool = True, on_time: bool = False):
        """
        Initializes a new instance of the ChatKeyboardBuilder class.

        Args:
            resize (bool): If True, the keyboard is resized to fit the screen. Defaults to True.
            on_time (bool): If True, the keyboard remains visible until the user closes it. Defaults to False.
        """
        self.rows: List[Dict[str, List[Dict[str, str]]]] = []
        self._resize = resize
        self._on_time = on_time

    def row(self, *buttons: str) -> 'ChatKeyboardBuilder':
        """
        Adds a new row of buttons.

        Args:
            *buttons: Strings representing the button texts to add to the row.

        Returns:
            ChatKeyboardBuilder: The builder instance for chaining.
        """
        button_list = [{"text": text} for text in buttons]
        self.rows.append({"buttons": button_list})
        return self

    def build(self) -> Dict[str, Any]:
        """
        Finalizes and returns the constructed keyboard layout.

        Returns:
            Dict[str, Any]: The keyboard layout as a dictionary, containing rows and their button configurations.
        """
        return {
            "rows": self.rows,
            "resize_keyboard": self._resize,
            "on_time_keyboard": self._on_time
        }