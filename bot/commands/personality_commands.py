"""
Personality Commands - Custom personality system for premium users
"""

import discord
from discord.ext import commands
from discord import app_commands

class PersonalityData:
    """Class to store personality customization data during the process"""
    def __init__(self):
        self.age = None
        self.traits = []
        self.interests = []
        self.speaking_style = None
        self.humor_style = None
        self.special_quirks = None

class PersonalityNameModal(discord.ui.Modal, title="Bot's Name & Identity"):
    def __init__(self, bot, personality_data, view):
        super().__init__()
        self.bot = bot
        self.personality_data = personality_data
        self.view = view
    
    name_input = discord.ui.TextInput(
        label="Bot's Name/Identity",
        placeholder="What should I call myself? (e.g., Alex, Luna, etc.) - Optional",
        style=discord.TextStyle.short,
        max_length=50,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        name_text = self.name_input.value.strip()
        if name_text:
            self.personality_data.name = name_text
        
        # Move to next step
        await self.view.move_to_next_step(interaction)

class PersonalityAgeModal(discord.ui.Modal, title="Bot's Age/Maturity"):
    def __init__(self, bot, personality_data, view):
        super().__init__()
        self.bot = bot
        self.personality_data = personality_data
        self.view = view
    
    age_input = discord.ui.TextInput(
        label="Bot's Age/Maturity Level",
        placeholder="How old should I act? (e.g., 20, 25) - Optional",
        style=discord.TextStyle.short,
        max_length=3,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        age_text = self.age_input.value.strip()
        if age_text:
            try:
                age = int(age_text)
                if 13 <= age <= 100:  # Reasonable age range
                    self.personality_data.age = age
            except ValueError:
                pass  # Invalid age, skip
        
        # Acknowledge the modal submission first
        await interaction.response.defer()
        
        # Move to next step
        await self.view.move_to_next_step_after_modal(interaction)

class PersonalityTraitsModal(discord.ui.Modal, title="Personality Traits"):
    def __init__(self, bot, personality_data, view):
        super().__init__()
        self.bot = bot
        self.personality_data = personality_data
        self.view = view
    
    traits_input = discord.ui.TextInput(
        label="Personality Traits",
        placeholder="How should I behave? (e.g., funny, sarcastic, supportive, energetic)",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        traits_text = self.traits_input.value.strip()
        if traits_text:
            # Split by common separators and clean up
            traits = [t.strip() for t in traits_text.replace(',', '\n').replace(';', '\n').split('\n') if t.strip()]
            self.personality_data.traits = traits[:8]  # Limit to 8 traits
        
        # Acknowledge the modal submission first
        await interaction.response.defer()
        
        # Move to next step
        await self.view.move_to_next_step_after_modal(interaction)

class PersonalityInterestsModal(discord.ui.Modal, title="Interests & Knowledge"):
    def __init__(self, bot, personality_data, view):
        super().__init__()
        self.bot = bot
        self.personality_data = personality_data
        self.view = view
    
    interests_input = discord.ui.TextInput(
        label="Interests & Areas of Knowledge",
        placeholder="What should I be passionate about? (e.g., anime, coding, music, sports)",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        interests_text = self.interests_input.value.strip()
        if interests_text:
            interests = [i.strip() for i in interests_text.replace(',', '\n').replace(';', '\n').split('\n') if i.strip()]
            self.personality_data.interests = interests[:8]  # Limit to 8 interests
        
        # Acknowledge the modal submission first
        await interaction.response.defer()
        
        # Move to next step
        await self.view.move_to_next_step_after_modal(interaction)

class PersonalitySpeakingModal(discord.ui.Modal, title="Speaking Style"):
    def __init__(self, bot, personality_data, view):
        super().__init__()
        self.bot = bot
        self.personality_data = personality_data
        self.view = view
    
    speaking_input = discord.ui.TextInput(
        label="Speaking Style",
        placeholder="How should I talk? (e.g., casual, formal, street slang, professional)",
        style=discord.TextStyle.short,
        max_length=100,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        speaking_text = self.speaking_input.value.strip()
        if speaking_text:
            self.personality_data.speaking_style = speaking_text
        
        # Acknowledge the modal submission first
        await interaction.response.defer()
        
        # Move to next step
        await self.view.move_to_next_step_after_modal(interaction)

class PersonalityHumorModal(discord.ui.Modal, title="Humor Style"):
    def __init__(self, bot, personality_data, view):
        super().__init__()
        self.bot = bot
        self.personality_data = personality_data
        self.view = view
    
    humor_input = discord.ui.TextInput(
        label="Humor Style",
        placeholder="What kind of humor should I use? (e.g., sarcastic, wholesome, dark, punny)",
        style=discord.TextStyle.short,
        max_length=100,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        humor_text = self.humor_input.value.strip()
        if humor_text:
            self.personality_data.humor_style = humor_text
        
        # Acknowledge the modal submission first
        await interaction.response.defer()
        
        # Move to next step
        await self.view.move_to_next_step_after_modal(interaction)

class PersonalityQuirksModal(discord.ui.Modal, title="Special Quirks"):
    def __init__(self, bot, personality_data, view):
        super().__init__()
        self.bot = bot
        self.personality_data = personality_data
        self.view = view
    
    quirks_input = discord.ui.TextInput(
        label="Special Quirks or Catchphrases",
        placeholder="Any special habits, catchphrases, or unique behaviors?",
        style=discord.TextStyle.paragraph,
        max_length=200,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        quirks_text = self.quirks_input.value.strip()
        if quirks_text:
            self.personality_data.special_quirks = quirks_text
        
        # Acknowledge the modal submission first
        await interaction.response.defer()
        
        # Complete customization
        await self.view.complete_customization_after_modal(interaction)

class PersonalityCustomizationView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=600)  # 10 minute timeout
        self.bot = bot
        self.user_id = user_id
        self.personality_data = PersonalityData()
        self.current_step = "welcome"
        self.setup_buttons()
    
    def check_user(self, interaction: discord.Interaction) -> bool:
        """Check if this is the original user"""
        return str(interaction.user.id) == str(self.user_id)
    
    def setup_buttons(self):
        """Setup buttons based on current step"""
        self.clear_items()
        
        if self.current_step == "welcome":
            button = discord.ui.Button(
                label="Start Customization",
                emoji="🎨",
                style=discord.ButtonStyle.primary,
                custom_id="start"
            )
            button.callback = self.start_callback
            self.add_item(button)
        

        
        elif self.current_step == "age":
            button = discord.ui.Button(
                label="Set Age/Maturity",
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
        
        elif self.current_step == "traits":
            button = discord.ui.Button(
                label="Set Personality Traits",
                emoji="🎭",
                style=discord.ButtonStyle.primary,
                custom_id="traits"
            )
            button.callback = self.traits_callback
            self.add_item(button)
            
            skip_button = discord.ui.Button(
                label="Skip",
                emoji="⏭️",
                style=discord.ButtonStyle.secondary,
                custom_id="skip"
            )
            skip_button.callback = self.skip_callback
            self.add_item(skip_button)
        
        elif self.current_step == "interests":
            button = discord.ui.Button(
                label="Set Interests",
                emoji="🎯",
                style=discord.ButtonStyle.primary,
                custom_id="interests"
            )
            button.callback = self.interests_callback
            self.add_item(button)
            
            skip_button = discord.ui.Button(
                label="Skip",
                emoji="⏭️",
                style=discord.ButtonStyle.secondary,
                custom_id="skip"
            )
            skip_button.callback = self.skip_callback
            self.add_item(skip_button)
        
        elif self.current_step == "speaking":
            button = discord.ui.Button(
                label="Set Speaking Style",
                emoji="💬",
                style=discord.ButtonStyle.primary,
                custom_id="speaking"
            )
            button.callback = self.speaking_callback
            self.add_item(button)
            
            skip_button = discord.ui.Button(
                label="Skip",
                emoji="⏭️",
                style=discord.ButtonStyle.secondary,
                custom_id="skip"
            )
            skip_button.callback = self.skip_callback
            self.add_item(skip_button)
        
        elif self.current_step == "humor":
            button = discord.ui.Button(
                label="Set Humor Style",
                emoji="😄",
                style=discord.ButtonStyle.primary,
                custom_id="humor"
            )
            button.callback = self.humor_callback
            self.add_item(button)
            
            skip_button = discord.ui.Button(
                label="Skip",
                emoji="⏭️",
                style=discord.ButtonStyle.secondary,
                custom_id="skip"
            )
            skip_button.callback = self.skip_callback
            self.add_item(skip_button)
        
        elif self.current_step == "quirks":
            button = discord.ui.Button(
                label="Add Special Quirks",
                emoji="✨",
                style=discord.ButtonStyle.primary,
                custom_id="quirks"
            )
            button.callback = self.quirks_callback
            self.add_item(button)
            
            finish_button = discord.ui.Button(
                label="Finish Customization",
                emoji="✅",
                style=discord.ButtonStyle.success,
                custom_id="finish"
            )
            finish_button.callback = self.finish_callback
            self.add_item(finish_button)
    
    def get_welcome_embed(self) -> discord.Embed:
        """Initial welcome embed for personality customization"""
        embed = discord.Embed(
            title="🎨 Customize My Personality",
            description="As a Premium user, you can customize how I behave and respond! Let's make me uniquely yours.",
            color=0xFFD700
        )
        
        embed.add_field(
            name="🎭 What You Can Customize",
            value="• Age/maturity level\n• Personality traits\n• Interests & knowledge areas\n• Speaking style\n• Humor style\n• Special quirks & catchphrases",
            inline=False
        )
        
        embed.add_field(
            name="⏱️ Time Required",
            value="About 3-5 minutes. You can skip any step you want!",
            inline=False
        )
        
        embed.add_field(
            name="🔄 Note",
            value="This will replace my current personality. You can always reset to default later.",
            inline=False
        )
        
        embed.set_footer(text="Click 'Start Customization' to begin • Premium Feature")
        return embed
    
    def get_step_embed(self, step: str) -> discord.Embed:
        """Get embed for specific customization step"""
        embeds = {
            "name": {
                "title": "🏷️ Bot Name & Identity",
                "description": "What should I call myself? This is optional - I'll still be Chatore to everyone else!",
                "example": "Examples: Alex, Luna, Buddy, or keep it as Chatore"
            },
            "age": {
                "title": "🎂 Age & Maturity Level", 
                "description": "How old should I act? This affects my maturity and conversation style.",
                "example": "Examples: 18 (young & energetic), 25 (balanced), 30 (mature)"
            },
            "traits": {
                "title": "🎭 Personality Traits",
                "description": "How should I behave in conversations?",
                "example": "Examples: funny, sarcastic, supportive, energetic, calm, witty"
            },
            "interests": {
                "title": "🎯 Interests & Knowledge",
                "description": "What should I be passionate about and knowledgeable in?",
                "example": "Examples: anime, coding, music, sports, art, gaming, movies"
            },
            "speaking": {
                "title": "💬 Speaking Style",
                "description": "How should I communicate with you?",
                "example": "Examples: casual, formal, street slang, professional, friendly"
            },
            "humor": {
                "title": "😄 Humor Style",
                "description": "What kind of humor should I use?",
                "example": "Examples: sarcastic, wholesome, dark humor, punny, dry wit"
            },
            "quirks": {
                "title": "✨ Special Quirks",
                "description": "Any special habits, catchphrases, or unique behaviors?",
                "example": "Examples: Always says 'no cap', uses lots of emojis, references memes"
            }
        }
        
        step_info = embeds.get(step, embeds["name"])
        
        embed = discord.Embed(
            title=step_info["title"],
            description=step_info["description"],
            color=0x9B59B6
        )
        
        embed.add_field(
            name="💡 " + step_info["example"].split(":")[0],
            value=step_info["example"].split(": ", 1)[1],
            inline=False
        )
        
        # Add progress indicator
        steps = ["name", "age", "traits", "interests", "speaking", "humor", "quirks"]
        current_index = steps.index(step) + 1
        embed.set_footer(text=f"Step {current_index}/7 • Click the button to customize or skip")
        
        return embed
    
    async def move_to_next_step(self, interaction: discord.Interaction):
        """Move to the next customization step"""
        if self.current_step == "age":
            self.current_step = "traits"
        elif self.current_step == "traits":
            self.current_step = "interests"
        elif self.current_step == "interests":
            self.current_step = "speaking"
        elif self.current_step == "speaking":
            self.current_step = "humor"
        elif self.current_step == "humor":
            self.current_step = "quirks"
        else:
            await self.complete_customization(interaction)
            return
        
        embed = self.get_step_embed(self.current_step)
        self.setup_buttons()
        
        # Try to respond first, if that fails, use followup
        try:
            await interaction.response.edit_message(embed=embed, view=self)
        except discord.errors.InteractionResponded:
            # If interaction was already responded to (from modal), use followup
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
        except discord.errors.NotFound:
            # If interaction token expired, send a new message
            await interaction.followup.send(embed=embed, view=self, ephemeral=True)
    
    async def skip_current_step(self, interaction: discord.Interaction):
        """Skip the current step"""
        await self.move_to_next_step(interaction)
    
    async def move_to_next_step_after_modal(self, interaction: discord.Interaction):
        """Move to the next customization step after modal submission"""
        if self.current_step == "age":
            self.current_step = "traits"
        elif self.current_step == "traits":
            self.current_step = "interests"
        elif self.current_step == "interests":
            self.current_step = "speaking"
        elif self.current_step == "speaking":
            self.current_step = "humor"
        elif self.current_step == "humor":
            self.current_step = "quirks"
        else:
            await self.complete_customization_after_modal(interaction)
            return
        
        embed = self.get_step_embed(self.current_step)
        self.setup_buttons()
        
        # Use followup since we already deferred the interaction
        await interaction.followup.edit_message(interaction.message.id, embed=embed, view=self)
    
    async def complete_customization_after_modal(self, interaction: discord.Interaction):
        """Complete the personality customization after modal submission"""
        user_id = str(interaction.user.id)
        
        # Build personality data dictionary
        personality_dict = {}
        if self.personality_data.age:
            personality_dict['age'] = self.personality_data.age
        if self.personality_data.traits:
            personality_dict['traits'] = self.personality_data.traits
        if self.personality_data.interests:
            personality_dict['interests'] = self.personality_data.interests
        if self.personality_data.speaking_style:
            personality_dict['speaking_style'] = self.personality_data.speaking_style
        if self.personality_data.humor_style:
            personality_dict['humor_style'] = self.personality_data.humor_style
        if self.personality_data.special_quirks:
            personality_dict['special_quirks'] = self.personality_data.special_quirks
        
        # Save custom personality
        success = self.bot.personality_manager.set_custom_personality(user_id, personality_dict)
        
        if success:
            await self.bot.personality_manager.save_personalities()
            
            embed = discord.Embed(
                title="🎉 Personality Customized!",
                description="Your custom personality has been saved! I'll now behave according to your preferences.",
                color=0x00FF7F
            )
            
            # Show summary of customizations
            summary_parts = []
            if self.personality_data.age:
                summary_parts.append(f"**Age**: {self.personality_data.age} years old")
            if self.personality_data.traits:
                summary_parts.append(f"**Traits**: {', '.join(self.personality_data.traits[:3])}{'...' if len(self.personality_data.traits) > 3 else ''}")
            if self.personality_data.interests:
                summary_parts.append(f"**Interests**: {', '.join(self.personality_data.interests[:3])}{'...' if len(self.personality_data.interests) > 3 else ''}")
            if self.personality_data.speaking_style:
                summary_parts.append(f"**Speaking**: {self.personality_data.speaking_style}")
            if self.personality_data.humor_style:
                summary_parts.append(f"**Humor**: {self.personality_data.humor_style}")
            
            if summary_parts:
                embed.add_field(
                    name="📝 Your Customizations",
                    value="\n".join(summary_parts),
                    inline=False
                )
            
            embed.add_field(
                name="🚀 What's Next?",
                value="• Start chatting with me to see your custom personality in action!\n• Use `/personality` to manage presets and settings\n• Save this personality as a preset for easy switching!",
                inline=False
            )
            
            embed.add_field(
                name="💾 Pro Tip",
                value="Use the 'Manage Presets' button in `/personality` to save this configuration as a preset!",
                inline=False
            )
            
            embed.set_footer(text="Premium Feature • Your personality is now active!")
        else:
            embed = discord.Embed(
                title="❌ Customization Failed",
                description="There was an error saving your personality. Please try again.",
                color=0xFF6B6B
            )
        
        # Use followup since we already deferred the interaction
        await interaction.followup.edit_message(interaction.message.id, embed=embed, view=None)
    
    async def complete_customization(self, interaction: discord.Interaction):
        """Complete the personality customization"""
        user_id = str(interaction.user.id)
        
        # Build personality data dictionary
        personality_dict = {}
        if self.personality_data.age:
            personality_dict['age'] = self.personality_data.age
        if self.personality_data.traits:
            personality_dict['traits'] = self.personality_data.traits
        if self.personality_data.interests:
            personality_dict['interests'] = self.personality_data.interests
        if self.personality_data.speaking_style:
            personality_dict['speaking_style'] = self.personality_data.speaking_style
        if self.personality_data.humor_style:
            personality_dict['humor_style'] = self.personality_data.humor_style
        if self.personality_data.special_quirks:
            personality_dict['special_quirks'] = self.personality_data.special_quirks
        
        # Save custom personality
        success = self.bot.personality_manager.set_custom_personality(user_id, personality_dict)
        
        if success:
            await self.bot.personality_manager.save_personalities()
            
            embed = discord.Embed(
                title="🎉 Personality Customized!",
                description="Your custom personality has been saved! I'll now behave according to your preferences.",
                color=0x00FF7F
            )
            
            # Show summary of customizations
            summary_parts = []
            if self.personality_data.age:
                summary_parts.append(f"**Age**: {self.personality_data.age} years old")
            if self.personality_data.traits:
                summary_parts.append(f"**Traits**: {', '.join(self.personality_data.traits[:3])}{'...' if len(self.personality_data.traits) > 3 else ''}")
            if self.personality_data.interests:
                summary_parts.append(f"**Interests**: {', '.join(self.personality_data.interests[:3])}{'...' if len(self.personality_data.interests) > 3 else ''}")
            if self.personality_data.speaking_style:
                summary_parts.append(f"**Speaking**: {self.personality_data.speaking_style}")
            if self.personality_data.humor_style:
                summary_parts.append(f"**Humor**: {self.personality_data.humor_style}")
            
            if summary_parts:
                embed.add_field(
                    name="📝 Your Customizations",
                    value="\n".join(summary_parts),
                    inline=False
                )
            
            embed.add_field(
                name="🚀 What's Next?",
                value="• Start chatting with me to see your custom personality in action!\n• Use `/personality` to manage presets and settings\n• Save this personality as a preset for easy switching!",
                inline=False
            )
            
            embed.add_field(
                name="💾 Pro Tip",
                value="Use the 'Manage Presets' button in `/personality` to save this configuration as a preset!",
                inline=False
            )
            
            embed.set_footer(text="Premium Feature • Your personality is now active!")
        else:
            embed = discord.Embed(
                title="❌ Customization Failed",
                description="There was an error saving your personality. Please try again.",
                color=0xFF6B6B
            )
        
        # Try to respond first, if that fails, use followup
        try:
            await interaction.response.edit_message(embed=embed, view=None)
        except discord.errors.InteractionResponded:
            # If interaction was already responded to (from modal), use followup
            await interaction.followup.edit_message(interaction.message.id, embed=embed, view=None)
        except discord.errors.NotFound:
            # If interaction token expired, send a new message
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    # Button callback methods
    async def start_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This customization is not for you!", ephemeral=True)
            return
        
        self.current_step = "age"
        embed = self.get_step_embed(self.current_step)
        self.setup_buttons()
        await interaction.response.edit_message(embed=embed, view=self)
    

    
    async def age_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This customization is not for you!", ephemeral=True)
            return
        
        modal = PersonalityAgeModal(self.bot, self.personality_data, self)
        await interaction.response.send_modal(modal)
    
    async def traits_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This customization is not for you!", ephemeral=True)
            return
        
        modal = PersonalityTraitsModal(self.bot, self.personality_data, self)
        await interaction.response.send_modal(modal)
    
    async def interests_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This customization is not for you!", ephemeral=True)
            return
        
        modal = PersonalityInterestsModal(self.bot, self.personality_data, self)
        await interaction.response.send_modal(modal)
    
    async def speaking_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This customization is not for you!", ephemeral=True)
            return
        
        modal = PersonalitySpeakingModal(self.bot, self.personality_data, self)
        await interaction.response.send_modal(modal)
    
    async def humor_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This customization is not for you!", ephemeral=True)
            return
        
        modal = PersonalityHumorModal(self.bot, self.personality_data, self)
        await interaction.response.send_modal(modal)
    
    async def quirks_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This customization is not for you!", ephemeral=True)
            return
        
        modal = PersonalityQuirksModal(self.bot, self.personality_data, self)
        await interaction.response.send_modal(modal)
    
    async def skip_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This customization is not for you!", ephemeral=True)
            return
        
        await self.skip_current_step(interaction)
    
    async def finish_callback(self, interaction: discord.Interaction):
        if not self.check_user(interaction):
            await interaction.response.send_message("❌ This customization is not for you!", ephemeral=True)
            return
        
        await self.complete_customization(interaction)
    
    async def on_timeout(self):
        # Disable all buttons when timeout occurs
        for item in self.children:
            item.disabled = True

def setup(bot):
    """Setup personality commands - this is called from the main bot file"""
    pass  # Commands are integrated into utility_commands.py