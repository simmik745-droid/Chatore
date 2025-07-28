"""
Tier Manager - Handles user subscription tiers and rate limiting
"""

import json
import os
import aiofiles
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import asyncio
import discord

class TierManager:
    def __init__(self):
        self.user_tiers = {}  # user_id -> tier_info
        self.user_usage = {}  # user_id -> usage_info
        self.tier_file = "user_tiers.json"
        self.load_tiers()
        
        # Tier configurations
        self.tier_configs = {
            'free': {
                'name': 'Free Tier',
                'context_limit': 12,
                'requests_per_12h': 40,
                'price': 0,
                'features': [
                    '12 message context',
                    '40 requests per 12 hours',
                    'Basic AI responses',
                    'Memory system',
                    'All slash commands',
                    'Standard personality'
                ]
            },
            'premium': {
                'name': 'Premium Tier',
                'context_limit': 25,
                'requests_per_12h': 200,
                'price': 1.50,  # USD per month
                'features': [
                    '25 message context',
                    '200 requests per 12 hours',
                    'Priority AI responses',
                    'Enhanced memory system',
                    'All slash commands',
                    '🎨 Custom personality system',
                    '💾 Personality presets (5 slots)',
                    '🎭 Trait & behavior customization',
                    '💬 Speaking style options',
                    '😄 Humor style selection',
                    'Premium support',
                    'Early access to new features'
                ]
            }
        }
    
    def load_tiers(self):
        """Load tier data from file"""
        try:
            if os.path.exists(self.tier_file):
                with open(self.tier_file, 'r') as f:
                    data = json.load(f)
                    self.user_tiers = data.get('user_tiers', {})
                    self.user_usage = data.get('user_usage', {})
        except Exception as e:
            print(f"Error loading tier data: {e}")
    
    async def save_tiers(self):
        """Save tier data to file"""
        try:
            data = {
                'user_tiers': self.user_tiers,
                'user_usage': self.user_usage
            }
            async with aiofiles.open(self.tier_file, 'w') as f:
                await f.write(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error saving tier data: {e}")
    
    def get_user_tier(self, user_id: str) -> str:
        """Get user's current tier (default: free)"""
        if user_id not in self.user_tiers:
            # Initialize new user as free tier
            self.user_tiers[user_id] = {
                'tier': 'free',
                'subscribed_at': datetime.now().isoformat(),
                'expires_at': None,  # Free tier never expires
                'auto_renew': False
            }
        
        user_tier_info = self.user_tiers[user_id]
        
        # Check if premium subscription has expired
        if user_tier_info['tier'] == 'premium' and user_tier_info.get('expires_at'):
            expires_at = datetime.fromisoformat(user_tier_info['expires_at'])
            if datetime.now() > expires_at:
                # Downgrade to free tier
                user_tier_info['tier'] = 'free'
                user_tier_info['expires_at'] = None
                print(f"User {user_id} premium subscription expired, downgraded to free")
        
        return user_tier_info['tier']
    
    def get_tier_config(self, tier: str) -> Dict:
        """Get configuration for a specific tier"""
        return self.tier_configs.get(tier, self.tier_configs['free'])
    
    def get_user_tier_info(self, user_id: str) -> Dict:
        """Get complete tier information for user"""
        tier = self.get_user_tier(user_id)
        config = self.get_tier_config(tier)
        user_info = self.user_tiers.get(user_id, {})
        
        return {
            'tier': tier,
            'config': config,
            'subscribed_at': user_info.get('subscribed_at'),
            'expires_at': user_info.get('expires_at'),
            'auto_renew': user_info.get('auto_renew', False)
        }
    
    def initialize_user_usage(self, user_id: str):
        """Initialize usage tracking for user"""
        if user_id not in self.user_usage:
            self.user_usage[user_id] = {
                'requests_12h': 0,
                'last_reset': datetime.now().isoformat(),
                'total_requests': 0,
                'first_request': datetime.now().isoformat()
            }
    
    def reset_usage_if_needed(self, user_id: str):
        """Reset usage counter if 12 hours have passed"""
        self.initialize_user_usage(user_id)
        
        usage = self.user_usage[user_id]
        last_reset = datetime.fromisoformat(usage['last_reset'])
        
        # Reset if more than 12 hours have passed
        if datetime.now() - last_reset > timedelta(hours=12):
            usage['requests_12h'] = 0
            usage['last_reset'] = datetime.now().isoformat()
    
    def can_make_request(self, user_id: str) -> Tuple[bool, Dict]:
        """Check if user can make a request based on their tier limits"""
        self.reset_usage_if_needed(user_id)
        
        tier = self.get_user_tier(user_id)
        config = self.get_tier_config(tier)
        usage = self.user_usage[user_id]
        
        can_request = usage['requests_12h'] < config['requests_per_12h']
        
        return can_request, {
            'current_usage': usage['requests_12h'],
            'limit': config['requests_per_12h'],
            'tier': tier,
            'resets_at': (datetime.fromisoformat(usage['last_reset']) + timedelta(hours=12)).isoformat()
        }
    
    def increment_usage(self, user_id: str):
        """Increment user's request usage"""
        self.reset_usage_if_needed(user_id)
        
        usage = self.user_usage[user_id]
        usage['requests_12h'] += 1
        usage['total_requests'] += 1
    
    def get_context_limit(self, user_id: str) -> int:
        """Get context limit for user based on their tier"""
        tier = self.get_user_tier(user_id)
        config = self.get_tier_config(tier)
        return config['context_limit']
    
    def subscribe_premium(self, user_id: str, duration_months: int = 1) -> bool:
        """Subscribe user to premium tier"""
        try:
            expires_at = datetime.now() + timedelta(days=30 * duration_months)
            
            self.user_tiers[user_id] = {
                'tier': 'premium',
                'subscribed_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat(),
                'auto_renew': False,
                'duration_months': duration_months
            }
            
            print(f"User {user_id} subscribed to premium for {duration_months} month(s)")
            
            # Send welcome DM to user
            import asyncio
            asyncio.create_task(self.send_premium_welcome_dm(user_id, duration_months))
            
            return True
        except Exception as e:
            print(f"Error subscribing user {user_id} to premium: {e}")
            return False
    
    async def send_premium_welcome_dm(self, user_id: str, duration_months: int):
        """Send welcome DM to new premium user"""
        try:
            # Get bot instance from the tier manager
            if hasattr(self, 'bot'):
                bot = self.bot
            else:
                return  # Can't send DM without bot instance
            
            user = bot.get_user(int(user_id))
            if not user:
                user = await bot.fetch_user(int(user_id))
            
            if user:
                embed = discord.Embed(
                    title="🎉 Welcome to Chatore Premium!",
                    description="Congratulations! Your Premium subscription is now active.",
                    color=0x00FF7F
                )
                
                embed.add_field(
                    name="✨ Your Premium Benefits",
                    value="• **25 message context** (upgraded from 12)\n• **200 requests per 12 hours** (upgraded from 40)\n• **Custom personality settings** - Make me uniquely yours!\n• **Priority AI responses** - Faster processing\n• **Premium support** - Direct help when needed",
                    inline=False
                )
                
                embed.add_field(
                    name="📅 Subscription Details",
                    value=f"• **Duration**: {duration_months} month{'s' if duration_months != 1 else ''}\n• **Price**: $1.50/month\n• **Activated**: {datetime.now().strftime('%B %d, %Y')}\n• **Expires**: {(datetime.now() + timedelta(days=30 * duration_months)).strftime('%B %d, %Y')}",
                    inline=False
                )
                
                embed.add_field(
                    name="🚀 Get Started",
                    value="• Use `/plan` to check your new limits\n• Try `/personality` to customize my behavior, traits & humor style\n• Save up to 5 personality presets for easy switching\n• All premium features are active immediately!\n• Use `/help` to explore all commands",
                    inline=False
                )
                
                embed.add_field(
                    name="💡 Pro Tips",
                    value="• I now remember 25 messages instead of 12\n• You can make 200 requests every 12 hours\n• Customize my personality to match your style\n• Enjoy priority response processing!",
                    inline=False
                )
                
                embed.set_footer(text="Thank you for supporting Chatore! 💙")
                embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
                
                await user.send(embed=embed)
                print(f"Premium welcome DM sent to user {user_id}")
                
        except Exception as e:
            print(f"Error sending premium welcome DM to user {user_id}: {e}")
    
    def set_bot_instance(self, bot):
        """Set the bot instance for sending DMs"""
        self.bot = bot
    
    def get_usage_stats(self, user_id: str) -> Dict:
        """Get detailed usage statistics for user"""
        self.reset_usage_if_needed(user_id)
        
        tier_info = self.get_user_tier_info(user_id)
        usage = self.user_usage.get(user_id, {})
        
        # Calculate time until reset
        if usage.get('last_reset'):
            last_reset = datetime.fromisoformat(usage['last_reset'])
            reset_time = last_reset + timedelta(hours=12)
            time_until_reset = reset_time - datetime.now()
            hours_until_reset = max(0, time_until_reset.total_seconds() / 3600)
        else:
            hours_until_reset = 0
        
        return {
            'tier': tier_info['tier'],
            'tier_name': tier_info['config']['name'],
            'current_usage': usage.get('requests_12h', 0),
            'usage_limit': tier_info['config']['requests_per_12h'],
            'context_limit': tier_info['config']['context_limit'],
            'hours_until_reset': hours_until_reset,
            'total_requests': usage.get('total_requests', 0),
            'member_since': usage.get('first_request'),
            'expires_at': tier_info.get('expires_at')
        }
    
    def get_all_premium_users(self) -> list:
        """Get list of all premium users"""
        premium_users = []
        for user_id, tier_info in self.user_tiers.items():
            if tier_info['tier'] == 'premium':
                premium_users.append({
                    'user_id': user_id,
                    'subscribed_at': tier_info.get('subscribed_at'),
                    'expires_at': tier_info.get('expires_at')
                })
        return premium_users
    
    def get_tier_stats(self) -> Dict:
        """Get overall tier statistics"""
        total_users = len(self.user_tiers)
        free_users = sum(1 for info in self.user_tiers.values() if info['tier'] == 'free')
        premium_users = total_users - free_users
        
        return {
            'total_users': total_users,
            'free_users': free_users,
            'premium_users': premium_users,
            'premium_percentage': (premium_users / total_users * 100) if total_users > 0 else 0
        }