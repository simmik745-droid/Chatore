"""
Help Commands - Modern interactive help system with dropdown and pagination
"""

import discord
from discord.ext import commands
from discord import app_commands

class HelpView(discord.ui.View):
    def __init__(self, bot, original_user_id=None):
        super().__init__(timeout=30)  # 30 second timeout
        self.bot = bot
        self.current_page = "main"
        self.current_subpage = 0  # For pagination within categories
        self.original_user_id = original_user_id
        self.message = None  # Store message for timeout updates
        self.setup_components()
    
    def setup_components(self):
        """Setup dropdown and navigation buttons"""
        self.clear_items()
        
        # Add dropdown menu
        dropdown = HelpDropdown(self)
        self.add_item(dropdown)
        
        # Add navigation buttons for paginated content
        if self.current_page in ["chat", "utility"]:
            # Add left/right navigation for paginated content
            left_button = discord.ui.Button(
                emoji="⬅️",
                style=discord.ButtonStyle.secondary,
                disabled=self.current_subpage == 0,
                row=1
            )
            left_button.callback = self.previous_page
            self.add_item(left_button)
            
            right_button = discord.ui.Button(
                emoji="➡️", 
                style=discord.ButtonStyle.secondary,
                disabled=not self.has_next_page(),
                row=1
            )
            right_button.callback = self.next_page
            self.add_item(right_button)
        
        # Always add home button
        home_button = discord.ui.Button(
            label="🏠 Home",
            style=discord.ButtonStyle.primary,
            row=1
        )
        home_button.callback = self.home_button_callback
        self.add_item(home_button)
    
    def get_main_embed(self):
        embed = discord.Embed(
            title="🍽️ Chatore Help Center",
            description="Welcome! I'm Chatore, your AI companion powered by Gemini 2.5 Flash.",
            color=0x7289DA
        )
        
        embed.add_field(
            name="🚀 Quick Start",
            value="• Mention me `@Chatore` to chat naturally\n• Use `/help` to see all commands\n• Try `/memory` to tell me about yourself\n• Use `/ask` for private questions",
            inline=False
        )
        
        embed.add_field(
            name="📋 Categories",
            value="Use the dropdown menu below to explore:\n\n🤖 **About Me** - Learn about my personality\n💬 **Chat Commands** - Memory and conversation tools\n🛠️ **Utility Commands** - Bot tools and information",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Select a category from the dropdown • Auto-closes in 30s")
        return embed
    
    def has_next_page(self):
        """Check if there's a next page for current category"""
        if self.current_page == "chat":
            return self.current_subpage < len(self.get_chat_pages()) - 1
        elif self.current_page == "utility":
            return self.current_subpage < len(self.get_utility_pages()) - 1
        return False
    
    async def previous_page(self, interaction: discord.Interaction):
        """Go to previous page"""
        if self.current_subpage > 0:
            self.current_subpage -= 1
            embed = self.get_current_embed()
            self.setup_components()
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def next_page(self, interaction: discord.Interaction):
        """Go to next page"""
        if self.has_next_page():
            self.current_subpage += 1
            embed = self.get_current_embed()
            self.setup_components()
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def home_button_callback(self, interaction: discord.Interaction):
        """Return to home page"""
        self.current_page = "main"
        self.current_subpage = 0
        embed = self.get_main_embed()
        self.setup_components()
        await interaction.response.edit_message(embed=embed, view=self)
    
    def check_user(self, interaction: discord.Interaction):
        """Check if interaction is from the original user"""
        if self.original_user_id and str(interaction.user.id) != str(self.original_user_id):
            return False
        return True
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if user can interact and if view hasn't timed out"""
        # Check if user is authorized
        if not self.check_user(interaction):
            await interaction.response.send_message(
                "❌ This help menu is not for you! Use `/help` to get your own.",
                ephemeral=True
            )
            return False
        
        # Check if view has timed out (this is automatically handled by Discord)
        return True
    
    def get_current_embed(self):
        """Get embed for current page and subpage"""
        if self.current_page == "main":
            return self.get_main_embed()
        elif self.current_page == "about":
            return self.get_about_embed()
        elif self.current_page == "chat":
            return self.get_chat_embed()
        elif self.current_page == "utility":
            return self.get_utility_embed()
        return self.get_main_embed()
    
    def get_about_embed(self):
        embed = discord.Embed(
            title="🤖 About Chatore",
            description="Hi! I'm Chatore, your friendly AI companion powered by Gemini 2.5 Flash.",
            color=0x9B59B6
        )
        
        embed.add_field(
            name="🎭 My Personality",
            value="• Friendly and witty with good humor\n• Knowledgeable about gaming, tech, and memes\n• Supportive and encouraging\n• Uses emojis and internet slang naturally",
            inline=False
        )
        
        embed.add_field(
            name="🤖 About Me",
            value="• Male bot created by Abhinav\n• Age unknown but I'm timeless!\n• Love gaming and various topics\n• Can speak both English and Hinglish",
            inline=False
        )
        
        embed.add_field(
            name="🧠 What Makes Me Special",
            value="• I remember things about you permanently\n• I track our recent conversations for context\n• I can chat casually or answer formal questions\n• I provide beautiful, organized responses",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text="Use the dropdown to explore more!")
        return embed
    
    def get_chat_pages(self):
        """Get all chat command pages"""
        all_commands = [
            ("/memory <text>", "💾", "Tell me something to remember about you forever"),
            ("/memories", "📝", "See what I remember about you + manage memories"),
            ("/ask <question>", "❓", "Ask me a formal question with length options (private DM response)"),
            ("/delete_memory", "🗑️", "Delete a specific memory from your stored memories"),
            ("/forget", "🗑️", "Clear all your memories and conversation history"),
        ]
        
        # Split commands into pages of 5
        pages = []
        for i in range(0, len(all_commands), 5):
            pages.append(all_commands[i:i+5])
        
        return pages
    
    def get_chat_embed(self):
        pages = self.get_chat_pages()
        current_commands = pages[self.current_subpage]
        
        embed = discord.Embed(
            title="💬 Chat & Memory Commands",
            description="Commands for managing conversations and memories",
            color=0x00FF7F
        )
        
        for cmd, emoji, desc in current_commands:
            embed.add_field(
                name=f"{emoji} {cmd}",
                value=desc,
                inline=False
            )
        
        # Add memory system info on first page
        if self.current_subpage == 0:
            embed.add_field(
                name="💡 Memory System",
                value="• **Permanent Memories**: Stay forever\n• **Conversation Context**: Last 12-25 messages\n• **Smart Responses**: Uses both for natural chat",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.current_subpage + 1}/{len(pages)} • Use ⬅️➡️ to navigate")
        return embed
    
    def get_utility_pages(self):
        """Get all utility command pages"""
        all_commands = [
            ("/personality", "🌟", "Learn about my personality and customize it (Premium)"),
            ("/language", "🌐", "Switch between English and Hinglish personalities"),
            ("/langstatus", "🗣️", "Check your current language setting"),
            ("/ping", "🏓", "Check my response time and connection status"),
            ("/stats", "📊", "View bot statistics and usage information"),
            ("/activity", "⏰", "Check your activity status and memory cleanup info"),
            ("/plan", "📊", "Check your subscription plan and usage limits"),
            ("/subscribe", "⭐", "Subscribe to Chatore Premium for enhanced features"),
            ("/invite", "🔗", "Get the invite link to add me to your server"),
            ("/owner", "👑", "Meet Abhinav Anand - Chatore's owner and creator"),
            ("/help", "❓", "Show this interactive help menu"),
        ]
        
        # Split commands into pages of 6
        pages = []
        for i in range(0, len(all_commands), 6):
            pages.append(all_commands[i:i+6])
        
        return pages
    
    def get_utility_embed(self):
        pages = self.get_utility_pages()
        current_commands = pages[self.current_subpage]
        
        embed = discord.Embed(
            title="🛠️ Utility Commands",
            description="Helpful tools and bot information",
            color=0xE91E63
        )
        
        for cmd, emoji, desc in current_commands:
            embed.add_field(
                name=f"{emoji} {cmd}",
                value=desc,
                inline=False
            )
        
        # Add pro tips on last page
        if self.current_subpage == len(pages) - 1:
            embed.add_field(
                name="🎯 Pro Tips",
                value="• Slash commands work in any channel\n• Most responses use beautiful embeds\n• I'm always learning and improving!",
                inline=False
            )
        
        embed.set_footer(text=f"Page {self.current_subpage + 1}/{len(pages)} • Use ⬅️➡️ to navigate")
        return embed
    
    async def on_timeout(self):
        """Handle timeout - disable all components and update message"""
        for item in self.children:
            item.disabled = True
        
        # Create timeout embed
        embed = discord.Embed(
            title="⏰ Help Menu Timed Out",
            description="This help menu has expired after 30 seconds of inactivity.",
            color=0x95A5A6
        )
        embed.add_field(
            name="💡 Need Help Again?",
            value="Use `/help` to open a new help menu anytime!",
            inline=False
        )
        embed.set_footer(text="Help menu expired • Use /help for a new one")
        
        # Try to edit the message to show timeout
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except discord.NotFound:
                # Message was deleted
                pass
            except discord.Forbidden:
                # No permission to edit
                pass
            except Exception:
                # Other errors
                pass

class HelpDropdown(discord.ui.Select):
    def __init__(self, help_view):
        self.help_view = help_view
        
        options = [
            discord.SelectOption(
                label="Home",
                description="Return to the main help page",
                emoji="🏠",
                value="main"
            ),
            discord.SelectOption(
                label="About Me",
                description="Learn about Chatore's personality and capabilities",
                emoji="🤖",
                value="about"
            ),
            discord.SelectOption(
                label="Chat Commands",
                description="Commands for conversations and memory management",
                emoji="💬",
                value="chat"
            ),
            discord.SelectOption(
                label="Utility Commands", 
                description="Helpful tools and bot information",
                emoji="🛠️",
                value="utility"
            ),
        ]
        
        super().__init__(
            placeholder="Choose a help category...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        # Update current page and reset subpage
        self.help_view.current_page = self.values[0]
        self.help_view.current_subpage = 0
        
        # Get appropriate embed and update components
        embed = self.help_view.get_current_embed()
        self.help_view.setup_components()
        
        await interaction.response.edit_message(embed=embed, view=self.help_view)

def setup(bot):
    """Setup help commands"""
    
    @bot.command(name='help')
    async def interactive_help(ctx):
        """Show Chatore's interactive help system"""
        view = HelpView(bot, ctx.author.id)
        embed = view.get_main_embed()
        message = await ctx.reply(embed=embed, view=view)
        view.message = message

    # Slash Commands
    @bot.tree.command(name="help", description="Show Chatore's interactive help system")
    async def slash_help(interaction: discord.Interaction):
        """Show Chatore's interactive help system (slash command)"""
        view = HelpView(bot, interaction.user.id)
        embed = view.get_main_embed()
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()