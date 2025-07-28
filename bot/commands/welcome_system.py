"""
Welcome System - Handles new user onboarding with systematic memory collection
"""

import discord
from discord.ext import commands

class OnboardingData:
    """Class to store onboarding data during the process"""
    def __init__(self):
        self.name = None
        self.age = None
        self.hobbies = []
        self.likes = []
        self.dislikes = []
        self.occupation = None
        self.location = None
        self.additional_info = None

class NameModal(discord.ui.Modal, title="What's your name? 👋"):
    def __init__(self, bot, onboarding_data, view):
        super().__init__()
        self.bot = bot
        self.onboarding_data = onboarding_data
        self.view = view
    
    name_input = discord.ui.TextInput(
        label="Your Name",
        placeholder="What should I call you? (e.g., Alex, Sarah, etc.)",
        style=discord.TextStyle.short,
        max_length=50,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.onboarding_data.name = self.name_input.value
        
        # Move to next step
        await self.view.move_to_next_step(interaction)

class AgeModal(discord.ui.Modal, title="How old are you? 🎂"):
    def __init__(self, bot, onboarding_data, view):
        super().__init__()
        self.bot = bot
        self.onboarding_data = onboarding_data
        self.view = view
    
    age_input = discord.ui.TextInput(
        label="Your Age",
        placeholder="Enter your age (e.g., 20, 25) or leave blank to skip",
        style=discord.TextStyle.short,
        max_length=3,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        age_text = self.age_input.value.strip()
        if age_text:
            try:
                age = int(age_text)
                if 1 <= age <= 120:
                    self.onboarding_data.age = age
                else:
                    self.onboarding_data.age = None
            except ValueError:
                self.onboarding_data.age = None
        
        # Move to next step
        await self.view.move_to_next_step(interaction)

class HobbiesModal(discord.ui.Modal, title="What are your hobbies? 🎮"):
    def __init__(self, bot, onboarding_data, view):
        super().__init__()
        self.bot = bot
        self.onboarding_data = onboarding_data
        self.view = view
    
    hobbies_input = discord.ui.TextInput(
        label="Your Hobbies",
        placeholder="Gaming, reading, coding, music, sports, art, etc.",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        hobbies_text = self.hobbies_input.value.strip()
        if hobbies_text:
            # Split by common separators and clean up
            hobbies = [h.strip() for h in hobbies_text.replace(',', '\n').replace(';', '\n').split('\n') if h.strip()]
            self.onboarding_data.hobbies = hobbies[:10]  # Limit to 10 hobbies
        
        # Move to next step
        await self.view.move_to_next_step(interaction)

class LikesModal(discord.ui.Modal, title="What do you like? ❤️"):
    def __init__(self, bot, onboarding_data, view):
        super().__init__()
        self.bot = bot
        self.onboarding_data = onboarding_data
        self.view = view
    
    likes_input = discord.ui.TextInput(
        label="Things You Like",
        placeholder="Pizza, movies, anime, technology, travel, etc.",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        likes_text = self.likes_input.value.strip()
        if likes_text:
            likes = [l.strip() for l in likes_text.replace(',', '\n').replace(';', '\n').split('\n') if l.strip()]
            self.onboarding_data.likes = likes[:10]  # Limit to 10 likes
        
        # Move to next step
        await self.view.move_to_next_step(interaction)

class OccupationModal(discord.ui.Modal, title="What do you do? 💼"):
    def __init__(self, bot, onboarding_data, view):
        super().__init__()
        self.bot = bot
        self.onboarding_data = onboarding_data
        self.view = view
    
    occupation_input = discord.ui.TextInput(
        label="Your Occupation/Status",
        placeholder="Student, Developer, Teacher, Gamer, etc. (or skip)",
        style=discord.TextStyle.short,
        max_length=100,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        occupation_text = self.occupation_input.value.strip()
        if occupation_text:
            self.onboarding_data.occupation = occupation_text
        
        # Move to next step
        await self.view.move_to_next_step(interaction)

class AdditionalInfoModal(discord.ui.Modal, title="Anything else? 💭"):
    def __init__(self, bot, onboarding_data, view):
        super().__init__()
        self.bot = bot
        self.onboarding_data = onboarding_data
        self.view = view
    
    additional_input = discord.ui.TextInput(
        label="Additional Information",
        placeholder="Anything else you'd like me to know about you?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        additional_text = self.additional_input.value.strip()
        if additional_text:
            self.onboarding_data.additional_info = additional_text
        
        # Complete onboarding
        await self.view.complete_onboarding(interaction)

class OnboardingView(discord.ui.View):
    def __init__(self, bot, original_user_id, user=None):
        super().__init__(timeout=30)  # 30 second timeout
        self.message = None  # Store message for timeout updates
        self.bot = bot
        self.original_user_id = original_user_id
        self.user = user or bot.get_user(int(original_user_id))
        self.onboarding_data = OnboardingData()
        self.current_step = "welcome"
        self.setup_buttons()
    
    def check_user(self, interaction: discord.Interaction) -> bool:
        """Check if this is the original user"""
        if str(interaction.user.id) != str(self.original_user_id):
            return False
        return True
    
    def get_welcome_embed(self) -> discord.Embed:
        """Initial welcome embed"""
        language = self.bot.memory.get_user_language(str(self.original_user_id))
        user_name = self.user.display_name if self.user else "Friend"
        
        if language == 'hinglish':
            embed = discord.Embed(
                title="🎉 Namaste! Welcome to Chatore!",
                description=f"Hey {user_name}! Main Chatore hun, tera AI dost! 🤖\n\nTujhe better jaanne ke liye, main step by step kuch sawal puchunga. Ready hai?",
                color=0x7289DA
            )
            embed.add_field(
                name="📝 Kya hoga?",
                value="• Tera naam\n• Age (optional)\n• Hobbies aur interests\n• Likes/dislikes\n• Occupation\n• Aur kuch bhi jo tu batana chahe!",
                inline=False
            )
            embed.add_field(
                name="⏱️ Time lagega?",
                value="Bas 2-3 minutes! Aur tu koi bhi step skip kar sakta hai.",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="🎉 Welcome to Chatore!",
                description=f"Hey {user_name}! I'm Chatore, your AI companion! 🤖\n\nTo get to know you better, I'll ask you a few questions step by step. Ready?",
                color=0x7289DA
            )
            embed.add_field(
                name="📝 What we'll cover:",
                value="• Your name\n• Age (optional)\n• Hobbies & interests\n• Things you like\n• Your occupation\n• Anything else you'd like to share!",
                inline=False
            )
            embed.add_field(
                name="⏱️ How long?",
                value="Just 2-3 minutes! You can skip any step you want.",
                inline=False
            )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Click 'Let's Start!' to begin • Timeout: 10 minutes")
        return embed
    
    def get_age_embed(self) -> discord.Embed:
        """Age collection embed"""
        language = self.bot.memory.get_user_language(str(self.original_user_id))
        
        if language == 'hinglish':
            embed = discord.Embed(
                title=f"👋 Nice to meet you, {self.onboarding_data.name}!",
                description="Ab bata, tera age kya hai? (Optional hai, skip kar sakta hai)",
                color=0x9B59B6
            )
            embed.add_field(
                name="🎂 Age batane se kya fayda?",
                value="Main age-appropriate responses de sakta hun aur better understand kar sakta hun teri preferences.",
                inline=False
            )
        else:
            embed = discord.Embed(
                title=f"👋 Nice to meet you, {self.onboarding_data.name}!",
                description="Now, what's your age? (This is optional, you can skip it)",
                color=0x9B59B6
            )
            embed.add_field(
                name="🎂 Why age matters?",
                value="I can give age-appropriate responses and better understand your preferences.",
                inline=False
            )
        
        embed.set_footer(text="Step 2/6 • Click 'Enter Age' or 'Skip' to continue")
        return embed
    
    def get_hobbies_embed(self) -> discord.Embed:
        """Hobbies collection embed"""
        language = self.bot.memory.get_user_language(str(self.original_user_id))
        
        age_text = f" ({self.onboarding_data.age} years old)" if self.onboarding_data.age else ""
        
        if language == 'hinglish':
            embed = discord.Embed(
                title=f"🎮 Cool, {self.onboarding_data.name}{age_text}!",
                description="Ab bata, tere hobbies kya hai? Gaming, coding, music, sports - jo bhi pasand hai!",
                color=0x00FF7F
            )
            embed.add_field(
                name="💡 Examples:",
                value="Gaming, reading, coding, music, sports, art, cooking, traveling, photography, etc.",
                inline=False
            )
        else:
            embed = discord.Embed(
                title=f"🎮 Cool, {self.onboarding_data.name}{age_text}!",
                description="What are your hobbies? Gaming, coding, music, sports - whatever you enjoy!",
                color=0x00FF7F
            )
            embed.add_field(
                name="💡 Examples:",
                value="Gaming, reading, coding, music, sports, art, cooking, traveling, photography, etc.",
                inline=False
            )
        
        embed.set_footer(text="Step 3/6 • Click 'Add Hobbies' or 'Skip' to continue")
        return embed
    
    def get_likes_embed(self) -> discord.Embed:
        """Likes collection embed"""
        language = self.bot.memory.get_user_language(str(self.original_user_id))
        
        hobbies_text = ", ".join(self.onboarding_data.hobbies[:3]) if self.onboarding_data.hobbies else "various things"
        
        if language == 'hinglish':
            embed = discord.Embed(
                title=f"❤️ {hobbies_text} - nice choices!",
                description="Ab bata, tujhe aur kya pasand hai? Food, movies, games, technology - kuch bhi!",
                color=0xE91E63
            )
            embed.add_field(
                name="💡 Examples:",
                value="Pizza, anime, Marvel movies, technology, memes, cats, coffee, etc.",
                inline=False
            )
        else:
            embed = discord.Embed(
                title=f"❤️ {hobbies_text} - nice choices!",
                description="What else do you like? Food, movies, games, technology - anything!",
                color=0xE91E63
            )
            embed.add_field(
                name="💡 Examples:",
                value="Pizza, anime, Marvel movies, technology, memes, cats, coffee, etc.",
                inline=False
            )
        
        embed.set_footer(text="Step 4/6 • Click 'Add Likes' or 'Skip' to continue")
        return embed
    
    def get_occupation_embed(self) -> discord.Embed:
        """Occupation collection embed"""
        language = self.bot.memory.get_user_language(str(self.original_user_id))
        
        if language == 'hinglish':
            embed = discord.Embed(
                title="💼 Almost done!",
                description="Tu kya karta hai? Student hai, job karta hai, ya kuch aur?",
                color=0xFF9933
            )
            embed.add_field(
                name="💡 Examples:",
                value="Student, Software Developer, Teacher, Gamer, Artist, Engineer, etc.",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="💼 Almost done!",
                description="What do you do? Are you a student, working, or something else?",
                color=0xFF9933
            )
            embed.add_field(
                name="💡 Examples:",
                value="Student, Software Developer, Teacher, Gamer, Artist, Engineer, etc.",
                inline=False
            )
        
        embed.set_footer(text="Step 5/6 • Click 'Add Occupation' or 'Skip' to continue")
        return embed
    
    def get_final_embed(self) -> discord.Embed:
        """Final step embed"""
        language = self.bot.memory.get_user_language(str(self.original_user_id))
        
        if language == 'hinglish':
            embed = discord.Embed(
                title="🎯 Last step!",
                description="Kuch aur hai jo tu mujhe batana chahta hai? Koi special thing, preference, ya kuch bhi!",
                color=0x5865F2
            )
            embed.add_field(
                name="💭 Optional hai!",
                value="Agar kuch nahi hai toh direct 'Finish' kar sakta hai.",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="🎯 Last step!",
                description="Anything else you'd like me to know? Any special preferences or information!",
                color=0x5865F2
            )
            embed.add_field(
                name="💭 This is optional!",
                value="If there's nothing else, you can directly click 'Finish Setup'.",
                inline=False
            )
        
        embed.set_footer(text="Step 6/6 • Click 'Add More Info' or 'Finish Setup'")
        return embed
    
    async def complete_onboarding(self, interaction: discord.Interaction):
        """Complete the onboarding process and save all data"""
        user_id = str(interaction.user.id)
        
        # Build comprehensive memory string
        memory_parts = []
        
        if self.onboarding_data.name:
            memory_parts.append(f"Name: {self.onboarding_data.name}")
        
        if self.onboarding_data.age:
            memory_parts.append(f"Age: {self.onboarding_data.age} years old")
        
        if self.onboarding_data.occupation:
            memory_parts.append(f"Occupation: {self.onboarding_data.occupation}")
        
        if self.onboarding_data.hobbies:
            memory_parts.append(f"Hobbies: {', '.join(self.onboarding_data.hobbies)}")
        
        if self.onboarding_data.likes:
            memory_parts.append(f"Likes: {', '.join(self.onboarding_data.likes)}")
        
        if self.onboarding_data.additional_info:
            memory_parts.append(f"Additional info: {self.onboarding_data.additional_info}")
        
        # Save comprehensive memory
        full_memory = " | ".join(memory_parts)
        self.bot.memory.add_user_memory(user_id, full_memory)
        await self.bot.memory.save_memory()
        
        # Create completion embed
        language = self.bot.memory.get_user_language(user_id)
        
        if language == 'hinglish':
            embed = discord.Embed(
                title="🎉 Setup Complete! Welcome to the family!",
                description=f"Arrey waah, {self.onboarding_data.name or (self.user.display_name if self.user else 'Friend')}! Ab main tujhe acche se jaanta hun!",
                color=0x00FF7F
            )
            embed.add_field(
                name="📝 Maine ye sab yaad rakha hai:",
                value=self.format_saved_info(),
                inline=False
            )
            embed.add_field(
                name="🚀 Ab kya?",
                value="• Bas mention kar (@Chatore) ya DM kar - main samjh jaunga!\n• `/help` dekh ke aur commands explore kar\n• `/language` se language change kar sakta hai\n• Chill kar aur maje kar! 🎮",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="🎉 Setup Complete! Welcome to the family!",
                description=f"Awesome, {self.onboarding_data.name or (self.user.display_name if self.user else 'Friend')}! Now I know you much better!",
                color=0x00FF7F
            )
            embed.add_field(
                name="📝 Here's what I'll remember:",
                value=self.format_saved_info(),
                inline=False
            )
            embed.add_field(
                name="🚀 What's next?",
                value="• Just mention me (@Chatore) or DM me - I'll understand!\n• Check out `/help` for more commands\n• Use `/language` to switch between English/Hinglish\n• Have fun chatting! 🎮",
                inline=False
            )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Let's start our conversation journey! 🚀")
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    def format_saved_info(self) -> str:
        """Format the saved information for display"""
        info_parts = []
        
        if self.onboarding_data.name:
            info_parts.append(f"**Name:** {self.onboarding_data.name}")
        
        if self.onboarding_data.age:
            info_parts.append(f"**Age:** {self.onboarding_data.age}")
        
        if self.onboarding_data.occupation:
            info_parts.append(f"**Occupation:** {self.onboarding_data.occupation}")
        
        if self.onboarding_data.hobbies:
            info_parts.append(f"**Hobbies:** {', '.join(self.onboarding_data.hobbies[:5])}")
        
        if self.onboarding_data.likes:
            info_parts.append(f"**Likes:** {', '.join(self.onboarding_data.likes[:5])}")
        
        if self.onboarding_data.additional_info:
            info_parts.append(f"**Extra:** {self.onboarding_data.additional_info[:100]}...")
        
        return "\n".join(info_parts) if info_parts else "Basic profile information"
    
    def setup_buttons(self):
        """Setup buttons based on current step"""
        self.clear_items()
        
        if self.current_step == "welcome":
            button = discord.ui.Button(
                label="Let's Start!",
                emoji="🚀",
                style=discord.ButtonStyle.primary,
                custom_id="start"
            )
            button.callback = self.start_callback
            self.add_item(button)
        
        elif self.current_step == "name":
            button = discord.ui.Button(
                label="Enter Name",
                emoji="👋",
                style=discord.ButtonStyle.primary,
                custom_id="name"
            )
            button.callback = self.name_callback
            self.add_item(button)
        
        elif self.current_step == "age":
            button = discord.ui.Button(
                label="Enter Age",
                emoji="🎂",
                style=discord.ButtonStyle.primary,
                custom_id="age"
            )
            button.callback = self.age_callback
            self.add_item(button)
            
            skip_button = discord.ui.Button(
                label="Skip",
                emoji="⏭️",
                style=discord.ButtonStyle.secondary,
                custom_id="skip"
            )
            skip_button.callback = self.skip_callback
            self.add_item(skip_button)
        
        elif self.current_step == "hobbies":
            button = discord.ui.Button(
                label="Add Hobbies",
                emoji="🎮",
                style=discord.ButtonStyle.primary,
                custom_id="hobbies"
            )
            button.callback = self.hobbies_callback
            self.add_item(button)
            
            skip_button = discord.ui.Button(
                label="Skip",
                emoji="⏭️",
                style=discord.ButtonStyle.secondary,
                custom_id="skip"
            )
            skip_button.callback = self.skip_callback
            self.add_item(skip_button)
        
        elif self.current_step == "likes":
            button = discord.ui.Button(
                label="Add Likes",
                emoji="❤️",
                style=discord.ButtonStyle.primary,
                custom_id="likes"
            )
            button.callback = self.likes_callback
            self.add_item(button)
            
            skip_button = discord.ui.Button(
                label="Skip",
                emoji="⏭️",
                style=discord.ButtonStyle.secondary,
                custom_id="skip"
            )
            skip_button.callback = self.skip_callback
            self.add_item(skip_button)
        
        elif self.current_step == "occupation":
            button = discord.ui.Button(
                label="Add Occupation",
                emoji="💼",
                style=discord.ButtonStyle.primary,
                custom_id="occupation"
            )
            button.callback = self.occupation_callback
            self.add_item(button)
            
            skip_button = discord.ui.Button(
                label="Skip",
                emoji="⏭️",
                style=discord.ButtonStyle.secondary,
                custom_id="skip"
            )
            skip_button.callback = self.skip_callback
            self.add_item(skip_button)
        
        elif self.current_step == "additional":
            button = discord.ui.Button(
                label="Add More Info",
                emoji="💭",
                style=discord.ButtonStyle.primary,
                custom_id="additional"
            )
            button.callback = self.additional_callback
            self.add_item(button)
            
            finish_button = discord.ui.Button(
                label="Finish Setup",
                emoji="✅",
                style=discord.ButtonStyle.success,
                custom_id="finish"
            )
            finish_button.callback = self.finish_callback
            self.add_item(finish_button)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if user can interact with this view"""
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you! Mention me to get your own.", ephemeral=True)
            return False
        return True
    
    # Button callback methods
    async def start_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you! Mention me to get your own.", ephemeral=True)
            return
        
        self.current_step = "name"
        embed = self.get_name_embed()
        self.setup_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def name_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you!", ephemeral=True)
            return
        
        modal = NameModal(self.bot, self.onboarding_data, self)
        await interaction.response.send_modal(modal)
    
    async def age_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you!", ephemeral=True)
            return
        
        modal = AgeModal(self.bot, self.onboarding_data, self)
        await interaction.response.send_modal(modal)
    
    async def hobbies_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you!", ephemeral=True)
            return
        
        modal = HobbiesModal(self.bot, self.onboarding_data, self)
        await interaction.response.send_modal(modal)
    
    async def likes_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you!", ephemeral=True)
            return
        
        modal = LikesModal(self.bot, self.onboarding_data, self)
        await interaction.response.send_modal(modal)
    
    async def occupation_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you!", ephemeral=True)
            return
        
        modal = OccupationModal(self.bot, self.onboarding_data, self)
        await interaction.response.send_modal(modal)
    
    async def additional_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you!", ephemeral=True)
            return
        
        modal = AdditionalInfoModal(self.bot, self.onboarding_data, self)
        await interaction.response.send_modal(modal)
    
    async def skip_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you!", ephemeral=True)
            return
        
        await self.skip_current_step(interaction)
    
    async def finish_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This onboarding is not for you!", ephemeral=True)
            return
        
        await self.complete_onboarding(interaction)
    
    def get_name_embed(self) -> discord.Embed:
        """Name collection embed"""
        language = self.bot.memory.get_user_language(str(self.original_user_id))
        user_name = self.user.display_name if self.user else "Friend"
        
        if language == 'hinglish':
            embed = discord.Embed(
                title="👋 Let's get to know you!",
                description=f"Pehle bata, tera naam kya hai? Main tujhe kya bulau?",
                color=0x9B59B6
            )
            embed.add_field(
                name="💡 Kyun zaroori hai?",
                value="Naam se main tujhe personally address kar sakta hun aur better conversation ho sakti hai.",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="👋 Let's get to know you!",
                description="First, what's your name? What should I call you?",
                color=0x9B59B6
            )
            embed.add_field(
                name="💡 Why is this important?",
                value="With your name, I can address you personally and have better conversations.",
                inline=False
            )
        
        embed.set_footer(text="Step 1/6 • Click 'Enter Name' to continue")
        return embed
    
    async def skip_current_step(self, interaction: discord.Interaction):
        """Skip the current step and move to next"""
        if self.current_step == "age":
            self.current_step = "hobbies"
            embed = self.get_hobbies_embed()
        elif self.current_step == "hobbies":
            self.current_step = "likes"
            embed = self.get_likes_embed()
        elif self.current_step == "likes":
            self.current_step = "occupation"
            embed = self.get_occupation_embed()
        elif self.current_step == "occupation":
            self.current_step = "additional"
            embed = self.get_final_embed()
        else:
            await self.complete_onboarding(interaction)
            return
        
        self.setup_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def move_to_next_step(self, interaction: discord.Interaction):
        """Move to the next step after completing current one"""
        if self.current_step == "name":
            self.current_step = "age"
            embed = self.get_age_embed()
        elif self.current_step == "age":
            self.current_step = "hobbies"
            embed = self.get_hobbies_embed()
        elif self.current_step == "hobbies":
            self.current_step = "likes"
            embed = self.get_likes_embed()
        elif self.current_step == "likes":
            self.current_step = "occupation"
            embed = self.get_occupation_embed()
        elif self.current_step == "occupation":
            self.current_step = "additional"
            embed = self.get_final_embed()
        else:
            await self.complete_onboarding(interaction)
            return
        
        self.setup_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    

    
    async def on_timeout(self):
        # Disable all buttons when timeout occurs
        for item in self.children:
            item.disabled = True
    
    async def on_timeout(self):
        """Handle timeout - disable all components and update message"""
        for item in self.children:
            item.disabled = True
        
        # Create timeout embed
        embed = discord.Embed(
            title="⏰ Welcome Menu Timed Out",
            description="This welcome menu has expired after 30 seconds of inactivity.",
            color=0x95A5A6
        )
        embed.add_field(
            name="💡 Getting Started",
            value="You can start chatting with me anytime by mentioning me or using `/help`!",
            inline=False
        )
        embed.set_footer(text="Welcome to Chatore! Start chatting anytime.")
        
        # Try to edit the message to show timeout
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except (discord.NotFound, discord.Forbidden, Exception):
                pass

def create_welcome_embed(bot, user: discord.User) -> discord.Embed:
    """Create the initial welcome embed for new users"""
    view = OnboardingView(bot, user.id, user)
    return view.get_welcome_embed()

class WelcomeView(discord.ui.View):
    """Wrapper class for compatibility"""
    def __init__(self, bot, original_user_id, user=None):
        super().__init__(timeout=600)
        self.onboarding_view = OnboardingView(bot, original_user_id, user)
        # Copy all items from onboarding view
        for item in self.onboarding_view.children:
            self.add_item(item)

def setup(bot):
    """Setup welcome system - this is called from the main bot file"""
    pass  # No commands to register, just utility functions