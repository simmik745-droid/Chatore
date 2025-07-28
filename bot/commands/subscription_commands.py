"""
Subscription Commands - Tier management and subscription handling
"""

import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta

class SubscriptionView(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=30)  # 30 second timeout
        self.bot = bot
        self.user_id = user_id
        self.message = None  # Store message for timeout updates
    
    @discord.ui.button(label="Request Premium", emoji="⭐", style=discord.ButtonStyle.primary)
    async def subscribe_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This subscription menu is not for you!", ephemeral=True)
            return
        
        # Create subscription request modal
        modal = SubscriptionModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Learn More", emoji="ℹ️", style=discord.ButtonStyle.secondary)
    async def learn_more_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.user_id):
            await interaction.response.send_message("❌ This subscription menu is not for you!", ephemeral=True)
            return
        
        embed = create_features_comparison_embed(self.bot)
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """Handle timeout - disable all components and update message"""
        for item in self.children:
            item.disabled = True
        
        # Create timeout embed
        embed = discord.Embed(
            title="⏰ Subscription Menu Timed Out",
            description="This subscription menu has expired after 30 seconds of inactivity.",
            color=0x95A5A6
        )
        embed.add_field(
            name="💡 Need Help Again?",
            value="Use `/subscribe` to open a new subscription menu anytime!",
            inline=False
        )
        embed.set_footer(text="Menu expired • Use /subscribe for a new one")
        
        # Try to edit the message to show timeout
        if self.message:
            try:
                await self.message.edit(embed=embed, view=self)
            except (discord.NotFound, discord.Forbidden, Exception):
                pass

class SubscriptionModal(discord.ui.Modal, title="Premium Subscription Request"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    discord_username = discord.ui.TextInput(
        label="Discord Username",
        placeholder="Enter your Discord username (e.g., john_doe)",
        style=discord.TextStyle.short,
        max_length=32,
        required=True
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        username = self.discord_username.value.strip()
        
        if not username:
            embed = discord.Embed(
                title="❌ Invalid Username",
                description="Please enter a valid Discord username.",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        
        # Check if already premium
        current_tier = self.bot.tier_manager.get_user_tier(user_id)
        if current_tier == 'premium':
            embed = discord.Embed(
                title="⭐ Already Premium!",
                description="You're already subscribed to Premium tier!",
                color=0xFFD700
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Send notification to owner
        await self.notify_owner(interaction, username)
        
        # Send confirmation to user
        embed = discord.Embed(
            title="📨 Subscription Request Sent!",
            description="Your Premium subscription request has been sent to the bot owner.",
            color=0x00FF7F
        )
        
        embed.add_field(
            name="✅ What Happens Next?",
            value="• The bot owner will review your request\n• You'll be contacted for payment details\n• Premium will be activated after payment\n• You'll receive a confirmation message",
            inline=False
        )
        
        embed.add_field(
            name="📋 Your Request Details",
            value=f"**Discord User**: {interaction.user.mention}\n**Username Provided**: {username}\n**Requested**: Premium Subscription",
            inline=False
        )
        
        embed.add_field(
            name="⏱️ Processing Time",
            value="Requests are typically processed within 24 hours.",
            inline=False
        )
        
        embed.set_footer(text="Thank you for your interest in Chatore Premium!")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def notify_owner(self, interaction: discord.Interaction, username: str):
        """Send notification to bot owner about subscription request"""
        try:
            # Bot owner ID (replace with actual owner ID)
            owner_id = 1369333896965001396  # Replace with your Discord user ID
            
            owner = self.bot.get_user(owner_id)
            if not owner:
                owner = await self.bot.fetch_user(owner_id)
            
            if owner:
                embed = discord.Embed(
                    title="💰 New Premium Subscription Request",
                    description="Someone wants to subscribe to Chatore Premium!",
                    color=0xFFD700
                )
                
                embed.add_field(
                    name="👤 User Information",
                    value=f"**Discord User**: {interaction.user.mention} ({interaction.user.name})\n**User ID**: {interaction.user.id}\n**Username Provided**: {username}",
                    inline=False
                )
                
                embed.add_field(
                    name="📊 Current Status",
                    value=f"**Current Tier**: {self.bot.tier_manager.get_user_tier(str(interaction.user.id)).title()}\n**Server**: {interaction.guild.name if interaction.guild else 'DM'}\n**Timestamp**: <t:{int(interaction.created_at.timestamp())}:F>",
                    inline=False
                )
                
                embed.add_field(
                    name="🎯 Quick Actions",
                    value="Use `/grant_premium @user 1` to grant 1 month premium\nOr contact the user for payment details",
                    inline=False
                )
                
                embed.set_thumbnail(url=interaction.user.display_avatar.url)
                embed.set_footer(text="Premium Subscription Request • Chatore Bot")
                
                await owner.send(embed=embed)
                
        except Exception as e:
            print(f"Error notifying owner about subscription request: {e}")

def create_plan_embed(bot, user_id: str) -> discord.Embed:
    """Create embed showing user's current plan"""
    tier_info = bot.tier_manager.get_user_tier_info(user_id)
    usage_stats = bot.tier_manager.get_usage_stats(user_id)
    
    # Color based on tier
    color = 0xFFD700 if tier_info['tier'] == 'premium' else 0x7289DA
    
    # Title with tier emoji
    title_emoji = "⭐" if tier_info['tier'] == 'premium' else "🆓"
    title = f"{title_emoji} {tier_info['config']['name']}"
    
    embed = discord.Embed(
        title=title,
        description=f"Your current subscription plan and usage statistics",
        color=color
    )
    
    # Usage information
    usage_percentage = (usage_stats['current_usage'] / usage_stats['usage_limit']) * 100
    usage_bar = create_usage_bar(usage_percentage)
    
    embed.add_field(
        name="📊 Current Usage",
        value=f"{usage_bar}\n**{usage_stats['current_usage']}/{usage_stats['usage_limit']} requests** ({usage_percentage:.1f}%)\nResets in {usage_stats['hours_until_reset']:.1f} hours",
        inline=False
    )
    
    # Plan features
    features_text = "\n".join([f"• {feature}" for feature in tier_info['config']['features']])
    embed.add_field(
        name="✨ Plan Features",
        value=features_text,
        inline=False
    )
    
    # Subscription details
    if tier_info['tier'] == 'premium':
        expires_at = datetime.fromisoformat(tier_info['expires_at'])
        days_remaining = (expires_at - datetime.now()).days
        
        embed.add_field(
            name="📅 Subscription Details",
            value=f"• **Status**: Active Premium\n• **Expires**: {expires_at.strftime('%B %d, %Y')}\n• **Days Remaining**: {days_remaining} days",
            inline=False
        )
    else:
        embed.add_field(
            name="💡 Upgrade Available",
            value="Consider upgrading to Premium for more requests and enhanced features!\nUse `/subscribe` to upgrade.",
            inline=False
        )
    
    # Statistics
    embed.add_field(
        name="📈 Your Statistics",
        value=f"• **Total Requests**: {usage_stats['total_requests']:,}\n• **Member Since**: {datetime.fromisoformat(usage_stats['member_since']).strftime('%B %Y') if usage_stats['member_since'] else 'Recently'}",
        inline=False
    )
    
    embed.set_footer(text=f"Context Limit: {usage_stats['context_limit']} messages")
    embed.timestamp = discord.utils.utcnow()
    
    return embed

def create_subscription_embed(bot, user_id: str) -> discord.Embed:
    """Create embed for subscription page"""
    current_tier = bot.tier_manager.get_user_tier(user_id)
    
    if current_tier == 'premium':
        embed = discord.Embed(
            title="⭐ You're Already Premium!",
            description="Thank you for being a Premium subscriber!",
            color=0xFFD700
        )
        
        tier_info = bot.tier_manager.get_user_tier_info(user_id)
        expires_at = datetime.fromisoformat(tier_info['expires_at'])
        
        embed.add_field(
            name="📅 Your Subscription",
            value=f"• **Plan**: Premium Monthly\n• **Expires**: {expires_at.strftime('%B %d, %Y')}\n• **Auto-Renew**: {'✅ Enabled' if tier_info['auto_renew'] else '❌ Disabled'}",
            inline=False
        )
        
        return embed
    
    embed = discord.Embed(
        title="⭐ Upgrade to Chatore Premium",
        description="Unlock enhanced features and higher limits!",
        color=0xFFD700
    )
    
    # Current vs Premium comparison
    free_config = bot.tier_manager.get_tier_config('free')
    premium_config = bot.tier_manager.get_tier_config('premium')
    
    embed.add_field(
        name="🆓 Your Current Plan (Free)",
        value=f"• {free_config['context_limit']} message context\n• {free_config['requests_per_12h']} requests per 12 hours\n• Basic features",
        inline=True
    )
    
    embed.add_field(
        name="⭐ Premium Plan ($1.50/month)",
        value=f"• {premium_config['context_limit']} message context\n• {premium_config['requests_per_12h']} requests per 12 hours\n• 🎨 Custom personality system\n• 💾 Personality presets (5 slots)\n• Priority responses\n• Premium support",
        inline=True
    )
    
    embed.add_field(
        name="🚀 Upgrade Benefits",
        value="• **2x More Context**: Better conversation memory\n• **5x More Requests**: Use Chatore more freely\n• **🎭 Custom Personality**: Customize my traits, humor, speaking style\n• **💾 Personality Presets**: Save & switch between 5 different personalities\n• **Priority Processing**: Faster responses\n• **Premium Support**: Direct help when needed",
        inline=False
    )
    
    embed.add_field(
        name="💳 How to Subscribe",
        value="1. Click 'Subscribe to Premium' below\n2. Enter your Discord username\n3. Wait for owner contact for payment\n4. Premium activates after payment!",
        inline=False
    )
    
    embed.add_field(
        name="💰 Pricing",
        value="**$1.50/month** - Affordable premium features\n*Payment details will be provided by the bot owner*",
        inline=False
    )
    
    embed.set_footer(text="Click 'Subscribe to Premium' to send your subscription request")
    
    return embed

def create_features_comparison_embed(bot) -> discord.Embed:
    """Create detailed features comparison embed"""
    embed = discord.Embed(
        title="📊 Plan Comparison",
        description="Compare Free and Premium features side by side",
        color=0x7289DA
    )
    
    free_config = bot.tier_manager.get_tier_config('free')
    premium_config = bot.tier_manager.get_tier_config('premium')
    
    # Feature comparison table
    features = [
        ("Message Context", f"{free_config['context_limit']} messages", f"{premium_config['context_limit']} messages"),
        ("Requests per 12h", f"{free_config['requests_per_12h']} requests", f"{premium_config['requests_per_12h']} requests"),
        ("AI Response Speed", "Standard", "Priority"),
        ("Memory System", "✅ Included", "✅ Enhanced"),
        ("Personality System", "❌ Standard only", "✅ Full customization"),
        ("Personality Presets", "❌ Not available", "✅ 5 preset slots"),
        ("Slash Commands", "✅ All commands", "✅ All commands"),
        ("Support", "Community", "Premium"),
        ("New Features", "Standard release", "Early access"),
        ("Price", "Free", "$1.50/month")
    ]
    
    free_column = []
    premium_column = []
    
    for feature, free_val, premium_val in features:
        free_column.append(f"**{feature}**: {free_val}")
        premium_column.append(f"**{feature}**: {premium_val}")
    
    embed.add_field(
        name="🆓 Free Tier",
        value="\n".join(free_column),
        inline=True
    )
    
    embed.add_field(
        name="⭐ Premium Tier",
        value="\n".join(premium_column),
        inline=True
    )
    
    embed.add_field(
        name="🎯 Why Upgrade?",
        value="• **Better Conversations**: 25 messages context means I remember more of our chat\n• **More Freedom**: 200 requests per 12 hours vs 40 for free users\n• **Faster Responses**: Priority processing for premium users\n• **Support the Bot**: Help keep Chatore running and improving",
        inline=False
    )
    
    return embed

def create_usage_bar(percentage: float, length: int = 10) -> str:
    """Create a visual usage bar"""
    filled = int(percentage / 100 * length)
    empty = length - filled
    
    if percentage >= 90:
        bar_char = "🟥"
    elif percentage >= 70:
        bar_char = "🟨"
    else:
        bar_char = "🟩"
    
    return bar_char * filled + "⬜" * empty

def setup(bot):
    """Setup subscription commands"""
    
    @bot.tree.command(name="plan", description="Check your current subscription plan and usage")
    async def plan_command(interaction: discord.Interaction):
        """Show user's current plan and usage statistics"""
        user_id = str(interaction.user.id)
        
        embed = create_plan_embed(bot, user_id)
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(name="subscribe", description="Subscribe to Chatore Premium")
    async def subscribe_command(interaction: discord.Interaction):
        """Show subscription options and allow upgrading to premium"""
        user_id = str(interaction.user.id)
        
        embed = create_subscription_embed(bot, user_id)
        view = SubscriptionView(bot, user_id)
        
        await interaction.response.send_message(embed=embed, view=view)
        view.message = await interaction.original_response()
    
    # Owner-only commands for tier management
    @bot.tree.command(name="grant_premium", description="Grant premium to a user (Owner only)")
    @app_commands.describe(user="User to grant premium to", months="Duration in months")
    async def grant_premium(interaction: discord.Interaction, user: discord.User, months: int = 1):
        """Grant premium subscription to a user (owner only)"""
        # Check if user is bot owner
        if str(interaction.user.id) != "1369333896965001396":  # Replace with actual owner ID
            await interaction.response.send_message("❌ This command is only available to the bot owner.", ephemeral=True)
            return
        
        user_id = str(user.id)
        success = bot.tier_manager.subscribe_premium(user_id, months)
        
        if success:
            await bot.tier_manager.save_tiers()
            
            embed = discord.Embed(
                title="✅ Premium Granted",
                description=f"Successfully granted {months} month(s) of Premium to {user.mention}",
                color=0x00FF7F
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title="❌ Failed",
                description="Failed to grant premium subscription.",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(name="tier_stats", description="View tier statistics (Owner only)")
    async def tier_stats(interaction: discord.Interaction):
        """Show tier statistics (owner only)"""
        # Check if user is bot owner
        if str(interaction.user.id) != "1369333896965001396":  # Replace with actual owner ID
            await interaction.response.send_message("❌ This command is only available to the bot owner.", ephemeral=True)
            return
        
        stats = bot.tier_manager.get_tier_stats()
        
        embed = discord.Embed(
            title="📊 Tier Statistics",
            color=0x7289DA
        )
        
        embed.add_field(
            name="👥 User Distribution",
            value=f"• **Total Users**: {stats['total_users']}\n• **Free Users**: {stats['free_users']}\n• **Premium Users**: {stats['premium_users']}\n• **Premium Rate**: {stats['premium_percentage']:.1f}%",
            inline=False
        )
        
        # Get premium users list
        premium_users = bot.tier_manager.get_all_premium_users()
        if premium_users:
            premium_list = []
            for user_info in premium_users[:5]:  # Show first 5
                user_id = user_info['user_id']
                expires = datetime.fromisoformat(user_info['expires_at']).strftime('%m/%d/%Y')
                premium_list.append(f"<@{user_id}> (expires {expires})")
            
            embed.add_field(
                name="⭐ Recent Premium Users",
                value="\n".join(premium_list) + (f"\n... and {len(premium_users) - 5} more" if len(premium_users) > 5 else ""),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)