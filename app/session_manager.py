from typing import Dict
import uuid
from memory.memory_manager import MemoryManager
from datetime import datetime, timedelta


# Session management
class Session:
    def __init__(self, user_id: str = None):
        self.session_id = (
            f"{user_id}_{uuid.uuid4().hex[:8]}" if user_id else uuid.uuid4().hex
        )
        self.start_time = datetime.now()
        self.last_activity = datetime.now()
        self.message_count = 0
        self.is_active = True
        self.user_id = user_id
        # Initialize memory manager with both session_id and user_id
        self.memory = MemoryManager(self.session_id, user_id)

    def update_activity(self):
        """Update the last activity time of the session."""
        self.last_activity = datetime.now()

    def check_timeout(self, timeout_minutes: int) -> bool:
        """
        Check if the session has timed out.

        Args:
            timeout_minutes (int): The timeout duration in minutes.

        Returns:
            bool: True if the session has timed out, False otherwise.
        """
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.timeout_minutes = 30

    def get_session(self, session_id: str) -> Session:
        """
        Retrieve an active session by its ID.

        Args:
            session_id (str): The ID of the session to retrieve.

        Returns:
            Session: The active session associated with the given ID, or None if not found or inactive.
        """
        session = self.sessions.get(session_id, None)
        if session and session.is_active:
            return session
        return None

    def create_session(self, user_id: str) -> Session:
        """
        Create a new session for a user.

        Args:
            user_id (str): The ID of the user for whom to create the session.

        Returns:
            Session: The newly created session.
        """
        session = Session(user_id)
        self.sessions[session.session_id] = session
        return session

    def check_session_timeout(self, session_id: str) -> bool:
        """
        Check if a session has timed out.

        Args:
            session_id (str): The ID of the session to check.

        Returns:
            bool: True if the session has timed out, False otherwise.
        """
        session = self.get_session(session_id)
        return session.check_timeout(self.timeout_minutes) if session else True

    def end_session(self, session_id: str) -> None:
        """
        End a session, marking it as inactive and removing it from the manager.

        Args:
            session_id (str): The ID of the session to end.
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            # Store memory summary before ending session
            session.memory.store_summary()
            session.is_active = False
            del self.sessions[session_id]
