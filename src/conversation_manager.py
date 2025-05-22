import time
from typing import Dict, Any, Optional


class ConversationManager:
    """
    Manages multi-step conversation states with TTL (Time To Live) functionality.
    
    This class provides an in-memory storage solution for managing active conversations,
    typically used in chat applications like Slack bots. It handles conversation lifecycle
    including creation, updates, retrieval, and automatic cleanup based on TTL.
    
    Attributes:
        active_conversations: Dictionary storing active conversation data indexed by thread ID
        ttl: Time to live in seconds for conversations before they expire (default: 3600s/1hour)
    """
    
    def __init__(self, ttl: int = 3600):
        """
        Initialize the ConversationManager with specified TTL.
        
        Args:
            ttl (int): Time to live in seconds for conversations. Defaults to 3600 (1 hour).
        """
        self.active_conversations: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def start_conversation(self, thread_ts: str, action_type: str, context: Dict[str, Any]) -> None:
        """
        Start a new conversation and register it in the active conversations storage.
        
        Creates a new conversation entry with initial context, timestamp, and state.
        The conversation is marked as 'awaiting_response' by default.
        
        Args:
            thread_ts (str): Unique Slack thread ID used as conversation identifier
            action_type (str): Type of action being performed (e.g., 'create_card', 'update_task')
            context (Dict[str, Any]): Initial data and context needed for the conversation
            
        Returns:
            None
        """
        self.active_conversations[thread_ts] = {
            'action_type': action_type,
            'created_at': time.time(),
            'context': context,
            'state': 'awaiting_response'
        }
        print(f"✅ Starting conversation: {thread_ts} - {action_type}")

    def update_conversation(self, thread_ts: str, updates: Dict[str, Any]) -> bool:
        """
        Update the context of an existing conversation.
        
        Merges the provided updates into the existing conversation context.
        Only updates conversations that are currently active.
        
        Args:
            thread_ts (str): Thread ID of the conversation to update
            updates (Dict[str, Any]): Dictionary containing the updates to merge into context
            
        Returns:
            bool: True if the conversation was found and updated, False otherwise
        """
        if thread_ts in self.active_conversations:
            self.active_conversations[thread_ts]['context'].update(updates)
            return True
        return False

    def get_conversation(self, thread_ts: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an active conversation if it exists and hasn't expired.
        
        Checks if the conversation exists and validates that it hasn't exceeded the TTL.
        If the conversation has expired, it's automatically cleaned up and None is returned.
        
        Args:
            thread_ts (str): Thread ID of the conversation to retrieve
            
        Returns:
            Optional[Dict[str, Any]]: Conversation data if found and valid, None if not found or expired
        """
        conversation = self.active_conversations.get(thread_ts)
        
        if conversation:
            # Check if conversation has expired (using instance TTL, not hardcoded 3600)
            if time.time() - conversation['created_at'] > self.ttl:
                self.end_conversation(thread_ts)
                return None
        
        return conversation

    def end_conversation(self, thread_ts: str) -> None:
        """
        Terminate and remove a conversation from active storage.
        
        Removes the conversation from the active conversations dictionary and
        logs the termination for debugging purposes.
        
        Args:
            thread_ts (str): Thread ID of the conversation to terminate
            
        Returns:
            None
        """
        if thread_ts in self.active_conversations:
            del self.active_conversations[thread_ts]
            print(f"🔚 Conversation ended: {thread_ts}")