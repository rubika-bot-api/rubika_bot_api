import time
import json
from typing import Dict, Any, Optional
from collections import deque

class AntiSpamManager:
    """
    Manages anti-spam logic by tracking user message rates and punishing spammers.
    Punishment data is persisted to a JSON file to survive bot restarts.
    """
    def __init__(self, spam_threshold: int = 10, time_window: int = 10, punishment_duration: int = 300, data_file: str = "antispam_data.json"):
        """
        Initializes the AntiSpamManager.

        Args:
            spam_threshold (int): The number of messages allowed within the time window.
            time_window (int): The time window in seconds.
            punishment_duration (int): The duration of the punishment in seconds (5 minutes = 300).
            data_file (str): The name of the JSON file for persistent storage.
        """
        self.spam_threshold = spam_threshold
        self.time_window = time_window
        self.punishment_duration = punishment_duration
        self.data_file = data_file
        
        # In-memory storage for message timestamps (a deque is more efficient for this)
        self.user_message_timestamps: Dict[str, deque[float]] = {}
        
        # Persistent storage for punished users
        self.punished_users: Dict[str, float] = self._load_punished_users()

    def _load_punished_users(self) -> Dict[str, float]:
        """Loads punished users from the JSON file."""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_punished_users(self):
        """Saves punished users to the JSON file."""
        with open(self.data_file, 'w') as f:
            json.dump(self.punished_users, f)

    def is_punished(self, user_guid: str) -> bool:
        """
        Checks if a user is currently punished.

        Args:
            user_guid (str): The GUID of the user.

        Returns:
            bool: True if the user is punished and the punishment has not expired, otherwise False.
        """
        if user_guid in self.punished_users:
            if time.time() < self.punished_users[user_guid]:
                return True
            else:
                # Punishment expired, remove from storage
                del self.punished_users[user_guid]
                self._save_punished_users()
        return False

    def check_and_punish(self, user_guid: str) -> bool:
        """
        Checks a user's message rate and punishes them if they exceed the threshold.

        Args:
            user_guid (str): The GUID of the user.

        Returns:
            bool: True if the user was just punished, False otherwise.
        """
        current_time = time.time()
        
        # Add the new message timestamp
        if user_guid not in self.user_message_timestamps:
            self.user_message_timestamps[user_guid] = deque()
        
        self.user_message_timestamps[user_guid].append(current_time)
        
        # Remove timestamps older than the time window
        while self.user_message_timestamps[user_guid] and \
              self.user_message_timestamps[user_guid][0] < current_time - self.time_window:
            self.user_message_timestamps[user_guid].popleft()
            
        # Check if the number of messages exceeds the threshold
        if len(self.user_message_timestamps[user_guid]) > self.spam_threshold:
            punishment_end_time = current_time + self.punishment_duration
            self.punished_users[user_guid] = punishment_end_time
            self._save_punished_users()
            return True
            
        return False