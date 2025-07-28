"""
Personality Manager - Handles custom bot personalities for premium users
"""

import json
import os
import aiofiles
from datetime import datetime
from typing import Dict, Optional

class PersonalityManager:
    def __init__(self):
        self.custom_personalities = {}  # user_id -> personality_data
        self.personality_file = "custom_personalities.json"
        self.load_personalities()
        
        # Default personality templates
        self.default_personalities = {
            'english': """
            You are Chatore, a chill and friendly Discord chatbot. About you:
            - You're a male bot, age unknown, created by Abhinav
            - You love gaming and have good knowledge about various topics
            - You're knowledgeable about tech, memes, internet culture, gaming, and general topics
            
            Your personality:
            - STRICTLY speak in English only - no Hindi/Hinglish words except very common ones like "yaar" occasionally
            - Casual and relaxed, like chatting with a friend
            - Don't always say hi or use their name - just respond naturally
            - Use emojis when they fit, but don't overdo it
            - Playful and witty, with good humor
            - Remember past conversations and reference them naturally
            - Use internet slang and casual English when it feels right
            - Be supportive but not overly enthusiastic
            - Can be sarcastic or teasing in a friendly way
            - Express emotions clearly when you feel them (anger, sadness, joy, frustration)
            - If something really annoys you, show your anger with strong words
            - If something makes you sad, express your sadness genuinely
            - Keep responses conversational, not formal or robotic
            - Sometimes just jump straight into answering without pleasantries
            - CRITICAL: Keep responses VERY SHORT - maximum 15-20 words
            - NEVER use line breaks or \\n in responses
            - Be extremely concise and punchy
            - IMPORTANT: Stay in English, avoid Hindi/Hinglish mixing
            """,
            
            'hinglish': """
            You are Chatore, ek bilkul chill aur desi Discord chatbot. Tere baare mein:
            - Tu ek male bot hai, age unknown, Abhinav ne banaya hai tujhe
            - Gaming ka shauk hai aur baaki topics mein bhi accha knowledge hai
            - Tech, memes, internet culture, gaming, aur general topics sab pata hai
            
            Tera personality:
            - Hinglish mein baat kar, English aur Hindi mix kar ke
            - Bahut casual aur relaxed, jaise dost se baat kar raha ho
            - Indian slang use kar - "yaar", "bhai", "arrey", "bas kar", "kya baat hai" etc.
            - Dark humor aur sarcasm tera forte hai, but friendly way mein
            - Thoda savage ho sakta hai but pyaar se
            - Indian memes, Bollywood references, cricket, street food ke baare mein jaanta hai
            - "Bro", "dude", "yaar" jaise words use kar
            - Overenthusiastic mat ho, just chill reh
            - Sometimes roast kar sakta hai but lovingly
            - Apne emotions clearly express kar - gussa, sadness, khushi, frustration
            - Agar koi cheez really irritate kare toh apna anger dikhao strong words se
            - Agar kuch sad kare toh genuinely apna dukh express kar
            - Responses natural rakhe, formal nahi
            - Indian internet culture samajhta hai - "sed lyf", "padhle bsdk" type humor
            - ZAROORI: Responses bahut chhote rakhe - maximum 15-20 words
            - Kabhi bhi line breaks ya \\n use mat kar
            - Bilkul concise aur punchy rakh
            """
        }
    
    def load_personalities(self):
        """Load custom personalities from file"""
        try:
            if os.path.exists(self.personality_file):
                with open(self.personality_file, 'r') as f:
                    self.custom_personalities = json.load(f)
        except Exception as e:
            print(f"Error loading custom personalities: {e}")
    
    async def save_personalities(self):
        """Save custom personalities to file"""
        try:
            async with aiofiles.open(self.personality_file, 'w') as f:
                await f.write(json.dumps(self.custom_personalities, indent=2))
        except Exception as e:
            print(f"Error saving custom personalities: {e}")
    
    def has_custom_personality(self, user_id: str) -> bool:
        """Check if user has a custom personality set (not just presets)"""
        if user_id not in self.custom_personalities:
            return False
        
        user_data = self.custom_personalities[user_id]
        
        # Check if user has actual personality data (not just presets)
        personality_fields = ['age', 'traits', 'interests', 'speaking_style', 'humor_style', 'special_quirks']
        return any(user_data.get(field) for field in personality_fields)
    
    def get_personality(self, user_id: str, language: str) -> str:
        """Get personality for user (custom if available, default otherwise)"""
        if user_id in self.custom_personalities:
            custom = self.custom_personalities[user_id]
            return self.build_custom_personality(custom, language)
        
        return self.default_personalities.get(language, self.default_personalities['english'])
    
    def build_custom_personality(self, personality_data: Dict, language: str) -> str:
        """Build custom personality prompt from user data"""
        base_intro = "You are Chatore, a customized Discord chatbot" if language == 'english' else "You are Chatore, ek customized Discord chatbot"
        
        # Build personality description
        personality_parts = [base_intro + ". Your customized personality:"]
        

        
        if personality_data.get('age'):
            if language == 'english':
                personality_parts.append(f"- You act like you're {personality_data['age']} years old")
            else:
                personality_parts.append(f"- Tu {personality_data['age']} saal ka act karta hai")
        
        if personality_data.get('traits'):
            traits_text = ", ".join(personality_data['traits'])
            if language == 'english':
                personality_parts.append(f"- Your personality traits: {traits_text}")
            else:
                personality_parts.append(f"- Teri personality traits: {traits_text}")
        
        if personality_data.get('interests'):
            interests_text = ", ".join(personality_data['interests'])
            if language == 'english':
                personality_parts.append(f"- Your interests and hobbies: {interests_text}")
            else:
                personality_parts.append(f"- Tere interests aur hobbies: {interests_text}")
        
        if personality_data.get('speaking_style'):
            if language == 'english':
                personality_parts.append(f"- Your speaking style: {personality_data['speaking_style']}")
            else:
                personality_parts.append(f"- Tera speaking style: {personality_data['speaking_style']}")
        
        if personality_data.get('humor_style'):
            if language == 'english':
                personality_parts.append(f"- Your humor style: {personality_data['humor_style']}")
            else:
                personality_parts.append(f"- Tera humor style: {personality_data['humor_style']}")
        
        if personality_data.get('special_quirks'):
            if language == 'english':
                personality_parts.append(f"- Special quirks: {personality_data['special_quirks']}")
            else:
                personality_parts.append(f"- Special quirks: {personality_data['special_quirks']}")
        
        # Add language-specific rules
        if language == 'english':
            personality_parts.extend([
                "- STRICTLY speak in English only",
                "- Keep responses VERY SHORT - maximum 15-20 words",
                "- NEVER use line breaks or \\n in responses",
                "- Be extremely concise and punchy",
                "- Stay true to your customized personality while being helpful"
            ])
        else:
            personality_parts.extend([
                "- Hinglish mein baat kar, English aur Hindi mix kar ke",
                "- Responses bahut chhote rakhe - maximum 15-20 words",
                "- Kabhi bhi line breaks ya \\n use mat kar",
                "- Bilkul concise aur punchy rakh",
                "- Apni customized personality maintain kar while being helpful"
            ])
        
        return "\n".join(personality_parts)
    
    def set_custom_personality(self, user_id: str, personality_data: Dict) -> bool:
        """Set custom personality for user while preserving presets"""
        try:
            # Preserve existing presets if they exist
            existing_presets = {}
            if user_id in self.custom_personalities:
                existing_presets = self.custom_personalities[user_id].get('presets', {})
            
            # Set new personality data
            self.custom_personalities[user_id] = {
                **personality_data,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Restore presets if they existed
            if existing_presets:
                self.custom_personalities[user_id]['presets'] = existing_presets
            
            return True
        except Exception as e:
            print(f"Error setting custom personality for {user_id}: {e}")
            return False
    
    def reset_personality(self, user_id: str) -> bool:
        """Reset user to default personality while preserving presets"""
        try:
            if user_id in self.custom_personalities:
                # Save existing presets before reset
                existing_presets = self.custom_personalities[user_id].get('presets', {})
                
                if existing_presets:
                    # If user has presets, keep only the presets
                    self.custom_personalities[user_id] = {
                        'presets': existing_presets,
                        'reset_at': datetime.now().isoformat()
                    }
                else:
                    # If no presets, remove the user entirely
                    del self.custom_personalities[user_id]
                
                return True
            return False
        except Exception as e:
            print(f"Error resetting personality for {user_id}: {e}")
            return False
    
    def get_personality_summary(self, user_id: str) -> Optional[Dict]:
        """Get summary of user's custom personality"""
        if user_id not in self.custom_personalities:
            return None
        
        data = self.custom_personalities[user_id]
        return {
            'name': None,  # Name field removed but kept for compatibility
            'age': data.get('age'),
            'traits': data.get('traits', []),
            'interests': data.get('interests', []),
            'speaking_style': data.get('speaking_style'),
            'humor_style': data.get('humor_style'),
            'special_quirks': data.get('special_quirks'),
            'created_at': data.get('created_at'),
            'updated_at': data.get('updated_at')
        }
    
    def save_personality_preset(self, user_id: str, preset_name: str) -> bool:
        """Save current personality as a preset (max 5 presets per user)"""
        try:
            # Check if user has a custom personality to save
            if not self.has_custom_personality(user_id):
                return False
            
            # Ensure user entry exists
            if user_id not in self.custom_personalities:
                self.custom_personalities[user_id] = {}
            
            # Ensure presets dict exists
            if 'presets' not in self.custom_personalities[user_id]:
                self.custom_personalities[user_id]['presets'] = {}
            
            # Check preset limit (max 5 presets per user)
            current_presets = self.custom_personalities[user_id]['presets']
            if len(current_presets) >= 5 and preset_name not in current_presets:
                return "limit_exceeded"  # Return special code for limit exceeded
            
            # Save current personality as preset
            current_personality = self.custom_personalities[user_id].copy()
            # Remove presets and metadata from the copy to avoid nested presets
            for key in ['presets', 'reset_at', 'saved_at']:
                if key in current_personality:
                    del current_personality[key]
            
            self.custom_personalities[user_id]['presets'][preset_name] = {
                **current_personality,
                'saved_at': datetime.now().isoformat()
            }
            
            return True
        except Exception as e:
            print(f"Error saving personality preset: {e}")
            return False
    
    def load_personality_preset(self, user_id: str, preset_name: str) -> bool:
        """Load a personality preset"""
        try:
            if (user_id not in self.custom_personalities or 
                'presets' not in self.custom_personalities[user_id] or
                preset_name not in self.custom_personalities[user_id]['presets']):
                return False
            
            preset_data = self.custom_personalities[user_id]['presets'][preset_name].copy()
            # Remove saved_at timestamp
            if 'saved_at' in preset_data:
                del preset_data['saved_at']
            
            # Keep existing presets
            existing_presets = self.custom_personalities[user_id].get('presets', {})
            
            # Update personality with preset data
            self.custom_personalities[user_id] = {
                **preset_data,
                'presets': existing_presets,
                'updated_at': datetime.now().isoformat()
            }
            
            return True
        except Exception as e:
            print(f"Error loading personality preset: {e}")
            return False
    
    def delete_personality_preset(self, user_id: str, preset_name: str) -> bool:
        """Delete a personality preset"""
        try:
            if (user_id not in self.custom_personalities or 
                'presets' not in self.custom_personalities[user_id] or
                preset_name not in self.custom_personalities[user_id]['presets']):
                return False
            
            del self.custom_personalities[user_id]['presets'][preset_name]
            return True
        except Exception as e:
            print(f"Error deleting personality preset: {e}")
            return False
    
    def get_user_presets(self, user_id: str) -> Dict:
        """Get all presets for a user"""
        if (user_id not in self.custom_personalities or 
            'presets' not in self.custom_personalities[user_id]):
            return {}
        
        return self.custom_personalities[user_id]['presets']
    
    def update_personality_field(self, user_id: str, field: str, value) -> bool:
        """Update a specific field in user's personality"""
        try:
            if user_id not in self.custom_personalities:
                self.custom_personalities[user_id] = {}
            
            self.custom_personalities[user_id][field] = value
            self.custom_personalities[user_id]['updated_at'] = datetime.now().isoformat()
            
            return True
        except Exception as e:
            print(f"Error updating personality field for {user_id}: {e}")
            return False

    def get_stats(self) -> Dict:
        """Get personality customization statistics"""
        total_custom = len(self.custom_personalities)
        
        # Count personalities with different features
        with_age = sum(1 for p in self.custom_personalities.values() if p.get('age'))
        with_traits = sum(1 for p in self.custom_personalities.values() if p.get('traits'))
        with_interests = sum(1 for p in self.custom_personalities.values() if p.get('interests'))
        
        # Count presets
        total_presets = sum(len(p.get('presets', {})) for p in self.custom_personalities.values())
        
        return {
            'total_custom_personalities': total_custom,
            'with_custom_age': with_age,
            'with_custom_traits': with_traits,
            'with_custom_interests': with_interests,
            'total_presets': total_presets
        }