"""
Luna Bot - Main bot class and core functionality
"""

import discord
from discord.ext import commands
from discord import app_commands
import google.generativeai as genai
import os
import asyncio
from datetime import datetime

from .memory.memory_manager import MemoryManager
from .utils.emotion_detector import EmotionDetector
from .utils.tier_manager import TierManager
from .utils.personality_manager import PersonalityManager
from .commands import chat_commands, utility_commands, help_commands, language_commands, welcome_system, owner_commands, subscription_commands

# Configure Gemini with fallback API keys
GEMINI_API_KEYS = [
    os.getenv('GEMINI_API_KEY'),
    os.getenv('GEMINI_API_KEY_2'),
    os.getenv('GEMINI_API_KEY_3'),
    os.getenv('GEMINI_API_KEY_4'),
    os.getenv('GEMINI_API_KEY_5'),
]

# Filter out None values
GEMINI_API_KEYS = [key for key in GEMINI_API_KEYS if key is not None]

if not GEMINI_API_KEYS:
    print("❌ No Gemini API keys found! Please set GEMINI_API_KEY in .env file")
    exit(1)

# Configure with primary key initially
genai.configure(api_key=GEMINI_API_KEYS[0])
print(f"🔑 Loaded {len(GEMINI_API_KEYS)} Gemini API key(s)")

class LunaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents, help_command=None)
        
        self.memory = MemoryManager()
        self.tier_manager = TierManager()
        self.tier_manager.set_bot_instance(self)  # Set bot instance for DM sending
        self.personality_manager = PersonalityManager()
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.current_api_key_index = 0
        self.api_keys = GEMINI_API_KEYS
        self.emotion_detector = EmotionDetector()
        
        # Bot personalities for different languages
        self.personalities = {
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
        
        # Load commands
        self.setup_commands()
    
    def get_personality(self, user_id: str) -> str:
        """Get personality based on user's language preference and custom settings"""
        language = self.memory.get_user_language(user_id)
        
        # Check if user has premium tier and custom personality
        tier = self.tier_manager.get_user_tier(user_id)
        if tier == 'premium' and self.personality_manager.has_custom_personality(user_id):
            return self.personality_manager.get_personality(user_id, language)
        
        # Return default personality
        return self.personalities.get(language, self.personalities['english'])
    
    def format_response(self, response: str) -> str:
        """Format response to be concise and avoid unnecessary line breaks"""
        # Remove any existing \n characters that might be in the AI response
        response = response.replace('\\n', ' ').replace('\n', ' ')
        
        # Clean up extra spaces
        response = ' '.join(response.split())
        
        # If response is short (under 60 characters), return as is
        if len(response) <= 60:
            return response
        
        # For longer responses, split into max 2 lines only
        words = response.split()
        if len(words) <= 15:  # Short enough for one line
            return response
        
        # Split into 2 lines maximum
        mid_point = len(words) // 2
        line1 = ' '.join(words[:mid_point])
        line2 = ' '.join(words[mid_point:])
        
        # Make sure neither line is too long
        if len(line1) > 80:
            # Find a better split point
            for i in range(mid_point - 3, mid_point + 3):
                if i > 0 and i < len(words):
                    test_line1 = ' '.join(words[:i])
                    if len(test_line1) <= 80:
                        line1 = test_line1
                        line2 = ' '.join(words[i:])
                        break
        
        return f"{line1}\n{line2}"
    
    async def handle_new_user_welcome(self, message):
        """Handle welcome message for new users"""
        from .commands.welcome_system import create_welcome_embed, OnboardingView
        
        try:
            embed = create_welcome_embed(self, message.author)
            view = OnboardingView(self, message.author.id, message.author)
            
            welcome_message = await message.reply(embed=embed, view=view)
            view.message = welcome_message
            
        except Exception as e:
            print(f"Error in new user welcome: {e}")
            # Fallback to normal AI response if welcome fails
            await self.handle_ai_response(message)
    
    async def check_and_welcome_new_user(self, interaction: discord.Interaction):
        """Check if user is new and show welcome message (for slash commands)"""
        from .commands.welcome_system import create_welcome_embed, OnboardingView
        
        try:
            # Skip welcome for help command
            if interaction.command and interaction.command.name == "help":
                return
            
            user_id = str(interaction.user.id)
            if self.memory.is_new_user(user_id):
                # Update user activity to mark them as no longer new
                self.memory.update_user_activity(user_id)
                
                embed = create_welcome_embed(self, interaction.user)
                view = OnboardingView(self, interaction.user.id, interaction.user)
                
                welcome_message = await interaction.followup.send(embed=embed, view=view)
                view.message = welcome_message
            
        except Exception as e:
            print(f"Error in new user welcome: {e}")
    
    async def periodic_memory_cleanup(self):
        """Periodic task to cleanup inactive users' memory every hour"""
        while not self.is_closed():
            try:
                await asyncio.sleep(3600)  # Wait 1 hour (3600 seconds)
                
                # Cleanup inactive users
                cleaned_users = self.memory.cleanup_all_inactive_users()
                
                if cleaned_users:
                    print(f"Cleaned up memory for {len(cleaned_users)} inactive users")
                    await self.memory.save_memory()
                
            except Exception as e:
                print(f"Error in periodic memory cleanup: {e}")
                await asyncio.sleep(3600)  # Continue the loop even if there's an error
    
    def setup_commands(self):
        """Load all command modules"""
        chat_commands.setup(self)
        utility_commands.setup(self)
        help_commands.setup(self)
        language_commands.setup(self)
        welcome_system.setup(self)
        owner_commands.setup(self)
        subscription_commands.setup(self)
    
    async def on_ready(self):
        print(f'{self.user} has landed! 🚀')
        await self.change_presence(activity=discord.Game(name="Chatting with humans! 💬"))
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash command(s)")
        except Exception as e:
            print(f"❌ Failed to sync slash commands: {e}")
        
        # Set up error handler for slash commands
        async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
            print(f"Slash command error: {error}")
            if not interaction.response.is_done():
                await interaction.response.send_message("An error occurred while processing your command.", ephemeral=True)
        
        self.tree.on_error = on_app_command_error
        
        # Start periodic memory cleanup task
        self.loop.create_task(self.periodic_memory_cleanup())
    
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        # Check if this is a new user before processing commands
        user_id = str(message.author.id)
        is_new_user = self.memory.is_new_user(user_id)
        
        # Process commands first
        await self.process_commands(message)
        
        # If message mentions the bot or is a DM, respond with AI
        if self.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
            # Update user activity for any interaction
            self.memory.update_user_activity(user_id)
            
            # Check if this is a new user
            if is_new_user:
                await self.handle_new_user_welcome(message)
            else:
                await self.handle_ai_response(message)
    
    async def handle_ai_response(self, message):
        """Handle AI-powered responses with rate limiting"""
        try:
            user_id = str(message.author.id)
            
            # Check rate limits
            can_request, usage_info = self.tier_manager.can_make_request(user_id)
            
            if not can_request:
                # Rate limit exceeded
                tier = usage_info['tier']
                reset_time = datetime.fromisoformat(usage_info['resets_at'])
                hours_until_reset = (reset_time - datetime.now()).total_seconds() / 3600
                
                embed = discord.Embed(
                    title="⏰ Rate Limit Reached",
                    description=f"You've reached your {tier} tier limit of {usage_info['limit']} requests per 12 hours.",
                    color=0xFF9933
                )
                
                embed.add_field(
                    name="📊 Your Usage",
                    value=f"**Used**: {usage_info['current_usage']}/{usage_info['limit']} requests\n**Resets in**: {hours_until_reset:.1f} hours",
                    inline=False
                )
                
                if tier == 'free':
                    embed.add_field(
                        name="⭐ Upgrade to Premium",
                        value="Get 200 requests per 12 hours with Premium!\nUse `/subscribe` to upgrade.",
                        inline=False
                    )
                
                embed.set_footer(text="Use /plan to check your current usage")
                await message.reply(embed=embed)
                return
            
            # Show typing indicator
            async with message.channel.typing():
                user_message = message.content.replace(f'<@{self.user.id}>', '').strip()
                
                # Get user context with tier-based limit
                context = self.memory.get_user_context(user_id, self.tier_manager.get_context_limit(user_id))
                
                # Get user's personality based on language preference
                personality = self.get_personality(user_id)
                
                # Create prompt
                prompt = f"""
                {personality}
                
                {context}
                
                The user just said: "{user_message}"
                
                Respond as Chatore in a natural, conversational way. CRITICAL RULES:
                - Keep responses to 15-20 words maximum
                - NEVER use \\n or line breaks in your response
                - Be extremely concise and punchy
                - One short sentence or two very short ones
                - Don't always greet them or use their name unless it feels natural
                - Avoid long explanations - keep it brief and casual
                """
                
                # Generate response
                response = await self.generate_response(prompt)
                
                # Format response and ensure it's not too long
                formatted_response = self.format_response(response)
                
                # Final check: ensure max 3 lines and reasonable length
                lines = formatted_response.split('\n')
                if len(lines) > 2:  # Max 2 lines (0 and 1 index)
                    formatted_response = '\n'.join(lines[:2])
                
                # If still too long, truncate
                if len(formatted_response) > 120:
                    formatted_response = formatted_response[:117] + "..."
                
                # Send simple text response (no embed for normal chat)
                await message.reply(formatted_response)
                
                # Check for extreme emotions and send GIF if needed
                await self.handle_emotion_response(message, response)
                
                # Increment usage counter
                self.tier_manager.increment_usage(user_id)
                await self.tier_manager.save_tiers()
                
                # Save message to conversation history
                self.memory.add_message_to_history(user_id, user_message, response)
                await self.memory.save_memory()
                
        except Exception as e:
            error_embed = discord.Embed(
                title="Oops! 😅",
                description="Something went wrong while processing your message. Try again in a moment!",
                color=0xFF6B6B
            )
            await message.reply(embed=error_embed)
            print(f"Error in AI response: {e}")
    
    async def handle_emotion_response(self, message, bot_response: str):
        """Handle emotion detection and send GIFs for extreme emotions"""
        try:
            # Detect emotion in bot's response
            emotion = self.emotion_detector.detect_emotion(bot_response)
            
            # Check if we should send a GIF for this emotion (1/3 chance)
            if self.emotion_detector.should_send_gif(emotion, bot_response):
                # Get appropriate GIF
                gif_url = self.emotion_detector.get_emotion_gif(emotion)
                
                if gif_url:
                    # Send only the GIF URL (no text message)
                    await message.channel.send(gif_url)
                    
        except Exception as e:
            # Don't let emotion detection errors break the main flow
            print(f"Error in emotion detection: {e}")
    
    async def switch_api_key(self):
        """Switch to next available API key"""
        if len(self.api_keys) <= 1:
            return False
        
        self.current_api_key_index = (self.current_api_key_index + 1) % len(self.api_keys)
        new_key = self.api_keys[self.current_api_key_index]
        
        try:
            genai.configure(api_key=new_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            print(f"🔄 Switched to API key #{self.current_api_key_index + 1}")
            return True
        except Exception as e:
            print(f"❌ Failed to switch API key: {e}")
            return False
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini with fallback API keys"""
        last_error = None
        
        # Try all available API keys
        for attempt in range(len(self.api_keys)):
            try:
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    prompt
                )
                return response.text
                
            except Exception as e:
                last_error = e
                print(f"❌ Gemini API error with key #{self.current_api_key_index + 1}: {e}")
                
                # If we have more keys to try, switch to next one
                if attempt < len(self.api_keys) - 1:
                    if await self.switch_api_key():
                        print(f"🔄 Trying with backup API key...")
                        continue
                    else:
                        break
                else:
                    print("❌ All API keys exhausted")
                    break
        
        # If all keys failed, return error message
        print(f"❌ All Gemini API keys failed. Last error: {last_error}")
        return "Sorry, I'm having trouble with my AI brain right now! 🤔 Please try again in a moment."
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        if isinstance(error, commands.CommandNotFound):
            embed = discord.Embed(
                title="Unknown Command 🤔",
                description="I don't know that command! Use `/help` to see what I can do.",
                color=0xFF6B6B
            )
            await ctx.reply(embed=embed)
        else:
            embed = discord.Embed(
                title="Something went wrong! 😅",
                description="There was an error processing your command. Try again!",
                color=0xFF6B6B
            )
            await ctx.reply(embed=embed)
            print(f"Command error: {error}")