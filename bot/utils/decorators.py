"""
Utility decorators for bot commands
"""

import discord
from functools import wraps

def user_only(func):
    """Decorator to ensure only the command invoker can interact with buttons/views"""
    @wraps(func)
    async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
        # Check if this interaction is from the original command user
        if hasattr(self, 'original_user_id'):
            if str(interaction.user.id) != str(self.original_user_id):
                await interaction.response.send_message(
                    "❌ This command was not invoked by you! Use the command yourself to interact with it.",
                    ephemeral=True
                )
                return
        
        return await func(self, interaction, *args, **kwargs)
    return wrapper