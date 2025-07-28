"""
Utility Commands - Bot information and utility functions
"""

import discord
from discord.ext import commands
from discord import app_commands
from .personality_commands import PersonalityCustomizationView

class PersonalityView(discord.ui.View):
    def __init__(self, bot, user_id, has_custom):
        super().__init__(timeout=30)  # 30 second timeout
        self.bot = bot
        self.user_id = user_id
        self.has_custom = has_custom
        self.message = None  # Store message for timeout updates
    
    @discord.ui.button(label="Customize Personality", emoji="🎨", style=discord.ButtonStyle.primary, row=0)
    async def customize_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This personality menu is not for you!", ephemeral=True)
            return
        
        # Start personality customization
        customization_view = PersonalityCustomizationView(self.bot, self.user_id)
        embed = customization_view.get_welcome_embed()
        await interaction.response.edit_message(embed=embed, view=customization_view)
    
    @discord.ui.button(label="Manage Presets", emoji="💾", style=discord.ButtonStyle.secondary, row=0)
    async def presets_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This personality menu is not for you!", ephemeral=True)
            return
        
        # Show preset management
        preset_view = PersonalityPresetView(self.bot, self.user_id)
        embed = preset_view.get_preset_embed()
        await interaction.response.send_message(embed=embed, view=preset_view, ephemeral=True)
    
    @discord.ui.button(label="Edit Personality", emoji="✏️", style=discord.ButtonStyle.secondary, row=1)
    async def edit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This personality menu is not for you!", ephemeral=True)
            return
        
        if not self.has_custom:
            await interaction.response.send_message("❌ You don't have a custom personality to edit! Create one first.", ephemeral=True)
            return
        
        # Show personality edit options
        edit_view = PersonalityEditView(self.bot, self.user_id)
        embed = edit_view.get_edit_embed()
        await interaction.response.send_message(embed=embed, view=edit_view, ephemeral=True)
    
    @discord.ui.button(label="Reset to Default", emoji="🔄", style=discord.ButtonStyle.secondary, row=1)
    async def reset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This personality menu is not for you!", ephemeral=True)
            return
        
        if not self.has_custom:
            await interaction.response.send_message("❌ You don't have a custom personality to reset!", ephemeral=True)
            return
        
        # Reset personality
        success = self.bot.personality_manager.reset_personality(str(self.user_id))
        
        if success:
            await self.bot.personality_manager.save_personalities()
            
            embed = discord.Embed(
                title="🔄 Personality Reset",
                description="Your custom personality has been reset to default. I'm back to my original self!",
                color=0x00FF7F
            )
            embed.add_field(
                name="✅ What Changed",
                value="• Returned to default Chatore personality\n• All custom traits removed\n• Original speaking style restored",
                inline=False
            )
            embed.set_footer(text="You can customize me again anytime using the button above!")
            
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title="❌ Reset Failed",
                description="There was an error resetting your personality. Please try again.",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def on_timeout(self):
        """Handle timeout - disable all components and update message"""
        for item in self.children:
            item.disabled = True
        
        # Create timeout embed
        embed = discord.Embed(
            title="⏰ Personality Menu Timed Out",
            description="This personality menu has expired after 30 seconds of inactivity.",
            color=0x95A5A6
        )
        embed.add_field(
            name="💡 Need Help Again?",
            value="Use `/personality` to open a new personality menu anytime!",
            inline=False
        )
        embed.set_footer(text="Menu expired • Use /personality for a new one")
        
        # Try to edit the message to show timeout
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except (discord.NotFound, discord.Forbidden, Exception):
                pass

class PersonalityPresetView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
    
    def get_preset_embed(self):
        """Get embed showing available presets"""
        embed = discord.Embed(
            title="💾 Personality Presets",
            description="Save and load different personality configurations!",
            color=0x9B59B6
        )
        
        # Get user's presets
        presets = self.bot.personality_manager.get_user_presets(str(self.user_id))
        preset_count = len(presets)
        
        if presets:
            preset_list = []
            for name, data in list(presets.items())[:10]:  # Show max 10
                saved_date = data.get('saved_at', 'Unknown')[:10] if data.get('saved_at') else 'Unknown'
                preset_list.append(f"**{name}** - Saved: {saved_date}")
            
            embed.add_field(
                name=f"📋 Your Saved Presets ({preset_count}/5)",
                value="\n".join(preset_list),
                inline=False
            )
        else:
            embed.add_field(
                name="📋 Your Saved Presets (0/5)",
                value="No presets saved yet. Create a custom personality first, then save it as a preset!",
                inline=False
            )
        
        embed.add_field(
            name="💡 How Presets Work",
            value="• **Save**: Save your current personality as a preset (max 5)\n• **Load**: Switch to a saved preset instantly\n• **Delete**: Remove presets you no longer need",
            inline=False
        )
        
        if preset_count >= 5:
            embed.add_field(
                name="⚠️ Preset Limit Reached",
                value="You have reached the maximum of 5 presets. Delete an existing preset to save a new one.",
                inline=False
            )
        
        return embed
    
    @discord.ui.button(label="Save Current as Preset", emoji="💾", style=discord.ButtonStyle.primary)
    async def save_preset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        # Check if user has a custom personality
        if not self.bot.personality_manager.has_custom_personality(str(self.user_id)):
            embed = discord.Embed(
                title="❌ No Custom Personality",
                description="You need to create a custom personality first before saving it as a preset!",
                color=0xFF6B6B
            )
            embed.add_field(
                name="💡 How to Create",
                value="Use the 'Customize Personality' button in `/personality` to create your custom personality first.",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Show modal to get preset name
        modal = PresetSaveModal(self.bot, self.user_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Load Preset", emoji="📂", style=discord.ButtonStyle.secondary)
    async def load_preset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        presets = self.bot.personality_manager.get_user_presets(str(self.user_id))
        
        if not presets:
            embed = discord.Embed(
                title="❌ No Presets Found",
                description="You don't have any saved presets yet!",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create dropdown for preset selection
        view = PresetLoadView(self.bot, self.user_id, presets)
        embed = discord.Embed(
            title="📂 Load Personality Preset",
            description="Select which preset you'd like to load:",
            color=0x00AFF4
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Delete Preset", emoji="🗑️", style=discord.ButtonStyle.danger)
    async def delete_preset_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        presets = self.bot.personality_manager.get_user_presets(str(self.user_id))
        
        if not presets:
            embed = discord.Embed(
                title="❌ No Presets Found",
                description="You don't have any saved presets to delete!",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Create dropdown for preset deletion
        view = PresetDeleteView(self.bot, self.user_id, presets)
        embed = discord.Embed(
            title="🗑️ Delete Personality Preset",
            description="Select which preset you'd like to delete:",
            color=0xFF6B6B
        )
        embed.add_field(
            name="⚠️ Warning",
            value="Deleted presets cannot be recovered!",
            inline=False
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PresetSaveModal(discord.ui.Modal, title="Save Personality Preset"):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
    
    preset_name = discord.ui.TextInput(
        label="Preset Name",
        placeholder="Enter a name for this preset (e.g., 'Funny Mode', 'Serious Helper')",
        style=discord.TextStyle.short,
        max_length=50,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        name = self.preset_name.value.strip()
        
        if not name:
            embed = discord.Embed(
                title="❌ Invalid Name",
                description="Please enter a valid preset name.",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Save the preset
        result = self.bot.personality_manager.save_personality_preset(str(self.user_id), name)
        
        if result == True:
            await self.bot.personality_manager.save_personalities()
            
            embed = discord.Embed(
                title="💾 Preset Saved!",
                description=f"Your current personality has been saved as preset: **{name}**",
                color=0x00FF7F
            )
            embed.add_field(
                name="✅ What's Next?",
                value="• You can now load this preset anytime\n• Create different personalities and save them as presets\n• Switch between presets instantly!",
                inline=False
            )
        elif result == "limit_exceeded":
            embed = discord.Embed(
                title="❌ Preset Limit Reached",
                description=f"You can only save up to **5 presets**. Please delete an existing preset first.",
                color=0xFF6B6B
            )
            embed.add_field(
                name="💡 What You Can Do",
                value="• Delete an old preset you no longer need\n• Overwrite an existing preset by using the same name\n• Use the 'Delete Preset' option to make room",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Save Failed",
                description="There was an error saving your preset. Please try again.",
                color=0xFF6B6B
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class PresetLoadView(discord.ui.View):
    def __init__(self, bot, user_id, presets):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        
        # Create dropdown with presets
        options = []
        for name, data in list(presets.items())[:25]:  # Discord limit is 25 options
            saved_date = data.get('saved_at', 'Unknown')[:10] if data.get('saved_at') else 'Unknown'
            options.append(discord.SelectOption(
                label=name,
                description=f"Saved: {saved_date}",
                value=name
            ))
        
        if options:
            select = discord.ui.Select(
                placeholder="Choose a preset to load...",
                options=options,
                custom_id="preset_select"
            )
            select.callback = self.preset_select_callback
            self.add_item(select)
    
    async def preset_select_callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        preset_name = interaction.data['values'][0]
        
        # Load the preset
        success = self.bot.personality_manager.load_personality_preset(str(self.user_id), preset_name)
        
        if success:
            await self.bot.personality_manager.save_personalities()
            
            embed = discord.Embed(
                title="📂 Preset Loaded!",
                description=f"Successfully loaded preset: **{preset_name}**",
                color=0x00FF7F
            )
            embed.add_field(
                name="✅ What Changed",
                value="• Your personality has been updated to match the preset\n• All preset settings are now active\n• Start chatting to see the changes!",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Load Failed",
                description="There was an error loading the preset. Please try again.",
                color=0xFF6B6B
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class PresetDeleteView(discord.ui.View):
    def __init__(self, bot, user_id, presets):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        
        # Create dropdown with presets
        options = []
        for name, data in list(presets.items())[:25]:  # Discord limit is 25 options
            saved_date = data.get('saved_at', 'Unknown')[:10] if data.get('saved_at') else 'Unknown'
            options.append(discord.SelectOption(
                label=name,
                description=f"Saved: {saved_date}",
                value=name
            ))
        
        if options:
            select = discord.ui.Select(
                placeholder="Choose a preset to delete...",
                options=options,
                custom_id="preset_delete_select"
            )
            select.callback = self.preset_delete_callback
            self.add_item(select)
    
    async def preset_delete_callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        preset_name = interaction.data['values'][0]
        
        # Show confirmation
        embed = discord.Embed(
            title="⚠️ Confirm Preset Deletion",
            description=f"Are you sure you want to delete the preset: **{preset_name}**?",
            color=0xFF6B6B
        )
        embed.add_field(
            name="⚠️ Warning",
            value="This action cannot be undone!",
            inline=False
        )
        
        view = PresetDeleteConfirmView(self.bot, self.user_id, preset_name)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class PresetDeleteConfirmView(discord.ui.View):
    def __init__(self, bot, user_id, preset_name):
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.preset_name = preset_name
    
    @discord.ui.button(label="Yes, Delete", emoji="✅", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        # Delete the preset
        success = self.bot.personality_manager.delete_personality_preset(str(self.user_id), self.preset_name)
        
        if success:
            await self.bot.personality_manager.save_personalities()
            
            embed = discord.Embed(
                title="✅ Preset Deleted",
                description=f"Successfully deleted preset: **{self.preset_name}**",
                color=0x00FF7F
            )
        else:
            embed = discord.Embed(
                title="❌ Deletion Failed",
                description="There was an error deleting the preset. It may have already been removed.",
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
            description="Your preset was not deleted.",
            color=0x95A5A6
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class PersonalityEditView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
    
    def get_edit_embed(self):
        """Get embed for personality editing options"""
        embed = discord.Embed(
            title="✏️ Edit Your Personality",
            description="Choose which aspect of your personality you'd like to edit:",
            color=0xFFD700
        )
        
        # Get current personality data
        summary = self.bot.personality_manager.get_personality_summary(str(self.user_id))
        
        if summary:
            current_info = []
            if summary.get('age'):
                current_info.append(f"**Age**: {summary['age']} years old")
            if summary.get('traits'):
                current_info.append(f"**Traits**: {', '.join(summary['traits'][:3])}{'...' if len(summary['traits']) > 3 else ''}")
            if summary.get('interests'):
                current_info.append(f"**Interests**: {', '.join(summary['interests'][:3])}{'...' if len(summary['interests']) > 3 else ''}")
            if summary.get('speaking_style'):
                current_info.append(f"**Speaking**: {summary['speaking_style']}")
            if summary.get('humor_style'):
                current_info.append(f"**Humor**: {summary['humor_style']}")
            
            if current_info:
                embed.add_field(
                    name="📝 Current Settings",
                    value="\n".join(current_info),
                    inline=False
                )
        
        embed.add_field(
            name="✏️ What You Can Edit",
            value="• **Age/Maturity** - How old I should act\n• **Personality Traits** - My behavior characteristics\n• **Interests** - What I'm passionate about\n• **Speaking Style** - How I communicate\n• **Humor Style** - My type of humor\n• **Special Quirks** - Unique behaviors",
            inline=False
        )
        
        embed.set_footer(text="Select what you'd like to edit from the dropdown below")
        return embed
    
    @discord.ui.select(
        placeholder="Choose what to edit...",
        options=[
            discord.SelectOption(label="Age/Maturity", description="Edit how old I should act", emoji="🎂", value="age"),
            discord.SelectOption(label="Personality Traits", description="Edit my behavior traits", emoji="🎭", value="traits"),
            discord.SelectOption(label="Interests", description="Edit what I'm passionate about", emoji="🎯", value="interests"),
            discord.SelectOption(label="Speaking Style", description="Edit how I communicate", emoji="💬", value="speaking"),
            discord.SelectOption(label="Humor Style", description="Edit my type of humor", emoji="😄", value="humor"),
            discord.SelectOption(label="Special Quirks", description="Edit unique behaviors", emoji="✨", value="quirks"),
        ]
    )
    async def edit_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This is not for you!", ephemeral=True)
            return
        
        field_to_edit = select.values[0]
        
        # Get current value
        summary = self.bot.personality_manager.get_personality_summary(str(self.user_id))
        current_value = ""
        
        if summary:
            if field_to_edit == "age":
                current_value = str(summary.get('age', ''))
            elif field_to_edit == "traits":
                current_value = ', '.join(summary.get('traits', []))
            elif field_to_edit == "interests":
                current_value = ', '.join(summary.get('interests', []))
            elif field_to_edit == "speaking":
                current_value = summary.get('speaking_style', '')
            elif field_to_edit == "humor":
                current_value = summary.get('humor_style', '')
            elif field_to_edit == "quirks":
                current_value = summary.get('special_quirks', '')
        
        # Show modal for editing
        modal = PersonalityFieldEditModal(self.bot, self.user_id, field_to_edit, current_value)
        await interaction.response.send_modal(modal)

class PersonalityFieldEditModal(discord.ui.Modal):
    def __init__(self, bot, user_id, field, current_value):
        self.bot = bot
        self.user_id = user_id
        self.field = field
        self.current_value = current_value
        
        # Set modal title based on field
        field_names = {
            "age": "Edit Age/Maturity",
            "traits": "Edit Personality Traits", 
            "interests": "Edit Interests",
            "speaking": "Edit Speaking Style",
            "humor": "Edit Humor Style",
            "quirks": "Edit Special Quirks"
        }
        
        super().__init__(title=field_names.get(field, "Edit Personality"))
        
        # Create appropriate input field
        if field == "age":
            self.field_input = discord.ui.TextInput(
                label="Age/Maturity Level",
                placeholder="How old should I act? (e.g., 20, 25, 30)",
                style=discord.TextStyle.short,
                max_length=3,
                required=False,
                default=current_value
            )
        elif field in ["traits", "interests"]:
            self.field_input = discord.ui.TextInput(
                label=field_names[field].replace("Edit ", ""),
                placeholder="Separate with commas (e.g., funny, helpful, energetic)",
                style=discord.TextStyle.paragraph,
                max_length=300,
                required=False,
                default=current_value
            )
        else:
            self.field_input = discord.ui.TextInput(
                label=field_names[field].replace("Edit ", ""),
                placeholder=f"Describe your preferred {field.replace('_', ' ')}...",
                style=discord.TextStyle.paragraph if field == "quirks" else discord.TextStyle.short,
                max_length=200 if field == "quirks" else 100,
                required=False,
                default=current_value
            )
        
        self.add_item(self.field_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        new_value = self.field_input.value.strip()
        
        # Process the value based on field type
        if self.field == "age":
            if new_value:
                try:
                    age = int(new_value)
                    if not (13 <= age <= 100):
                        raise ValueError("Age out of range")
                    processed_value = age
                except ValueError:
                    embed = discord.Embed(
                        title="❌ Invalid Age",
                        description="Please enter a valid age between 13 and 100.",
                        color=0xFF6B6B
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
            else:
                processed_value = None
        elif self.field in ["traits", "interests"]:
            if new_value:
                processed_value = [item.strip() for item in new_value.replace(',', '\n').replace(';', '\n').split('\n') if item.strip()][:8]
            else:
                processed_value = []
        else:
            processed_value = new_value if new_value else None
        
        # Map field names to personality manager field names
        field_mapping = {
            "age": "age",
            "traits": "traits",
            "interests": "interests", 
            "speaking": "speaking_style",
            "humor": "humor_style",
            "quirks": "special_quirks"
        }
        
        # Update the personality field
        success = self.bot.personality_manager.update_personality_field(
            str(self.user_id), 
            field_mapping[self.field], 
            processed_value
        )
        
        if success:
            await self.bot.personality_manager.save_personalities()
            
            embed = discord.Embed(
                title="✅ Personality Updated",
                description=f"Successfully updated your {self.field.replace('_', ' ')}!",
                color=0x00FF7F
            )
            
            if processed_value:
                if isinstance(processed_value, list):
                    display_value = ', '.join(processed_value)
                else:
                    display_value = str(processed_value)
                
                embed.add_field(
                    name="📝 New Value",
                    value=f"*{display_value}*",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📝 Change",
                    value="Field cleared (using default)",
                    inline=False
                )
            
            embed.add_field(
                name="💡 Tip",
                value="Start chatting to see your personality changes in action!",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Update Failed",
                description="There was an error updating your personality. Please try again.",
                color=0xFF6B6B
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    """Setup utility commands"""
    
    @bot.command(name='personality')
    async def show_personality(ctx):
        """Show Chatore's personality with customization options for premium users"""
        user_id = str(ctx.author.id)
        tier = bot.tier_manager.get_user_tier(user_id)
        has_custom = bot.personality_manager.has_custom_personality(user_id)
        
        if tier == 'premium' and has_custom:
            # Show custom personality
            custom_summary = bot.personality_manager.get_personality_summary(user_id)
            
            embed = discord.Embed(
                title="🎨 Your Custom Chatore",
                description="You've customized my personality! Here's how I'm configured for you:",
                color=0xFFD700
            )
            
            if custom_summary['name']:
                embed.add_field(
                    name="🏷️ Name/Identity",
                    value=custom_summary['name'],
                    inline=True
                )
            
            if custom_summary['age']:
                embed.add_field(
                    name="🎂 Age/Maturity",
                    value=f"{custom_summary['age']} years old",
                    inline=True
                )
            
            if custom_summary['traits']:
                embed.add_field(
                    name="🎭 Personality Traits",
                    value=", ".join(custom_summary['traits'][:5]) + ("..." if len(custom_summary['traits']) > 5 else ""),
                    inline=False
                )
            
            if custom_summary['interests']:
                embed.add_field(
                    name="🎯 Interests",
                    value=", ".join(custom_summary['interests'][:5]) + ("..." if len(custom_summary['interests']) > 5 else ""),
                    inline=False
                )
            
            if custom_summary['speaking_style']:
                embed.add_field(
                    name="💬 Speaking Style",
                    value=custom_summary['speaking_style'],
                    inline=True
                )
            
            if custom_summary['humor_style']:
                embed.add_field(
                    name="😄 Humor Style",
                    value=custom_summary['humor_style'],
                    inline=True
                )
            
            if custom_summary['special_quirks']:
                embed.add_field(
                    name="✨ Special Quirks",
                    value=custom_summary['special_quirks'][:100] + ("..." if len(custom_summary['special_quirks']) > 100 else ""),
                    inline=False
                )
            
            embed.set_footer(text=f"⭐ Premium Feature • Customized on {custom_summary['created_at'][:10]}")
            
        else:
            # Show default personality
            embed = discord.Embed(
                title="About Chatore 🍽️",
                description="Hey there! I'm Chatore, your friendly AI companion!",
                color=0x7289DA
            )
            
            embed.add_field(
                name="About Me",
                value="• Male bot created by Abhinav 👨‍💻\n• Age: Unknown (but I'm timeless! ⏰)\n• Love gaming and have knowledge about various topics 🎮\n• Speak both English and Hinglish 🌐",
                inline=False
            )
            
            embed.add_field(
                name="Personality Traits",
                value="• Friendly and witty 😄\n• Good sense of humor 😂\n• Remembers our conversations 🧠\n• Loves gaming and tech 🎮\n• Always here to help! 💪",
                inline=False
            )
            
            embed.add_field(
                name="What I Can Do",
                value="• Chat about anything!\n• Remember things about you\n• Help with questions\n• Share memes and jokes\n• Be your digital friend! 🤖💙",
                inline=False
            )
            
            if tier == 'premium':
                embed.add_field(
                    name="⭐ Premium Feature Available",
                    value="As a Premium user, you can customize my personality!\nUse the buttons below to get started.",
                    inline=False
                )
        
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        
        # Add buttons for premium users
        if tier == 'premium':
            view = PersonalityView(bot, ctx.author.id, has_custom)
            await ctx.reply(embed=embed, view=view)
        else:
            await ctx.reply(embed=embed)

    @bot.command(name='ping')
    async def ping(ctx):
        """Check bot latency"""
        latency = round(bot.latency * 1000)
        
        if latency < 100:
            color = 0x00FF00  # Green
            status = "Excellent! 🚀"
        elif latency < 200:
            color = 0xFFFF00  # Yellow
            status = "Good! 👍"
        else:
            color = 0xFF0000  # Red
            status = "Slow... 🐌"
        
        embed = discord.Embed(
            title="Pong! 🏓",
            description=f"**Latency:** {latency}ms\n**Status:** {status}",
            color=color
        )
        await ctx.reply(embed=embed)

    @bot.command(name='stats')
    async def bot_stats(ctx):
        """Show bot statistics"""
        stats = bot.memory.get_stats()
        
        embed = discord.Embed(
            title="Chatore's Stats 📊",
            color=0xE91E63
        )
        
        embed.add_field(name="Users I Know", value=f"{stats['total_users']} people", inline=True)
        embed.add_field(name="Total Messages", value=f"{stats['total_conversations']} messages", inline=True)
        embed.add_field(name="Memories Stored", value=f"{stats['total_memories']} memories", inline=True)
        embed.add_field(name="Servers", value=f"{len(bot.guilds)} servers", inline=True)
        embed.add_field(name="Uptime", value="Since last restart", inline=True)
        
        embed.set_footer(text="Thanks for chatting with me! 💙")
        await ctx.reply(embed=embed)
    

    
    @bot.command(name='activity')
    async def user_activity(ctx):
        """Check your last activity and memory cleanup status"""
        user_id = str(ctx.author.id)
        
        # Get tier information
        tier = bot.tier_manager.get_user_tier(user_id)
        context_limit = bot.tier_manager.get_context_limit(user_id)
        
        embed = discord.Embed(
            title="📊 Your Activity Status",
            color=0xFFD700 if tier == 'premium' else 0x00AFF4
        )
        
        if user_id in bot.memory.user_last_activity:
            from datetime import datetime
            last_activity = datetime.fromisoformat(bot.memory.user_last_activity[user_id])
            time_diff = datetime.now() - last_activity
            hours_inactive = time_diff.total_seconds() / 3600
            
            embed.add_field(
                name="Last Activity",
                value=f"{last_activity.strftime('%Y-%m-%d %H:%M:%S')}",
                inline=False
            )
            
            embed.add_field(
                name="Inactive Duration",
                value=f"{hours_inactive:.1f} hours",
                inline=True
            )
            
            # Check message count with tier info
            msg_count = len(bot.memory.conversation_history.get(user_id, []))
            embed.add_field(
                name="Messages Stored",
                value=f"{msg_count}/25 (Context: {context_limit})",
                inline=True
            )
            
            embed.add_field(
                name="Current Tier",
                value=f"{'⭐ Premium' if tier == 'premium' else '🆓 Free'}",
                inline=True
            )
            
            if hours_inactive >= 3:
                embed.add_field(
                    name="⚠️ Memory Status",
                    value="Your message history will be reduced to 3 messages due to inactivity (3+ hours)",
                    inline=False
                )
                embed.color = 0xFF9933
            else:
                embed.add_field(
                    name="✅ Memory Status",
                    value=f"Active user - {context_limit} message context ({'⭐ Premium' if tier == 'premium' else '🆓 Free'} tier)",
                    inline=False
                )
                embed.color = 0xFFD700 if tier == 'premium' else 0x00FF7F
        else:
            embed.description = "No activity recorded yet."
            embed.color = 0x95A5A6
        
        embed.add_field(
            name="Memory Cleanup Rules",
            value="• Active users: 12 messages stored\n• Inactive 3+ hours: Only 3 messages stored\n• Permanent memories never deleted",
            inline=False
        )
        
        await ctx.reply(embed=embed)
    
    @bot.command(name='invite')
    async def invite(ctx):
        """Show bot invite link"""
        embed = discord.Embed(
            title="Click Below Button To Invite Me",
            color=0x00AFF4
        )
        
        embed.add_field(
            name="🔗 Invite Link",
            value="[Click here to invite Chatore!](https://discord.com/oauth2/authorize?client_id=1397146788577673276)",
            inline=False
        )
        
        await ctx.reply(embed=embed)

    # Slash Commands
    @bot.tree.command(name="personality", description="Learn about Chatore's personality and traits")
    async def slash_personality(interaction: discord.Interaction):
        """Show Chatore's personality with customization options for premium users (slash command)"""
        user_id = str(interaction.user.id)
        
        # Check if user has completed welcome setup
        if not bot.memory.has_completed_welcome_setup(user_id):
            from ..commands.welcome_system import create_welcome_embed, OnboardingView
            
            language = bot.memory.get_user_language(user_id)
            
            if language == 'hinglish':
                redirect_embed = discord.Embed(
                    title="🔄 Pehle Setup Complete Kar!",
                    description="Arrey bhai, personality customize karne se pehle mujhe tere baare mein jaanna padega!\n\nPehle welcome setup complete kar, phir personality features access kar sakta hai.",
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
                    description="Hey there! Before you can customize my personality, I need to get to know you first!\n\nPlease complete the welcome setup, then you can access personality features.",
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
                name="🎨 After Setup",
                value="Once complete, you'll be able to view my personality and customize it (Premium feature)!",
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
        
        tier = bot.tier_manager.get_user_tier(user_id)
        has_custom = bot.personality_manager.has_custom_personality(user_id)
        
        if tier == 'premium' and has_custom:
            # Show custom personality
            custom_summary = bot.personality_manager.get_personality_summary(user_id)
            
            embed = discord.Embed(
                title="🎨 Your Custom Chatore",
                description="You've customized my personality! Here's how I'm configured for you:",
                color=0xFFD700
            )
            
            if custom_summary['name']:
                embed.add_field(
                    name="🏷️ Name/Identity",
                    value=custom_summary['name'],
                    inline=True
                )
            
            if custom_summary['age']:
                embed.add_field(
                    name="🎂 Age/Maturity",
                    value=f"{custom_summary['age']} years old",
                    inline=True
                )
            
            if custom_summary['traits']:
                embed.add_field(
                    name="🎭 Personality Traits",
                    value=", ".join(custom_summary['traits'][:5]) + ("..." if len(custom_summary['traits']) > 5 else ""),
                    inline=False
                )
            
            if custom_summary['interests']:
                embed.add_field(
                    name="🎯 Interests",
                    value=", ".join(custom_summary['interests'][:5]) + ("..." if len(custom_summary['interests']) > 5 else ""),
                    inline=False
                )
            
            if custom_summary['speaking_style']:
                embed.add_field(
                    name="💬 Speaking Style",
                    value=custom_summary['speaking_style'],
                    inline=True
                )
            
            if custom_summary['humor_style']:
                embed.add_field(
                    name="😄 Humor Style",
                    value=custom_summary['humor_style'],
                    inline=True
                )
            
            if custom_summary['special_quirks']:
                embed.add_field(
                    name="✨ Special Quirks",
                    value=custom_summary['special_quirks'][:100] + ("..." if len(custom_summary['special_quirks']) > 100 else ""),
                    inline=False
                )
            
            embed.set_footer(text=f"⭐ Premium Feature • Customized on {custom_summary['created_at'][:10]}")
            
        else:
            # Show default personality
            embed = discord.Embed(
                title="About Chatore 🍽️",
                description="Hey there! I'm Chatore, your friendly AI companion!",
                color=0x7289DA
            )
            
            embed.add_field(
                name="About Me",
                value="• Male bot created by Abhinav 👨‍💻\n• Age: Unknown (but I'm timeless! ⏰)\n• Love gaming and have knowledge about various topics 🎮\n• Speak both English and Hinglish 🌐",
                inline=False
            )
            
            embed.add_field(
                name="Personality Traits",
                value="• Friendly and witty 😄\n• Good sense of humor 😂\n• Remembers our conversations 🧠\n• Loves gaming and tech 🎮\n• Always here to help! 💪",
                inline=False
            )
            
            embed.add_field(
                name="What I Can Do",
                value="• Chat about anything!\n• Remember things about you\n• Help with questions\n• Share memes and jokes\n• Be your digital friend! 🤖💙",
                inline=False
            )
            
            if tier == 'premium':
                embed.add_field(
                    name="⭐ Premium Feature Available",
                    value="As a Premium user, you can customize my personality!\nUse the buttons below to get started.",
                    inline=False
                )
        
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        
        # Add buttons for premium users
        if tier == 'premium':
            view = PersonalityView(bot, interaction.user.id, has_custom)
            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()
        else:
            await interaction.response.send_message(embed=embed)
        
        # Check for new users and show welcome message
        await bot.check_and_welcome_new_user(interaction)

    @bot.tree.command(name="ping", description="Check bot latency and connection status")
    async def slash_ping(interaction: discord.Interaction):
        """Check bot latency (slash command)"""
        latency = round(bot.latency * 1000)
        
        if latency < 100:
            color = 0x00FF00  # Green
            status = "Excellent! 🚀"
        elif latency < 200:
            color = 0xFFFF00  # Yellow
            status = "Good! 👍"
        else:
            color = 0xFF0000  # Red
            status = "Slow... 🐌"
        
        embed = discord.Embed(
            title="Pong! 🏓",
            description=f"**Latency:** {latency}ms\n**Status:** {status}",
            color=color
        )
        await interaction.response.send_message(embed=embed)
        
        # Check for new users and show welcome message
        await bot.check_and_welcome_new_user(interaction)

    @bot.tree.command(name="stats", description="View bot statistics and usage information")
    async def slash_stats(interaction: discord.Interaction):
        """Show bot statistics (slash command)"""
        stats = bot.memory.get_stats()
        
        embed = discord.Embed(
            title="Chatore's Stats 📊",
            color=0xE91E63
        )
        
        embed.add_field(name="Users I Know", value=f"{stats['total_users']} people", inline=True)
        embed.add_field(name="Total Messages", value=f"{stats['total_conversations']} messages", inline=True)
        embed.add_field(name="Memories Stored", value=f"{stats['total_memories']} memories", inline=True)
        embed.add_field(name="Servers", value=f"{len(bot.guilds)} servers", inline=True)
        embed.add_field(name="Uptime", value="Since last restart", inline=True)
        
        embed.set_footer(text="Thanks for chatting with me! 💙")
        await interaction.response.send_message(embed=embed)
    

    
    @bot.tree.command(name="activity", description="Check your activity status and memory cleanup info")
    async def slash_activity(interaction: discord.Interaction):
        """Check your last activity and memory cleanup status (slash command)"""
        user_id = str(interaction.user.id)
        
        # Get tier information
        tier = bot.tier_manager.get_user_tier(user_id)
        context_limit = bot.tier_manager.get_context_limit(user_id)
        
        embed = discord.Embed(
            title="📊 Your Activity Status",
            color=0xFFD700 if tier == 'premium' else 0x00AFF4
        )
        
        if user_id in bot.memory.user_last_activity:
            from datetime import datetime
            last_activity = datetime.fromisoformat(bot.memory.user_last_activity[user_id])
            time_diff = datetime.now() - last_activity
            hours_inactive = time_diff.total_seconds() / 3600
            
            embed.add_field(
                name="Last Activity",
                value=f"{last_activity.strftime('%Y-%m-%d %H:%M:%S')}",
                inline=False
            )
            
            embed.add_field(
                name="Inactive Duration",
                value=f"{hours_inactive:.1f} hours",
                inline=True
            )
            
            # Check message count with tier info
            msg_count = len(bot.memory.conversation_history.get(user_id, []))
            embed.add_field(
                name="Messages Stored",
                value=f"{msg_count}/25 (Context: {context_limit})",
                inline=True
            )
            
            embed.add_field(
                name="Current Tier",
                value=f"{'⭐ Premium' if tier == 'premium' else '🆓 Free'}",
                inline=True
            )
            
            if hours_inactive >= 3:
                embed.add_field(
                    name="⚠️ Memory Status",
                    value="Your message history will be reduced to 3 messages due to inactivity (3+ hours)",
                    inline=False
                )
                embed.color = 0xFF9933
            else:
                embed.add_field(
                    name="✅ Memory Status",
                    value=f"Active user - {context_limit} message context ({'⭐ Premium' if tier == 'premium' else '🆓 Free'} tier)",
                    inline=False
                )
                embed.color = 0xFFD700 if tier == 'premium' else 0x00FF7F
        else:
            embed.description = "No activity recorded yet."
            embed.color = 0x95A5A6
        
        embed.add_field(
            name="Memory Cleanup Rules",
            value="• Active users: 12 messages stored\n• Inactive 3+ hours: Only 3 messages stored\n• Permanent memories never deleted",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="invite", description="Get the invite link to add Chatore to your server")
    async def slash_invite(interaction: discord.Interaction):
        """Show bot invite link (slash command)"""
        embed = discord.Embed(
            title="Click Below Button To Invite Me",
            color=0x00AFF4
        )
        
        embed.add_field(
            name="🔗 Invite Link",
            value="[Click here to invite Chatore!](https://discord.com/oauth2/authorize?client_id=1397146788577673276&permissions=8&integration_type=0&scope=bot)",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
