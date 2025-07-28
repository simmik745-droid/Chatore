"""
Chat Commands - Memory and conversation related commands
"""

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime

class AddMemoryModal(discord.ui.Modal, title="Add New Memory"):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
    
    memory_input = discord.ui.TextInput(
        label="New Memory",
        placeholder="What would you like me to remember about you?",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        memory_text = self.memory_input.value.strip()
        
        if not memory_text:
            embed = discord.Embed(
                title="❌ Invalid Memory",
                description="Please enter a valid memory.",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Add the memory
        self.bot.memory.add_user_memory(self.user_id, memory_text)
        await self.bot.memory.save_memory()
        
        embed = discord.Embed(
            title="Memory Saved! 🧠",
            description=f"I'll remember that: *{memory_text}*",
            color=0x00FF7F
        )
        embed.set_footer(text=f"Memory added for {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MemoryManagementView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=30)  # 30 second timeout
        self.bot = bot
        self.user_id = user_id
        self.message = None  # Store message for timeout updates
    
    @discord.ui.button(label="Add New Memory", emoji="➕", style=discord.ButtonStyle.primary)
    async def add_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This memory management is not for you!", ephemeral=True)
            return
        
        # Show modal to add new memory
        modal = AddMemoryModal(self.bot, str(self.user_id))
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Edit Memory", emoji="✏️", style=discord.ButtonStyle.secondary)
    async def edit_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This memory management is not for you!", ephemeral=True)
            return
        
        # Get memories with indices
        memories_with_indices = self.bot.memory.get_user_memories_with_indices(self.user_id)
        
        if not memories_with_indices:
            await interaction.response.send_message("❌ You don't have any memories to edit!", ephemeral=True)
            return
        
        # Create dropdown for memory selection
        view = MemoryEditView(self.bot, self.user_id, memories_with_indices)
        embed = discord.Embed(
            title="✏️ Edit Specific Memory",
            description="Select which memory you'd like to edit from the dropdown below:",
            color=0xFFD700
        )
        
        # Show memories with numbers
        memory_list = []
        for i, mem in enumerate(memories_with_indices[:10]):  # Show max 10
            memory_preview = mem['memory'][:50] + "..." if len(mem['memory']) > 50 else mem['memory']
            memory_list.append(f"**{i+1}.** {memory_preview}")
        
        embed.add_field(
            name="Your Memories",
            value="\n".join(memory_list),
            inline=False
        )
        
        embed.add_field(
            name="💡 Tip",
            value="Select a memory to edit its content.",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Delete Specific Memory", emoji="🗑️", style=discord.ButtonStyle.danger)
    async def delete_memory_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This memory management is not for you!", ephemeral=True)
            return
        
        # Get memories with indices
        memories_with_indices = self.bot.memory.get_user_memories_with_indices(self.user_id)
        
        if not memories_with_indices:
            await interaction.response.send_message("❌ You don't have any memories to delete!", ephemeral=True)
            return
        
        # Create dropdown for memory selection
        view = MemoryDeletionView(self.bot, self.user_id, memories_with_indices)
        embed = discord.Embed(
            title="🗑️ Delete Specific Memory",
            description="Select which memory you'd like to delete from the dropdown below:",
            color=0xFF6B6B
        )
        
        # Show memories with numbers
        memory_list = []
        for i, mem in enumerate(memories_with_indices[:10]):  # Show max 10
            memory_preview = mem['memory'][:50] + "..." if len(mem['memory']) > 50 else mem['memory']
            memory_list.append(f"**{i+1}.** {memory_preview}")
        
        embed.add_field(
            name="Your Memories",
            value="\n".join(memory_list),
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Warning",
            value="Deleted memories cannot be recovered!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def on_timeout(self):
        """Handle timeout - disable all components and update message"""
        for item in self.children:
            item.disabled = True
        
        # Create timeout embed
        embed = discord.Embed(
            title="⏰ Memory Menu Timed Out",
            description="This memory management menu has expired after 30 seconds of inactivity.",
            color=0x95A5A6
        )
        embed.add_field(
            name="💡 Need Help Again?",
            value="Use `/memories` to open a new memory menu anytime!",
            inline=False
        )
        embed.set_footer(text="Menu expired • Use /memories for a new one")
        
        # Try to edit the message to show timeout
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except (discord.NotFound, discord.Forbidden, Exception):
                pass

class MemoryDeletionView(discord.ui.View):
    def __init__(self, bot, user_id, memories_with_indices):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.memories = memories_with_indices
        
        # Create dropdown with memories
        options = []
        for i, mem in enumerate(memories_with_indices[:25]):  # Discord limit is 25 options
            memory_preview = mem['memory'][:80] + "..." if len(mem['memory']) > 80 else mem['memory']
            options.append(discord.SelectOption(
                label=f"Memory {i+1}",
                description=memory_preview,
                value=str(mem['index'])
            ))
        
        if options:
            select = discord.ui.Select(
                placeholder="Choose a memory to delete...",
                options=options,
                custom_id="memory_select"
            )
            select.callback = self.memory_select_callback
            self.add_item(select)
    
    async def memory_select_callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        memory_index = int(interaction.data['values'][0])
        
        # Find the memory to show confirmation
        memory_to_delete = None
        for mem in self.memories:
            if mem['index'] == memory_index:
                memory_to_delete = mem['memory']
                break
        
        if not memory_to_delete:
            await interaction.response.send_message("❌ Memory not found!", ephemeral=True)
            return
        
        # Show confirmation
        embed = discord.Embed(
            title="⚠️ Confirm Memory Deletion",
            description=f"Are you sure you want to delete this memory?\n\n**Memory to delete:**\n*{memory_to_delete}*",
            color=0xFF6B6B
        )
        
        view = MemoryDeletionConfirmView(self.bot, self.user_id, memory_index, memory_to_delete)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class MemoryDeletionConfirmView(discord.ui.View):
    def __init__(self, bot, user_id, memory_index, memory_text):
        super().__init__(timeout=60)  # 1 minute timeout for confirmation
        self.bot = bot
        self.user_id = user_id
        self.memory_index = memory_index
        self.memory_text = memory_text
    
    @discord.ui.button(label="Yes, Delete", emoji="✅", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        # Delete the memory
        success = self.bot.memory.delete_specific_memory(self.user_id, self.memory_index)
        
        if success:
            await self.bot.memory.save_memory()
            
            embed = discord.Embed(
                title="✅ Memory Deleted",
                description=f"Successfully deleted the memory:\n*{self.memory_text}*",
                color=0x00FF7F
            )
            embed.add_field(
                name="💡 Tip",
                value="Use `/memories` to view your remaining memories.",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Deletion Failed",
                description="There was an error deleting the memory. It may have already been removed.",
                color=0xFF6B6B
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Cancel", emoji="❌", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="❌ Deletion Cancelled",
            description="Your memory was not deleted.",
            color=0x95A5A6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class MemoryEditView(discord.ui.View):
    def __init__(self, bot, user_id, memories_with_indices):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.memories = memories_with_indices
        
        # Create dropdown with memories
        options = []
        for i, mem in enumerate(memories_with_indices[:25]):  # Discord limit is 25 options
            memory_preview = mem['memory'][:80] + "..." if len(mem['memory']) > 80 else mem['memory']
            options.append(discord.SelectOption(
                label=f"Memory {i+1}",
                description=memory_preview,
                value=str(mem['index'])
            ))
        
        if options:
            select = discord.ui.Select(
                placeholder="Choose a memory to edit...",
                options=options,
                custom_id="memory_edit_select"
            )
            select.callback = self.memory_select_callback
            self.add_item(select)
    
    async def memory_select_callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        memory_index = int(interaction.data['values'][0])
        
        # Find the memory to edit
        memory_to_edit = None
        for mem in self.memories:
            if mem['index'] == memory_index:
                memory_to_edit = mem['memory']
                break
        
        if not memory_to_edit:
            await interaction.response.send_message("❌ Memory not found!", ephemeral=True)
            return
        
        # Show modal for editing
        modal = MemoryEditModal(self.bot, self.user_id, memory_index, memory_to_edit)
        await interaction.response.send_modal(modal)

class MemoryEditModal(discord.ui.Modal, title="Edit Memory"):
    def __init__(self, bot, user_id, memory_index, current_memory):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.memory_index = memory_index
        self.current_memory = current_memory
        
        # Create text input with current memory pre-filled
        self.memory_input = discord.ui.TextInput(
            label="Edit Memory",
            placeholder="Update your memory...",
            style=discord.TextStyle.paragraph,
            max_length=500,
            required=True,
            default=current_memory
        )
        self.add_item(self.memory_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        new_memory = self.memory_input.value.strip()
        
        if not new_memory:
            embed = discord.Embed(
                title="❌ Invalid Memory",
                description="Please enter a valid memory.",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Edit the memory
        success = self.bot.memory.edit_specific_memory(self.user_id, self.memory_index, new_memory)
        
        if success:
            await self.bot.memory.save_memory()
            
            embed = discord.Embed(
                title="✅ Memory Updated",
                description=f"Successfully updated your memory!\n\n**New memory:**\n*{new_memory}*",
                color=0x00FF7F
            )
            embed.add_field(
                name="💡 Tip",
                value="Use `/memories` to view all your updated memories.",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Update Failed",
                description="There was an error updating the memory. It may have been removed.",
                color=0xFF6B6B
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def create_ask_embed(response: str, question: str, user: discord.User, guild: discord.Guild = None, length: str = "medium"):
    """Create an embed for ask command response, handling size limits"""
    # Discord embed limits: total size 6000 chars, description 4096 chars
    max_description_length = 3800  # Leave more room for other fields and safety
    
    # Create title with length indicator
    length_emojis = {
        "short": "⚡",
        "medium": "📝", 
        "long": "📚"
    }
    
    length_names = {
        "short": "Quick Answer",
        "medium": "Detailed Answer",
        "long": "Comprehensive Answer"
    }
    
    # Smart truncation - try to avoid cutting mid-sentence
    if len(response) > max_description_length:
        # Try to find a good breaking point (sentence end)
        truncate_point = max_description_length - 100  # Leave buffer for "..."
        
        # Look for sentence endings near the truncate point
        sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']
        best_break = truncate_point
        
        for ending in sentence_endings:
            last_occurrence = response.rfind(ending, 0, max_description_length - 50)
            if last_occurrence > truncate_point - 200:  # Within reasonable range
                best_break = last_occurrence + len(ending)
                break
        
        response = response[:best_break].rstrip() + "\n\n*[Response truncated due to length limit. For very detailed answers, consider asking more specific questions.]*"
    
    embed = discord.Embed(
        title=f"{length_emojis.get(length, '📝')} Chatore's {length_names.get(length, 'Detailed Answer')}",
        description=response,
        color=0x5865F2,
        timestamp=discord.utils.utcnow()
    )
    
    # Truncate question if too long
    question_display = question
    if len(question) > 200:
        question_display = question[:197] + "..."
    
    embed.add_field(
        name="Your Question",
        value=f"*{question_display}*",
        inline=False
    )
    embed.set_author(
        name="Private Response",
        icon_url=None  # Will be set by the calling function
    )
    
    if guild:
        embed.set_footer(
            text=f"From {guild.name}",
            icon_url=guild.icon.url if guild.icon else None
        )
    else:
        embed.set_footer(text="From Direct Message")
    
    return embed

def create_ask_embeds_multiple(response: str, question: str, user: discord.User, guild: discord.Guild = None, length: str = "medium"):
    """Create multiple embeds for very long responses"""
    max_description_length = 3800
    embeds = []
    
    # If response fits in one embed, use single embed
    if len(response) <= max_description_length:
        return [create_ask_embed(response, question, user, guild, length)]
    
    # Split response into chunks
    chunks = []
    current_chunk = ""
    sentences = response.split('. ')
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Add period back if it's not the last sentence
        if sentence != sentences[-1]:
            sentence += '. '
        
        # Check if adding this sentence would exceed limit
        if len(current_chunk + sentence) > max_description_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # Single sentence is too long, force split
                chunks.append(sentence[:max_description_length])
                current_chunk = sentence[max_description_length:]
        else:
            current_chunk += sentence
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    # Create embeds for each chunk
    length_emojis = {
        "short": "⚡",
        "medium": "📝", 
        "long": "📚"
    }
    
    length_names = {
        "short": "Quick Answer",
        "medium": "Detailed Answer",
        "long": "Comprehensive Answer"
    }
    
    for i, chunk in enumerate(chunks):
        if i == 0:
            # First embed with question
            embed = discord.Embed(
                title=f"{length_emojis.get(length, '📝')} Chatore's {length_names.get(length, 'Detailed Answer')} (Part {i+1}/{len(chunks)})",
                description=chunk,
                color=0x5865F2,
                timestamp=discord.utils.utcnow()
            )
            
            # Truncate question if too long
            question_display = question
            if len(question) > 200:
                question_display = question[:197] + "..."
            
            embed.add_field(
                name="Your Question",
                value=f"*{question_display}*",
                inline=False
            )
        else:
            # Continuation embeds
            embed = discord.Embed(
                title=f"📚 Continued Response (Part {i+1}/{len(chunks)})",
                description=chunk,
                color=0x5865F2,
                timestamp=discord.utils.utcnow()
            )
        
        embed.set_author(
            name="Private Response",
            icon_url=None  # Will be set by the calling function
        )
        
        if guild:
            embed.set_footer(
                text=f"From {guild.name}",
                icon_url=guild.icon.url if guild.icon else None
            )
        else:
            embed.set_footer(text="From Direct Message")
        
        embeds.append(embed)
    
    return embeds

def setup(bot):
    """Setup chat commands"""
    
    @bot.command(name='memory')
    async def add_memory(ctx, *, memory_text):
        """Add a memory about yourself"""
        user_id = str(ctx.author.id)
        
        # Check if user has completed welcome setup
        if not bot.memory.has_completed_welcome_setup(user_id):
            from ..commands.welcome_system import create_welcome_embed, OnboardingView
            
            language = bot.memory.get_user_language(user_id)
            
            if language == 'hinglish':
                redirect_embed = discord.Embed(
                    title="🔄 Pehle Setup Complete Kar!",
                    description="Arrey bhai, memory add karne se pehle mujhe tere baare mein jaanna padega!\n\nPehle welcome setup complete kar, phir memories add kar sakta hai.",
                    color=0xFF9933
                )
                redirect_embed.add_field(
                    name="🚀 Kya karna hai?",
                    value="Neeche 'Start Welcome Setup' button click kar aur 2-3 minutes mein setup complete kar!",
                    inline=False
                )
            else:
                redirect_embed = discord.Embed(
                    title="🔄 Complete Setup First!",
                    description="Hey there! Before you can add memories, I need to get to know you first!\n\nPlease complete the welcome setup, then you can add memories.",
                    color=0xFF9933
                )
                redirect_embed.add_field(
                    name="🚀 What to do?",
                    value="Click the 'Start Welcome Setup' button below and complete the 2-3 minute setup!",
                    inline=False
                )
            
            redirect_embed.add_field(
                name="💡 Why Setup?",
                value="The setup helps me understand your preferences, interests, and how to chat with you better!",
                inline=False
            )
            redirect_embed.add_field(
                name="📝 Your Memory Will Be Saved",
                value=f"Don't worry! After setup, I'll remember: *{memory_text}*",
                inline=False
            )
            
            # Create welcome setup button
            class WelcomeRedirectView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                
                @discord.ui.button(label="Start Welcome Setup", emoji="🚀", style=discord.ButtonStyle.primary)
                async def start_welcome(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    if str(button_interaction.user.id) != user_id:
                        await button_interaction.response.send_message("❌ This setup is not for you!", ephemeral=True)
                        return
                    
                    # Save the memory they wanted to add for after setup
                    bot.memory.add_user_memory(user_id, f"[Pre-setup memory]: {memory_text}")
                    
                    embed = create_welcome_embed(bot, button_interaction.user)
                    view = OnboardingView(bot, button_interaction.user.id, button_interaction.user)
                    await button_interaction.response.edit_message(embed=embed, view=view)
                    view.message = await button_interaction.original_response()
            
            await ctx.reply(embed=redirect_embed, view=WelcomeRedirectView())
            return
        
        bot.memory.add_user_memory(user_id, memory_text)
        await bot.memory.save_memory()
        
        embed = discord.Embed(
            title="Memory Saved! 🧠",
            description=f"I'll remember that: *{memory_text}*",
            color=0x00FF7F
        )
        embed.set_footer(text=f"Memory added for {ctx.author.display_name}")
        await ctx.reply(embed=embed)

    @bot.command(name='forget')
    async def forget_user(ctx):
        """Clear your memories and conversation history"""
        user_id = str(ctx.author.id)
        bot.memory.clear_user_data(user_id)
        await bot.memory.save_memory()
        
        embed = discord.Embed(
            title="Memory Cleared! 🗑️",
            description="I've forgotten everything about you. We can start fresh!",
            color=0xFFD700
        )
        await ctx.reply(embed=embed)

    @bot.command(name='memories')
    async def show_memories(ctx):
        """Show what the bot remembers about you"""
        user_id = str(ctx.author.id)
        
        # Check if user has completed welcome setup
        if not bot.memory.has_completed_welcome_setup(user_id):
            from ..commands.welcome_system import create_welcome_embed, OnboardingView
            
            language = bot.memory.get_user_language(user_id)
            
            if language == 'hinglish':
                redirect_embed = discord.Embed(
                    title="🔄 Pehle Setup Complete Kar!",
                    description="Arrey bhai, memories dekhne se pehle mujhe tere baare mein jaanna padega!\n\nPehle welcome setup complete kar, phir memories access kar sakta hai.",
                    color=0xFF9933
                )
                redirect_embed.add_field(
                    name="🚀 Kya karna hai?",
                    value="Neeche 'Start Welcome Setup' button click kar aur 2-3 minutes mein setup complete kar!",
                    inline=False
                )
            else:
                redirect_embed = discord.Embed(
                    title="🔄 Complete Setup First!",
                    description="Hey there! Before you can view your memories, I need to get to know you first!\n\nPlease complete the welcome setup, then you can access your memories.",
                    color=0xFF9933
                )
                redirect_embed.add_field(
                    name="🚀 What to do?",
                    value="Click the 'Start Welcome Setup' button below and complete the 2-3 minute setup!",
                    inline=False
                )
            
            redirect_embed.add_field(
                name="💡 Why Setup?",
                value="The setup helps me understand your preferences, interests, and how to chat with you better!",
                inline=False
            )
            
            # Create welcome setup button
            class WelcomeRedirectView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                
                @discord.ui.button(label="Start Welcome Setup", emoji="🚀", style=discord.ButtonStyle.primary)
                async def start_welcome(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    if str(button_interaction.user.id) != user_id:
                        await button_interaction.response.send_message("❌ This setup is not for you!", ephemeral=True)
                        return
                    
                    embed = create_welcome_embed(bot, button_interaction.user)
                    view = OnboardingView(bot, button_interaction.user.id, button_interaction.user)
                    await button_interaction.response.edit_message(embed=embed, view=view)
                    view.message = await button_interaction.original_response()
            
            await ctx.reply(embed=redirect_embed, view=WelcomeRedirectView())
            return
        
        embed = discord.Embed(
            title=f"What I Remember About {ctx.author.display_name} 📝",
            color=0x9B59B6
        )
        
        if user_id in bot.memory.user_memories and bot.memory.user_memories[user_id]:
            memories = bot.memory.user_memories[user_id]
            memory_text = "\n".join([f"• {m['memory']}" for m in memories[-5:]])  # Show last 5
            embed.add_field(name="Memories", value=memory_text, inline=False)
        else:
            embed.add_field(name="Memories", value="Nothing yet! Use `!memory <text>` to tell me about yourself.", inline=False)
        
        if user_id in bot.memory.conversation_history and bot.memory.conversation_history[user_id]:
            convo_count = len(bot.memory.conversation_history[user_id])
            embed.add_field(name="Conversations", value=f"We've had {convo_count} recent conversations", inline=False)
        
        await ctx.reply(embed=embed)

    @bot.command(name='ask')
    async def ask_question(ctx, *, question):
        """Ask Luna a formal question (response sent privately to you)"""
        try:
            # Delete the original command message for privacy
            try:
                await ctx.message.delete()
            except:
                pass  # Ignore if we can't delete (permissions)
            
            # Send a brief acknowledgment in the channel
            ack_embed = discord.Embed(
                description=f"📨 {ctx.author.mention}, I'm processing your question privately...",
                color=0x5865F2
            )
            ack_msg = await ctx.send(embed=ack_embed)
            
            # Process the question
            user_id = str(ctx.author.id)
            
            # Get user context
            context = bot.memory.get_user_context(user_id)
            
            # Get user's language preference for formal responses
            user_language = bot.memory.get_user_language(user_id)
            
            # Create formal personality for !ask command (medium length default)
            if user_language == 'hinglish':
                formal_personality = """
                You are Chatore, ek knowledgeable aur helpful Discord chatbot. Tere baare mein:
                - Tu ek male bot hai, age unknown, Abhinav ne banaya hai tujhe
                - Gaming ka shauk hai aur baaki topics mein bhi accha knowledge hai
                - Tech, memes, internet culture, gaming, aur general topics sab pata hai
                
                For formal questions (like !ask command):
                - Hinglish mein BALANCED answer de good detail ke saath (5-8 sentences, around 400-500 words)
                - Helpful aur informative ho, but apni personality maintain kar
                - Good explanations de, formal nahi but structured
                - Proper formatting use kar but robotic mat ban
                - Key points, examples, aur explanations include kar while organized reh
                - Question ka proper answer de with examples if needed
                """
            else:
                formal_personality = """
                You are Chatore, a knowledgeable and helpful Discord chatbot. About you:
                - You're a male bot, age unknown, created by Abhinav
                - You love gaming and have good knowledge about various topics
                - You're knowledgeable about tech, memes, internet culture, gaming, and general topics
                
                For formal questions (like !ask command):
                - Provide a BALANCED answer with good detail (5-8 sentences, around 400-500 words)
                - Be helpful and informative while maintaining your personality
                - Give good explanations that are structured but not robotic
                - Use proper formatting and examples when helpful
                - Include key points, examples, and explanations while staying organized
                - Focus on giving a complete, useful answer to their question
                """
            
            prompt = f"""
            {formal_personality}
            
            {context}
            
            The user asked this formal question: "{question}"
            
            Provide a comprehensive, detailed answer. This is a formal question so give a complete response with proper explanations, examples if helpful, and structure your answer well. Don't worry about length limits - focus on being thorough and helpful.
            """
            
            # Generate response
            response = await bot.generate_response(prompt)
            
            # Create embed for private response with size handling (default to medium for prefix command)
            embeds = [create_ask_embed(response, question, ctx.author, ctx.guild, "medium")]
            # Set the bot avatar for the embed
            embeds[0].set_author(
                name="Private Response",
                icon_url=bot.user.avatar.url if bot.user.avatar else None
            )
            
            # Send private DM
            try:
                await ctx.author.send(embed=embeds[0])
                
                # Update acknowledgment message
                success_embed = discord.Embed(
                    description=f"✅ {ctx.author.mention}, I've sent you a private response!",
                    color=0x00FF7F
                )
                await ack_msg.edit(embed=success_embed)
                
                # Delete acknowledgment after 5 seconds
                await asyncio.sleep(5)
                await ack_msg.delete()
                
            except discord.Forbidden:
                # If DM fails, send in channel but mention it's private
                error_embed = discord.Embed(
                    title="❌ DM Failed",
                    description=f"{ctx.author.mention}, I couldn't send you a DM. Please enable DMs from server members or here's your answer:",
                    color=0xFF6B6B
                )
                await ack_msg.edit(embed=error_embed)
                await ctx.send(embed=embeds[0])
            
            # Note: !ask command responses are NOT saved to memory to keep them private
            
        except Exception as e:
            error_embed = discord.Embed(
                title="Error 😅",
                description="Something went wrong processing your question. Try again!",
                color=0xFF6B6B
            )
            await ctx.send(embed=error_embed)
            print(f"Error in ask command: {e}")

    # Slash Commands
    @bot.tree.command(name="memory", description="Store a permanent memory about yourself")
    @app_commands.describe(memory_text="What would you like me to remember about you?")
    async def slash_memory(interaction: discord.Interaction, memory_text: str):
        """Add a memory about yourself (slash command)"""
        user_id = str(interaction.user.id)
        
        # Check if user has completed welcome setup
        if not bot.memory.has_completed_welcome_setup(user_id):
            from ..commands.welcome_system import create_welcome_embed, OnboardingView
            
            language = bot.memory.get_user_language(user_id)
            
            if language == 'hinglish':
                redirect_embed = discord.Embed(
                    title="🔄 Pehle Setup Complete Kar!",
                    description="Arrey bhai, memory add karne se pehle mujhe tere baare mein jaanna padega!\n\nPehle welcome setup complete kar, phir memories add kar sakta hai.",
                    color=0xFF9933
                )
                redirect_embed.add_field(
                    name="🚀 Kya karna hai?",
                    value="Neeche 'Start Welcome Setup' button click kar aur 2-3 minutes mein setup complete kar!",
                    inline=False
                )
            else:
                redirect_embed = discord.Embed(
                    title="🔄 Complete Setup First!",
                    description="Hey there! Before you can add memories, I need to get to know you first!\n\nPlease complete the welcome setup, then you can add memories.",
                    color=0xFF9933
                )
                redirect_embed.add_field(
                    name="🚀 What to do?",
                    value="Click the 'Start Welcome Setup' button below and complete the 2-3 minute setup!",
                    inline=False
                )
            
            redirect_embed.add_field(
                name="💡 Why Setup?",
                value="The setup helps me understand your preferences, interests, and how to chat with you better!",
                inline=False
            )
            redirect_embed.add_field(
                name="📝 Your Memory Will Be Saved",
                value=f"Don't worry! After setup, I'll remember: *{memory_text}*",
                inline=False
            )
            
            # Create welcome setup button
            class WelcomeRedirectView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                
                @discord.ui.button(label="Start Welcome Setup", emoji="🚀", style=discord.ButtonStyle.primary)
                async def start_welcome(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    if str(button_interaction.user.id) != user_id:
                        await button_interaction.response.send_message("❌ This setup is not for you!", ephemeral=True)
                        return
                    
                    # Save the memory they wanted to add for after setup
                    bot.memory.add_user_memory(user_id, f"[Pre-setup memory]: {memory_text}")
                    
                    embed = create_welcome_embed(bot, button_interaction.user)
                    view = OnboardingView(bot, button_interaction.user.id, button_interaction.user)
                    await button_interaction.response.edit_message(embed=embed, view=view)
                    view.message = await button_interaction.original_response()
            
            await interaction.response.send_message(embed=redirect_embed, view=WelcomeRedirectView())
            return
        
        bot.memory.add_user_memory(user_id, memory_text)
        await bot.memory.save_memory()
        
        embed = discord.Embed(
            title="Memory Saved! 🧠",
            description=f"I'll remember that: *{memory_text}*",
            color=0x00FF7F
        )
        embed.set_footer(text=f"Memory added for {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
        
        # Check for new users and show welcome message
        await bot.check_and_welcome_new_user(interaction)

    @bot.tree.command(name="forget", description="Clear all your memories and conversation history")
    async def slash_forget(interaction: discord.Interaction):
        """Clear your memories and conversation history (slash command)"""
        user_id = str(interaction.user.id)
        bot.memory.clear_user_data(user_id)
        await bot.memory.save_memory()
        
        embed = discord.Embed(
            title="Memory Cleared! 🗑️",
            description="I've forgotten everything about you. We can start fresh!",
            color=0xFFD700
        )
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="memories", description="View what Chatore remembers about you")
    async def slash_memories(interaction: discord.Interaction):
        """Show what the bot remembers about you (slash command)"""
        user_id = str(interaction.user.id)
        
        # Check if user has completed welcome setup
        if not bot.memory.has_completed_welcome_setup(user_id):
            from ..commands.welcome_system import create_welcome_embed, OnboardingView
            
            language = bot.memory.get_user_language(user_id)
            
            if language == 'hinglish':
                redirect_embed = discord.Embed(
                    title="🔄 Pehle Setup Complete Kar!",
                    description="Arrey bhai, memories dekhne se pehle mujhe tere baare mein jaanna padega!\n\nPehle welcome setup complete kar, phir memories access kar sakta hai.",
                    color=0xFF9933
                )
                redirect_embed.add_field(
                    name="🚀 Kya karna hai?",
                    value="Neeche 'Start Welcome Setup' button click kar aur 2-3 minutes mein setup complete kar!",
                    inline=False
                )
            else:
                redirect_embed = discord.Embed(
                    title="🔄 Complete Setup First!",
                    description="Hey there! Before you can view your memories, I need to get to know you first!\n\nPlease complete the welcome setup, then you can access your memories.",
                    color=0xFF9933
                )
                redirect_embed.add_field(
                    name="🚀 What to do?",
                    value="Click the 'Start Welcome Setup' button below and complete the 2-3 minute setup!",
                    inline=False
                )
            
            redirect_embed.add_field(
                name="💡 Why Setup?",
                value="The setup helps me understand your preferences, interests, and how to chat with you better!",
                inline=False
            )
            
            # Create welcome setup button
            class WelcomeRedirectView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)
                
                @discord.ui.button(label="Start Welcome Setup", emoji="🚀", style=discord.ButtonStyle.primary)
                async def start_welcome(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                    if str(button_interaction.user.id) != user_id:
                        await button_interaction.response.send_message("❌ This setup is not for you!", ephemeral=True)
                        return
                    
                    embed = create_welcome_embed(bot, button_interaction.user)
                    view = OnboardingView(bot, button_interaction.user.id, button_interaction.user)
                    await button_interaction.response.edit_message(embed=embed, view=view)
                    view.message = await button_interaction.original_response()
            
            await interaction.response.send_message(embed=redirect_embed, view=WelcomeRedirectView())
            return
        
        embed = discord.Embed(
            title=f"What I Remember About {interaction.user.display_name} 📝",
            color=0x9B59B6
        )
        
        if user_id in bot.memory.user_memories and bot.memory.user_memories[user_id]:
            memories = bot.memory.user_memories[user_id]
            memory_text = "\n".join([f"• {m['memory']}" for m in memories[-5:]])  # Show last 5
            embed.add_field(name="Memories", value=memory_text, inline=False)
        else:
            embed.add_field(name="Memories", value="Nothing yet! Use the button below or `/memory <text>` to tell me about yourself.", inline=False)
        
        if user_id in bot.memory.conversation_history and bot.memory.conversation_history[user_id]:
            convo_count = len(bot.memory.conversation_history[user_id])
            embed.add_field(name="Conversations", value=f"We've had {convo_count} recent conversations", inline=False)
        
        # Always show memory management view (for adding and deleting)
        view = MemoryManagementView(bot, user_id)
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()



    @bot.tree.command(name="ask", description="Ask Chatore a formal question (response sent privately)")
    @app_commands.describe(
        question="What would you like to ask me?",
        length="Choose answer length (default: medium)"
    )
    @app_commands.choices(length=[
        app_commands.Choice(name="Short - Quick and concise (2-3 sentences)", value="short"),
        app_commands.Choice(name="Medium - Balanced detail (4-6 sentences)", value="medium"),
        app_commands.Choice(name="Long - Comprehensive and detailed", value="long")
    ])
    async def slash_ask(interaction: discord.Interaction, question: str, length: app_commands.Choice[str] = None):
        """Ask Chatore a formal question (response sent privately to you) (slash command)"""
        try:
            # Get answer length (default to medium)
            answer_length = length.value if length else "medium"
            
            # Send a brief acknowledgment in the channel (not ephemeral)
            length_text = {
                "short": "short",
                "medium": "medium-length", 
                "long": "detailed"
            }.get(answer_length, "medium-length")
            
            ack_embed = discord.Embed(
                description=f"📨 {interaction.user.mention}, I'm processing your question privately... (preparing {length_text} answer)",
                color=0x5865F2
            )
            await interaction.response.send_message(embed=ack_embed)
            
            # Process the question
            user_id = str(interaction.user.id)
            
            # Get user context
            context = bot.memory.get_user_context(user_id)
            
            # Get user's language preference for formal responses
            user_language = bot.memory.get_user_language(user_id)
            
            # Create formal personality for /ask command with length specifications
            length_instructions = {
                "short": {
                    "english": "Keep your answer SHORT and CONCISE (2-3 sentences max, around 50-100 words). Get straight to the point without unnecessary details.",
                    "hinglish": "Apna answer CHHOTA aur CONCISE rakh (2-3 sentences max, around 50-100 words). Seedha point pe aa, extra details mat de."
                },
                "medium": {
                    "english": "Provide a BALANCED answer with good detail (5-8 sentences, around 400-500 words). Include key points, examples, and explanations while staying organized.",
                    "hinglish": "BALANCED answer de good detail ke saath (5-8 sentences, around 400-500 words). Key points, examples, aur explanations include kar while organized reh."
                },
                "long": {
                    "english": "Give a COMPREHENSIVE and DETAILED answer (10-15 sentences, around 800-1000 words max). Include examples, explanations, thorough coverage, and multiple perspectives, but keep it under 1000 words to avoid truncation.",
                    "hinglish": "COMPREHENSIVE aur DETAILED answer de (10-15 sentences, around 800-1000 words max). Examples, explanations, thorough coverage, aur multiple perspectives include kar, but 1000 words ke under rakh truncation avoid karne ke liye."
                }
            }
            
            if user_language == 'hinglish':
                formal_personality = f"""
                You are Chatore, ek knowledgeable aur helpful Discord chatbot. Tere baare mein:
                - Tu ek male bot hai, age unknown, Abhinav ne banaya hai tujhe
                - Gaming ka shauk hai aur baaki topics mein bhi accha knowledge hai
                - Tech, memes, internet culture, gaming, aur general topics sab pata hai
                
                For formal questions (like /ask command):
                - Hinglish mein answer de
                - Helpful aur informative ho, but apni personality maintain kar
                - Good explanations de, formal nahi but structured
                - Proper formatting use kar but robotic mat ban
                - Question ka proper answer de with examples if needed
                
                IMPORTANT LENGTH REQUIREMENT:
                {length_instructions[answer_length]["hinglish"]}
                """
            else:
                formal_personality = f"""
                You are Chatore, a knowledgeable and helpful Discord chatbot. About you:
                - You're a male bot, age unknown, created by Abhinav
                - You love gaming and have good knowledge about various topics
                - You're knowledgeable about tech, memes, internet culture, gaming, and general topics
                
                For formal questions (like /ask command):
                - Provide answers in English
                - Be helpful and informative while maintaining your personality
                - Give good explanations that are structured but not robotic
                - Use proper formatting and examples when helpful
                - Focus on giving a complete, useful answer to their question
                
                IMPORTANT LENGTH REQUIREMENT:
                {length_instructions[answer_length]["english"]}
                """
            
            prompt = f"""
            {formal_personality}
            
            {context}
            
            The user asked this formal question: "{question}"
            
            Answer according to the length requirement specified above. This is a formal question so provide a well-structured response that matches the requested length ({answer_length}) while being helpful and informative.
            """
            
            # Generate response
            response = await bot.generate_response(prompt)
            
            # Create embed(s) for private response with size handling
            if answer_length == "long" and len(response) > 3800:
                # Use multiple embeds for long responses
                embeds = create_ask_embeds_multiple(response, question, interaction.user, interaction.guild, answer_length)
                # Set the bot avatar for all embeds
                for embed in embeds:
                    embed.set_author(
                        name="Private Response",
                        icon_url=bot.user.avatar.url if bot.user.avatar else None
                    )
            else:
                # Use single embed
                embeds = [create_ask_embed(response, question, interaction.user, interaction.guild, answer_length)]
                # Set the bot avatar for the embed
                embeds[0].set_author(
                    name="Private Response",
                    icon_url=bot.user.avatar.url if bot.user.avatar else None
                )
            
            # Send private DM(s)
            try:
                # Send first embed
                await interaction.user.send(embed=embeds[0])
                
                # Send additional embeds if any
                for embed in embeds[1:]:
                    await interaction.user.send(embed=embed)
                
                # Update acknowledgment message
                success_embed = discord.Embed(
                    description=f"✅ {interaction.user.mention}, I've sent you a private response!",
                    color=0x00FF7F
                )
                await interaction.edit_original_response(embed=success_embed)
                
                # Delete acknowledgment after 5 seconds
                await asyncio.sleep(5)
                await interaction.delete_original_response()
                
            except discord.Forbidden:
                # If DM fails, send in channel but mention it's private
                error_embed = discord.Embed(
                    title="❌ DM Failed",
                    description=f"{interaction.user.mention}, I couldn't send you a DM. Please enable DMs from server members or here's your answer:",
                    color=0xFF6B6B
                )
                await interaction.edit_original_response(embed=error_embed)
                
                # Send all embeds in channel
                for embed in embeds:
                    await interaction.followup.send(embed=embed)
            
            # Note: /ask command responses are NOT saved to memory to keep them private
            
        except Exception as e:
            error_embed = discord.Embed(
                title="Error 😅",
                description="Something went wrong processing your question. Try again!",
                color=0xFF6B6B
            )
            try:
                await interaction.edit_original_response(embed=error_embed)
            except:
                await interaction.followup.send(embed=error_embed)
            print(f"Error in slash ask command: {e}")

    @bot.tree.command(name="delete_memory", description="Delete a specific memory from your stored memories")
    async def slash_delete_memory(interaction: discord.Interaction):
        """Delete a specific memory (slash command)"""
        user_id = str(interaction.user.id)
        
        # Get memories with indices
        memories_with_indices = bot.memory.get_user_memories_with_indices(user_id)
        
        if not memories_with_indices:
            embed = discord.Embed(
                title="❌ No Memories Found",
                description="You don't have any memories stored yet! Use `/memory <text>` to add some.",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create dropdown for memory selection
        view = MemoryDeletionView(bot, user_id, memories_with_indices)
        embed = discord.Embed(
            title="🗑️ Delete Specific Memory",
            description="Select which memory you'd like to delete from the dropdown below:",
            color=0xFF6B6B
        )
        
        # Show memories with numbers
        memory_list = []
        for i, mem in enumerate(memories_with_indices[:10]):  # Show max 10
            memory_preview = mem['memory'][:50] + "..." if len(mem['memory']) > 50 else mem['memory']
            memory_list.append(f"**{i+1}.** {memory_preview}")
        
        embed.add_field(
            name="Your Memories",
            value="\n".join(memory_list),
            inline=False
        )
        
        if len(memories_with_indices) > 10:
            embed.add_field(
                name="📝 Note",
                value=f"Showing first 10 of {len(memories_with_indices)} memories. All memories are available in the dropdown.",
                inline=False
            )
        
        embed.add_field(
            name="⚠️ Warning",
            value="Deleted memories cannot be recovered!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)