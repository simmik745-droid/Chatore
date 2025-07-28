"""
Emotion Detection System - Detects bot emotions and sends appropriate GIFs
"""

import re
import random

class EmotionDetector:
    def __init__(self):
        # Anger keywords and patterns (specific angry phrases)
        self.anger_keywords = [
            'extremely angry', 'really angry', 'very angry', 'so angry',
            'angry', 'mad', 'furious', 'pissed', 'annoyed', 'irritated', 'frustrated',
            'rage', 'livid', 'outraged', 'infuriated', 'enraged', 'irate',
            'wtf', 'damn', 'hell', 'shit', 'fuck', 'bloody', 'bastard',
            'stupid', 'idiot', 'moron', 'pathetic',
            'hate', 'disgusted', 'sick of', 'fed up', 'can\'t stand',
            'bsdk', 'chutiya', 'madarchod', 'bhenchod', 'saala', 'kamina'
        ]
        
        # Sadness keywords and patterns (specific sad phrases)
        self.sadness_keywords = [
            'very sad', 'deeply sad', 'extremely sad', 'really sad', 'so sad',
            'sad', 'depressed', 'heartbroken', 'crying', 'tears', 'miserable', 
            'lonely', 'empty', 'broken', 'devastated', 'crushed', 'hopeless', 
            'despair', 'grief', 'sorry', 'apologize', 'regret', 'mistake', 
            'failed', 'failure', 'down', 'blue', 'melancholy', 'gloomy', 
            'dejected', 'sed', 'rip', 'oof', 'feels bad', 'big sad', 'depression',
            'hurt', 'disappointed', 'upset'
        ]
        
        # Anger patterns (regex)
        self.anger_patterns = [
            r'\b(what|why) the (hell|fuck|damn)\b',
            r'\b(go to hell|fuck off|shut up|piss off)\b',
            r'\b(i hate|i\'m done|screw this|this sucks)\b',
            r'[!]{2,}',  # Multiple exclamation marks
            r'[A-Z]{3,}',  # ALL CAPS words
        ]
        
        # Sadness patterns (regex)
        self.sadness_patterns = [
            r'\b(i\'m sorry|so sorry|my bad|forgive me)\b',
            r'\b(feel bad|feels bad|feeling down)\b',
            r'\b(no hope|give up|can\'t do)\b',
            r'[.]{3,}',  # Multiple dots (ellipsis)
            r':\(',  # Sad emoticon
        ]
        
        # Angry GIFs (Tenor URLs)
        self.angry_gifs = [
            "https://tenor.com/view/wrath-anger-inside-out-mad-angry-gif-17632370",
            "https://tenor.com/view/jujutsu-kaisen-gif-6060784482280572901",
            "https://tenor.com/view/hulk-hulk-smash-gif-7535165216942200597",
        ]
        
        # Sad GIFs (Tenor URLs)
        self.sad_gifs = [
            "https://tenor.com/view/bee-honey-bee-gif-648090940468114108",
            "https://tenor.com/view/sad-gif-17596606390723064939",
            "https://tenor.com/view/stillesque-gif-25544126",
        ]
    
    def detect_emotion(self, text: str) -> str:
        """
        Detect emotion in text
        Returns: 'angry', 'sad', or 'neutral'
        """
        if not text:
            return 'neutral'
        
        text_lower = text.lower()
        
        # Count anger indicators
        anger_score = 0
        for keyword in self.anger_keywords:
            if keyword in text_lower:
                anger_score += 1
        
        for pattern in self.anger_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                anger_score += 1
        
        # Count sadness indicators
        sadness_score = 0
        for keyword in self.sadness_keywords:
            if keyword in text_lower:
                sadness_score += 1
        
        for pattern in self.sadness_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                sadness_score += 1
        
        # Determine emotion based on scores
        # Need at least 2 indicators for strong emotion detection
        if anger_score > sadness_score and anger_score >= 2:
            return 'angry'
        elif sadness_score > anger_score and sadness_score >= 2:
            return 'sad'
        elif anger_score == sadness_score and anger_score >= 2:
            # If tied, check for specific strong indicators
            if any(word in text_lower for word in ['furious', 'rage', 'hate', 'fucking', 'damn']):
                return 'angry'
            elif any(word in text_lower for word in ['heartbroken', 'crying', 'devastated', 'sorry']):
                return 'sad'
            else:
                return 'angry'  # Default to angry for tied scores
        else:
            return 'neutral'
    
    def get_emotion_gif(self, emotion: str) -> str:
        """
        Get a random GIF for the detected emotion
        Returns: GIF URL or None
        """
        if emotion == 'angry':
            return random.choice(self.angry_gifs)
        elif emotion == 'sad':
            return random.choice(self.sad_gifs)
        else:
            return None
    
    def should_send_gif(self, emotion: str, text: str) -> bool:
        """
        Determine if a GIF should be sent based on emotion intensity
        Rate: 1/3 chance (33%) when conditions are met
        """
        if emotion == 'neutral':
            return False
        
        # If emotion is detected (angry or sad), check for intensity
        text_lower = text.lower()
        should_send = False
        
        if emotion == 'angry':
            # Check for extreme anger indicators
            extreme_indicators = [
                'extremely angry', 'really angry', 'very angry', 'so angry',
                'fucking', 'damn', 'absolutely', 'totally', 'completely', 'utterly'
            ]
            for indicator in extreme_indicators:
                if indicator in text_lower:
                    should_send = True
                    break
            
            # Multiple caps or exclamation marks indicate intensity
            if re.search(r'[A-Z]{4,}|[!]{3,}', text):
                should_send = True
            
            # If basic anger detected but no extreme indicators, still allow with lower chance
            if not should_send and emotion == 'angry':
                should_send = True  # Let rate limiting handle it
        
        elif emotion == 'sad':
            # Check for specific sad phrases
            sad_phrases = [
                'very sad', 'deeply sad', 'extremely sad', 'really sad', 'so sad',
                'heartbroken', 'devastated', 'miserable'
            ]
            for phrase in sad_phrases:
                if phrase in text_lower:
                    should_send = True
                    break
            
            # Multiple dots or specific phrases indicate intensity
            if re.search(r'[.]{4,}|:\(|T_T|;_;', text):
                should_send = True
            
            # If basic sadness detected but no extreme indicators, still allow with lower chance
            if not should_send and emotion == 'sad':
                should_send = True  # Let rate limiting handle it
        
        # Apply 1/3 rate limiting (33% chance)
        if should_send:
            import random
            return random.random() < 0.33  # 1/3 chance
        
        return False
    
