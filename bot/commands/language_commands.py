"""
Language Commands - Language switching and preferences
"""

import discord
from discord.ext import commands
from discord import app_commands

class LanguageSelect(discord.ui.Select):
    def __init__(self, bot, original_user_id):
        self.bot = bot
        self.original_user_id = original_user_id
        
        options = [
            discord.SelectOption(
                label="English",
                description="Casual and friendly English responses",
                emoji="🇺🇸",
                value="english"
            ),
            discord.SelectOption(
                label="Hinglish",
                description="Desi vibes with dark humor and sarcasm",
                emoji="🇮🇳",
                value="hinglish"
            )
        ]
        
        super().__init__(
            placeholder="Choose your preferred language...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Check if this is the original user
        if str(interaction.user.id) != str(self.original_user_id):
            await interaction.response.send_message(
                "❌ This language menu was not opened by you! Use `/language` to get your own.",
                ephemeral=True
            )
            return
        
        selected_language = self.values[0]
        user_id = str(interaction.user.id)
        
        # Save language preference
        self.bot.memory.set_user_language(user_id, selected_language)
        await self.bot.memory.save_memory()
        
        # Create response embed based on selected language
        if selected_language == "english":
            embed = discord.Embed(
                title="🇺🇸 Language Set to English",
                description="Cool! I'll chat with you in casual English with my usual chill vibe.",
                color=0x5865F2
            )
            embed.add_field(
                name="My English Personality",
                value="• Strictly English responses\n• Casual and friendly\n• Good humor and wit\n• Internet culture savvy\n• Only occasional 'yaar' allowed",
                inline=False
            )
        else:  # hinglish
            embed = discord.Embed(
                title="🇮🇳 Language Set to Hinglish",
                description="Arrey waah! Ab main tere saath Hinglish mein baat karunga, full desi style!",
                color=0xFF9933
            )
            embed.add_field(
                name="Meri Hinglish Personality",
                value="• Dark humor aur sarcasm\n• Indian slang aur references\n• Thoda savage but pyaar se\n• Bollywood, cricket, street food sab pata hai",
                inline=False
            )
        
        embed.set_footer(text=f"Language preference saved for {interaction.user.display_name}")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.edit_message(embed=embed, view=None)

class LanguageView(discord.ui.View):
    def __init__(self, bot, original_user_id):
        super().__init__(timeout=30)
        self.message = None  # Store message for timeout updates
        self.bot = bot
        self.original_user_id = original_user_id
        self.add_item(LanguageSelect(bot, original_user_id))
    
    async def on_timeout(self):
        # Disable the select menu when timeout occurs
        for item in self.children:
            item.disabled = True
    
    async def on_timeout(self):
        """Handle timeout - disable all components and update message"""
        for item in self.children:
            item.disabled = True
        
        # Create timeout embed
        embed = discord.Embed(
            title="⏰ Language Menu Timed Out",
            description="This language selection menu has expired after 30 seconds of inactivity.",
            color=0x95A5A6
        )
        embed.add_field(
            name="💡 Need Help Again?",
            value="Use `/language` to open a new language menu anytime!",
            inline=False
        )
        embed.set_footer(text="Menu expired • Use /language for a new one")
        
        # Try to edit the message to show timeout
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except (discord.NotFound, discord.Forbidden, Exception):
                pass

def setup(bot):
    """Setup language commands"""
    
    @bot.command(name='language', aliases=['lang'])
    async def set_language(ctx):
        """Change Chatore's language and personality"""
        user_id = str(ctx.author.id)
        current_language = bot.memory.get_user_language(user_id)
        
        embed = discord.Embed(
            title="🌐 Choose Your Language",
            description="Select how you want me to chat with you! Each language has its own personality.",
            color=0x7289DA
        )
        
        embed.add_field(
            name="🇺🇸 English",
            value="Casual, friendly, and chill vibes with good humor",
            inline=True
        )
        
        embed.add_field(
            name="🇮🇳 Hinglish",
            value="Desi style with dark humor, sarcasm, and Indian references",
            inline=True
        )
        
        embed.add_field(
            name="Current Setting",
            value=f"**{current_language.title()}** {'🇺🇸' if current_language == 'english' else '🇮🇳'}",
            inline=False
        )
        
        embed.set_footer(text="Select from the dropdown below • Timeout: 1 minute")
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        
        view = LanguageView(bot, ctx.author.id)
        await ctx.reply(embed=embed, view=view)
    
    @bot.command(name='langstatus')
    async def language_status(ctx):
        """Check current language setting"""
        user_id = str(ctx.author.id)
        current_language = bot.memory.get_user_language(user_id)
        
        if current_language == 'english':
            embed = discord.Embed(
                title="🇺🇸 Current Language: English",
                description="I'm currently chatting with you in casual English!",
                color=0x5865F2
            )
            embed.add_field(
                name="My Current Vibe",
                value="Chill, friendly, witty, and supportive with good humor",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="🇮🇳 Current Language: Hinglish",
                description="Abhi main tere saath Hinglish mein baat kar raha hun, full desi mode!",
                color=0xFF9933
            )
            embed.add_field(
                name="Mera Current Vibe",
                value="Dark humor, sarcasm, Indian references, thoda savage but pyaar se",
                inline=False
            )
        
        embed.add_field(
            name="Want to Change?",
            value="Use `/language` to switch between English and Hinglish",
            inline=False
        )
        
        embed.set_footer(text=f"Language preference for {ctx.author.display_name}")
        await ctx.reply(embed=embed)

    # Slash Commands
    @bot.tree.command(name="language", description="Change Chatore's language and personality")
    async def slash_language(interaction: discord.Interaction):
        """Change Chatore's language and personality (slash command)"""
        user_id = str(interaction.user.id)
        current_language = bot.memory.get_user_language(user_id)
        
        embed = discord.Embed(
            title="🌐 Choose Your Language",
            description="Select how you want me to chat with you! Each language has its own personality.",
            color=0x7289DA
        )
        
        embed.add_field(
            name="🇺🇸 English",
            value="Casual, friendly, and chill vibes with good humor",
            inline=True
        )
        
        embed.add_field(
            name="🇮🇳 Hinglish",
            value="Desi style with dark humor, sarcasm, and Indian references",
            inline=True
        )
        
        embed.add_field(
            name="Current Setting",
            value=f"**{current_language.title()}** {'🇺🇸' if current_language == 'english' else '🇮🇳'}",
            inline=False
        )
        
        embed.set_footer(text="Select from the dropdown below • Timeout: 1 minute")
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        
        view = LanguageView(bot, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
    
    @bot.tree.command(name="langstatus", description="Check your current language setting")
    async def slash_langstatus(interaction: discord.Interaction):
        """Check current language setting (slash command)"""
        user_id = str(interaction.user.id)
        current_language = bot.memory.get_user_language(user_id)
        
        if current_language == 'english':
            embed = discord.Embed(
                title="🇺🇸 Current Language: English",
                description="I'm currently chatting with you in casual English!",
                color=0x5865F2
            )
            embed.add_field(
                name="My Current Vibe",
                value="Chill, friendly, witty, and supportive with good humor",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="🇮🇳 Current Language: Hinglish",
                description="Abhi main tere saath Hinglish mein baat kar raha hun, full desi mode!",
                color=0xFF9933
            )
            embed.add_field(
                name="Mera Current Vibe",
                value="Dark humor, sarcasm, Indian references, thoda savage but pyaar se",
                inline=False
            )
        
        embed.add_field(
            name="Want to Change?",
            value="Use `/language` to switch between English and Hinglish",
            inline=False
        )
        
        embed.set_footer(text=f"Language preference for {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)