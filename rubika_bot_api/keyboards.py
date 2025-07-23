from typing import Dict, List, Any, Optional

def create_simple_keyboard(buttons: List[List[str]]) -> Dict:
    """
    Create a simple chat keypad (keyboard) structure for Rubika.

    Args:
        buttons: List of button rows, each row is a list of button texts.
        Example: [["Button1", "Button2"], ["Button3"]]

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
    
    @staticmethod
    def button_link(text: str, url: str) -> Dict[str, Any]:
        """
        Creates a dictionary for an inline link button.

        Args:
            text (str): The text that appears on the button.
            url (str): The URL that will be opened when the button is clicked.

        Returns:
            Dict[str, Any]: The inline link button.
        """
        return {"id": url, "type": "Link", "button_text": text} 


    @staticmethod
    def button_selection(text: str, button_id: str, selection_id: str, items: List[Dict[str, str]], title: Optional[str] = None, is_multi_selection: bool = False, columns_count: Optional[str] = None, search_type: str = "None", get_type: str = "Local") -> Dict[str, Any]:
        """
        Creates an inline selection button that opens a list of selectable items.
        Corresponds to ButtonSelection model.
        """
        button_selection_data = {
            "selection_id": selection_id,
            "items": items, # Each item is {"text": "...", "image_url": "...", "type": "TextOnly"}
            "is_multi_selection": is_multi_selection,
            "search_type": search_type,
            "get_type": get_type
        }
        if title: button_selection_data["title"] = title
        if columns_count: button_selection_data["columns_count"] = columns_count

        return {"id": button_id, "type": "Selection", "button_text": text, "button_selection": button_selection_data}

    @staticmethod
    def button_calendar(text: str, button_id: str, calendar_type: str = "DatePersian", default_value: Optional[str] = None, min_year: Optional[str] = None, max_year: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline calendar button for date selection.
        Corresponds to ButtonCalendar model.
        """
        button_calendar_data = {"type": calendar_type}
        if default_value: button_calendar_data["default_value"] = default_value
        if min_year: button_calendar_data["min_year"] = min_year
        if max_year: button_calendar_data["max_year"] = max_year
        if title: button_calendar_data["title"] = title

        return {"id": button_id, "type": "Calendar", "button_text": text, "button_calendar": button_calendar_data}

    @staticmethod
    def button_number_picker(text: str, button_id: str, min_value: str, max_value: str, default_value: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline number picker button for range selection.
        Corresponds to ButtonNumberPicker model.
        """
        button_number_picker_data = {
            "min_value": min_value,
            "max_value": max_value
        }
        if default_value: button_number_picker_data["default_value"] = default_value
        if title: button_number_picker_data["title"] = title

        return {"id": button_id, "type": "NumberPicker", "button_text": text, "button_number_picker": button_number_picker_data}

    @staticmethod
    def button_string_picker(text: str, button_id: str, items: List[str], default_value: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline string picker button for selecting from a list of strings.
        Corresponds to ButtonStringPicker model.
        """
        button_string_picker_data = {"items": items}
        if default_value: button_string_picker_data["default_value"] = default_value
        if title: button_string_picker_data["title"] = title

        return {"id": button_id, "type": "StringPicker", "button_text": text, "button_string_picker": button_string_picker_data}

    @staticmethod
    def button_location(text: str, button_id: str, default_pointer_location: Optional[Dict[str, str]] = None, default_map_location: Optional[Dict[str, str]] = None, location_type: str = "Picker", title: Optional[str] = None, location_image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline location picker/viewer button.
        Corresponds to ButtonLocation model. default_pointer_location/default_map_location are {"latitude": "...", "longitude": "..."}
        """
        button_location_data = {"type": location_type}
        if default_pointer_location: button_location_data["default_pointer_location"] = default_pointer_location
        if default_map_location: button_location_data["default_map_location"] = default_map_location
        if title: button_location_data["title"] = title
        if location_image_url: button_location_data["location_image_url"] = location_image_url

        return {"id": button_id, "type": "Location", "button_text": text, "button_location": button_location_data}
    
    @staticmethod
    def button_textbox(text: str, button_id: str, type_line: str = "SingleLine", type_keypad: str = "String", place_holder: Optional[str] = None, title: Optional[str] = None, default_value: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline textbox button for text input.
        Corresponds to ButtonTextbox model.
        """
        button_textbox_data = {
            "type_line": type_line,
            "type_keypad": type_keypad
        }
        if place_holder: button_textbox_data["place_holder"] = place_holder
        if title: button_textbox_data["title"] = title
        if default_value: button_textbox_data["default_value"] = default_value

        return {"id": button_id, "type": "Textbox", "button_text": text, "button_textbox": button_textbox_data}

    @staticmethod
    def button_payment(text: str, button_id: str) -> Dict[str, Any]:
        """Creates a simple inline payment button."""
        return {"id": button_id, "type": "Payment", "button_text": text}

    @staticmethod
    def button_camera_image(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to open camera for image capture."""
        return {"id": button_id, "type": "CameraImage", "button_text": text}

    @staticmethod
    def button_gallery_video(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to open gallery for video selection."""
        return {"id": button_id, "type": "GalleryVideo", "button_text": text}

    # Add more simplified button types as needed from ButtonTypeEnum


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
        self.rows_list: List[Dict[str, List[Dict[str, str]]]] = [] 
        self._resize = resize # CORRECTED: Assign resize
        self._on_time = on_time # CORRECTED: Assign on_time

    def row(self, *button_texts: str) -> 'ChatKeyboardBuilder':
        """
        Adds a new row of buttons to the chat keypad.

        Args:
            *button_texts: Strings representing the button texts to add to the row.
                           For chat keypads, ID and type are usually the same as text.

        Returns:
            ChatKeyboardBuilder: The builder instance for chaining.
        """
        button_list = []
        for text_val in button_texts:
            button_list.append({
                "id": text_val, 
                "type": "Simple", 
                "button_text": text_val
            })
        self.rows_list.append({"buttons": button_list})
        return self

    def build(self) -> Dict[str, Any]:
        """
        Finalizes and returns the constructed keyboard layout.

        Returns:
            Dict[str, Any]: The keyboard layout as a dictionary, containing rows and their button configurations.
        """
        return {
            "rows": self.rows_list,
            "resize_keyboard": self._resize,
            "on_time_keyboard": self._on_time
        }
    
    