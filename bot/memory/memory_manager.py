"""
Memory Manager - Handles user memories and conversation history
"""

import json
import os
import aiofiles
from datetime import datetime

class MemoryManager:
    def __init__(self):
        self.user_memories = {}  # Permanent memories set by users
        self.conversation_history = {}  # Last 12 messages per user for context
        self.user_preferences = {}  # User preferences (language, etc.)
        self.user_last_activity = {}  # Track last activity time for each user
        self.memory_file = "bot_memory.json"
        self.load_memory()
    
    def load_memory(self):
        """Load memory from file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.user_memories = data.get('user_memories', {})
                    self.conversation_history = data.get('conversation_history', {})
                    self.user_preferences = data.get('user_preferences', {})
                    self.user_last_activity = data.get('user_last_activity', {})
        except Exception as e:
            print(f"Error loading memory: {e}")
    
    async def save_memory(self):
        """Save memory to file"""
        try:
            data = {
                'user_memories': self.user_memories,
                'conversation_history': self.conversation_history,
                'user_preferences': self.user_preferences,
                'user_last_activity': self.user_last_activity
            }
            async with aiofiles.open(self.memory_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def add_user_memory(self, user_id: str, memory: str):
        """Add a permanent memory about a user (never deleted)"""
        # Update user activity
        self.update_user_activity(user_id)
        
        if user_id not in self.user_memories:
            self.user_memories[user_id] = []
        self.user_memories[user_id].append({
            'memory': memory,
            'timestamp': datetime.now().isoformat()
        })
    
    def update_user_activity(self, user_id: str):
        """Update user's last activity timestamp"""
        self.user_last_activity[user_id] = datetime.now().isoformat()
    
    def cleanup_inactive_user_memory(self, user_id: str):
        """Reduce message history to last 3 messages if user inactive for 3+ hours"""
        if user_id not in self.user_last_activity:
            return False
        
        try:
            last_activity = datetime.fromisoformat(self.user_last_activity[user_id])
            time_diff = datetime.now() - last_activity
            
            # If user inactive for more than 3 hours (10800 seconds)
            if time_diff.total_seconds() > 10800:  # 3 hours = 10800 seconds
                if user_id in self.conversation_history and len(self.conversation_history[user_id]) > 3:
                    # Keep only last 3 messages
                    self.conversation_history[user_id] = self.conversation_history[user_id][-3:]
                    print(f"Cleaned up memory for inactive user {user_id}: reduced to 3 messages")
                    return True
        except Exception as e:
            print(f"Error in cleanup for user {user_id}: {e}")
        
        return False
    
    def add_message_to_history(self, user_id: str, message: str, response: str, max_messages: int = 25):
        """Add message to conversation history with tier-based limits"""
        # Update user activity first
        self.update_user_activity(user_id)
        
        # Check if we need to cleanup memory for this user due to inactivity
        self.cleanup_inactive_user_memory(user_id)
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'user_message': message,
            'bot_response': response,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep messages based on tier (max 25 for premium, but we'll store up to 25 for all users)
        # The context limit is applied when retrieving, not storing
        if len(self.conversation_history[user_id]) > max_messages:
            self.conversation_history[user_id] = self.conversation_history[user_id][-max_messages:]
    
    def get_user_context(self, user_id: str, context_limit: int = 12) -> str:
        """Get user context for AI with tier-based limits"""
        context = ""
        
        # Add permanent user memories (these stay forever)
        if user_id in self.user_memories:
            memories = [m['memory'] for m in self.user_memories[user_id]]
            context += f"What I remember about this user (permanent): {'; '.join(memories)}\n\n"
        
        # Add recent conversation history based on user's tier limit
        if user_id in self.conversation_history:
            # Use the tier-based context limit
            recent_convos = self.conversation_history[user_id][-context_limit:]  # Show messages based on tier
            context += f"Recent conversation context (last {len(recent_convos)} messages):\n"
            for i, convo in enumerate(recent_convos, 1):
                context += f"{i}. User: '{convo['user_message'][:150]}...' | Bot: '{convo['bot_response'][:150]}...'\n"
        
        return context
    
    def cleanup_all_inactive_users(self):
        """Check and cleanup memory for all inactive users"""
        cleaned_users = []
        
        for user_id in list(self.user_last_activity.keys()):
            if self.cleanup_inactive_user_memory(user_id):
                cleaned_users.append(user_id)
        
        return cleaned_users
    
    def delete_specific_memory(self, user_id: str, memory_index: int) -> bool:
        """Delete a specific memory by index"""
        if user_id not in self.user_memories:
            return False
        
        memories = self.user_memories[user_id]
        if 0 <= memory_index < len(memories):
            del memories[memory_index]
            # Update activity
            self.update_user_activity(user_id)
            return True
        return False
    
    def get_user_memories_with_indices(self, user_id: str) -> list:
        """Get user memories with their indices for deletion purposes"""
        if user_id not in self.user_memories:
            return []
        
        memories_with_indices = []
        for i, memory_data in enumerate(self.user_memories[user_id]):
            memories_with_indices.append({
                'index': i,
                'memory': memory_data['memory'],
                'timestamp': memory_data['timestamp']
            })
        return memories_with_indices
    
    def edit_specific_memory(self, user_id: str, memory_index: int, new_memory: str) -> bool:
        """Edit a specific memory by index"""
        if user_id not in self.user_memories:
            return False
        
        memories = self.user_memories[user_id]
        if 0 <= memory_index < len(memories):
            memories[memory_index]['memory'] = new_memory
            memories[memory_index]['updated_at'] = datetime.now().isoformat()
            # Update user activity
            self.update_user_activity(user_id)
            return True
        return False

    def clear_user_data(self, user_id: str):
        """Clear all data for a user"""
        if user_id in self.user_memories:
            del self.user_memories[user_id]
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
        if user_id in self.user_preferences:
            del self.user_preferences[user_id]
        if user_id in self.user_last_activity:
            del self.user_last_activity[user_id]
    
    def set_user_language(self, user_id: str, language: str):
        """Set user's preferred language"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        self.user_preferences[user_id]['language'] = language
    
    def get_user_language(self, user_id: str) -> str:
        """Get user's preferred language (default: english)"""
        if user_id in self.user_preferences and 'language' in self.user_preferences[user_id]:
            return self.user_preferences[user_id]['language']
        return 'english'
    
    def is_new_user(self, user_id: str) -> bool:
        """Check if user is new (no memories and no conversation history)"""
        has_memories = user_id in self.user_memories and len(self.user_memories[user_id]) > 0
        has_conversations = user_id in self.conversation_history and len(self.conversation_history[user_id]) > 0
        return not (has_memories or has_conversations)
    
    def has_completed_welcome_setup(self, user_id: str) -> bool:
        """Check if user has completed the welcome setup process"""
        # A user has completed welcome setup if they have at least one memory
        # that contains basic profile information (name, age, hobbies, etc.)
        if user_id not in self.user_memories or not self.user_memories[user_id]:
            return False
        
        # Check if any memory contains welcome setup indicators
        for memory in self.user_memories[user_id]:
            memory_text = memory['memory'].lower()
            # Look for structured memory from welcome setup (contains multiple fields)
            if ('name:' in memory_text or 'age:' in memory_text or 
                'hobbies:' in memory_text or 'occupation:' in memory_text or
                'likes:' in memory_text):
                return True
        
        return False
    
    def get_stats(self):
        """Get memory statistics"""
        total_users = len(self.user_memories)
        total_conversations = sum(len(convos) for convos in self.conversation_history.values())
        total_memories = sum(len(memories) for memories in self.user_memories.values())
        
        return {
            'total_users': total_users,
            'total_conversations': total_conversations,
            'total_memories': total_memories
        }