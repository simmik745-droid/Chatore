"""
Owner Commands - Hidden commands only for the bot owner
"""

import discord
from discord.ext import commands
from discord import app_commands

# Bot owner's user ID
OWNER_ID = 1369333896965001396

def is_owner():
    """Check if user is the bot owner"""
    def predicate(ctx):
        return ctx.author.id == OWNER_ID
    return commands.check(predicate)

def is_owner_interaction(interaction: discord.Interaction) -> bool:
    """Check if interaction user is the bot owner"""
    return interaction.user.id == OWNER_ID

def setup(bot):
    """Setup owner commands"""
    
    @bot.command(name='listserver', hidden=True)
    @is_owner()
    async def list_servers(ctx):
        """List all servers the bot is in with invite links (Owner only)"""
        try:
            # Delete the command message for privacy
            try:
                await ctx.message.delete()
            except:
                pass
            
            guilds = bot.guilds
            
            if not guilds:
                embed = discord.Embed(
                    title="🏠 Server List",
                    description="Bot is not in any servers.",
                    color=0xFF6B6B
                )
                await ctx.author.send(embed=embed)
                return
            
            # Create main embed
            embed = discord.Embed(
                title="🏠 Bot Server List",
                description=f"Chatore is currently in **{len(guilds)}** server(s)",
                color=0x7289DA,
                timestamp=discord.utils.utcnow()
            )
            
            server_info = []
            
            for i, guild in enumerate(guilds, 1):
                # Get basic server info
                member_count = guild.member_count
                owner = guild.owner
                created_date = guild.created_at.strftime("%Y-%m-%d")
                
                # Try to create an invite link
                invite_link = "No invite permissions"
                try:
                    # Find a text channel to create invite from
                    text_channels = [ch for ch in guild.channels if isinstance(ch, discord.TextChannel)]
                    if text_channels:
                        # Try to create invite from the first available text channel
                        for channel in text_channels:
                            try:
                                invite = await channel.create_invite(
                                    max_age=0,  # Never expires
                                    max_uses=0,  # Unlimited uses
                                    unique=False,
                                    reason="Owner command: server list"
                                )
                                invite_link = invite.url
                                break
                            except discord.Forbidden:
                                continue
                            except Exception:
                                continue
                except Exception:
                    pass
                
                # Format server info
                server_text = f"**{i}. {guild.name}**\n"
                server_text += f"• ID: `{guild.id}`\n"
                server_text += f"• Members: {member_count}\n"
                server_text += f"• Owner: {owner.mention if owner else 'Unknown'}\n"
                server_text += f"• Created: {created_date}\n"
                server_text += f"• Invite: {invite_link}\n"
                
                server_info.append(server_text)
            
            # Split into multiple embeds if too long
            max_field_length = 1024
            current_field = ""
            field_count = 1
            
            for server in server_info:
                if len(current_field + server) > max_field_length:
                    # Add current field and start new one
                    embed.add_field(
                        name=f"📋 Servers ({field_count})",
                        value=current_field,
                        inline=False
                    )
                    current_field = server
                    field_count += 1
                else:
                    current_field += server + "\n"
            
            # Add remaining servers
            if current_field:
                embed.add_field(
                    name=f"📋 Servers ({field_count})" if field_count > 1 else "📋 Servers",
                    value=current_field,
                    inline=False
                )
            
            embed.set_footer(
                text=f"Generated for {ctx.author.display_name} • Owner Command",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None
            )
            
            # Send via DM for privacy
            try:
                await ctx.author.send(embed=embed)
                
                # Send confirmation in channel (will be deleted quickly)
                confirm_embed = discord.Embed(
                    description="📨 Server list sent to your DMs!",
                    color=0x00FF7F
                )
                confirm_msg = await ctx.send(embed=confirm_embed)
                
                # Delete confirmation after 3 seconds
                import asyncio
                await asyncio.sleep(3)
                await confirm_msg.delete()
                
            except discord.Forbidden:
                # If DM fails, send in channel with warning
                warning_embed = discord.Embed(
                    title="⚠️ DM Failed",
                    description="Couldn't send DM. Sending server list here (will auto-delete in 10 seconds):",
                    color=0xFF9933
                )
                await ctx.send(embed=warning_embed)
                
                msg = await ctx.send(embed=embed)
                
                # Delete after 10 seconds for privacy
                import asyncio
                await asyncio.sleep(10)
                await msg.delete()
                await warning_embed.delete()
                
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description="Failed to generate server list.",
                color=0xFF6B6B
            )
            await ctx.send(embed=error_embed)
            print(f"Error in listserver command: {e}")
    
    # Slash command for owner info (public)
    @bot.tree.command(name="owner", description="Show information about Chatore's owner")
    async def slash_owner_info(interaction: discord.Interaction):
        """Show owner information (slash command)"""
        try:
            # Get owner user object
            owner = bot.get_user(OWNER_ID)
            if not owner:
                try:
                    owner = await bot.fetch_user(OWNER_ID)
                except:
                    owner = None
            
            embed = discord.Embed(
                title="👑 Meet Abhinav Anand",
                description="The owner and creator of Chatore!",
                color=0xFFD700,
                timestamp=discord.utils.utcnow()
            )
            
            if owner:
                embed.set_thumbnail(url=owner.avatar.url if owner.avatar else None)
                
                # Owner's basic info
                embed.add_field(
                    name="📋 Basic Information",
                    value=f"**Name:** Abhinav Anand\n**Discord:** {owner.mention}\n**Username:** `{owner.name}`\n**User ID:** `{owner.id}`",
                    inline=False
                )
            else:
                embed.add_field(
                    name="📋 Basic Information",
                    value=f"**Name:** Abhinav Anand\n**User ID:** `{OWNER_ID}`",
                    inline=False
                )
            
            # Owner's personality and interests
            embed.add_field(
                name="🎯 About Abhinav",
                value="• **Age:** 15 years old\n• **Location:** India 🇮🇳\n• **Passion:** Loves to code and create amazing projects\n• **Personality:** Enthusiastic, creative, and always learning",
                inline=False
            )
            
            # What he does
            embed.add_field(
                name="💻 What He Does",
                value="• **Developer:** Creates Discord bots and applications\n• **Student:** Always learning new technologies\n• **Creator:** Built Chatore from scratch with love\n• **Enthusiast:** Passionate about AI and programming",
                inline=False
            )
            
            # His creation - Chatore
            embed.add_field(
                name="🤖 His Creation - Chatore",
                value="• Built with Python & discord.py\n• Powered by Google Gemini 2.5 Flash AI\n• Features advanced memory system\n• Supports both English & Hinglish personalities",
                inline=False
            )
            
            embed.set_footer(
                text="A young developer with big dreams! 🌟",
                icon_url=bot.user.avatar.url if bot.user.avatar else None
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description="Failed to get owner information.",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=error_embed)
            print(f"Error in owner info command: {e}")
    
    # Owner-only API status commands
    @bot.command(name='apistatus', hidden=True)
    @is_owner()
    async def api_status(ctx):
        """Check API key status and availability (Owner only)"""
        try:
            # Delete the command message for privacy
            try:
                await ctx.message.delete()
            except:
                pass
            
            embed = discord.Embed(
                title="🔑 API Key Status",
                color=0x00AFF4
            )
            
            embed.add_field(
                name="Available Keys",
                value=f"{len(bot.api_keys)} API key(s) configured",
                inline=True
            )
            
            embed.add_field(
                name="Current Key",
                value=f"Key #{bot.current_api_key_index + 1}",
                inline=True
            )
            
            # Test current API key
            try:
                test_response = await bot.generate_response("Say 'API test successful'")
                if "API test successful" in test_response or "successful" in test_response.lower():
                    embed.add_field(
                        name="Status",
                        value="✅ Current API key working",
                        inline=False
                    )
                    embed.color = 0x00FF7F
                else:
                    embed.add_field(
                        name="Status",
                        value="⚠️ API response unusual",
                        inline=False
                    )
                    embed.color = 0xFFD700
            except Exception as e:
                embed.add_field(
                    name="Status",
                    value=f"❌ API key failed: {str(e)[:100]}...",
                    inline=False
                )
                embed.color = 0xFF6B6B
            
            embed.add_field(
                name="Fallback System",
                value="✅ Automatic switching enabled" if len(bot.api_keys) > 1 else "⚠️ No backup keys configured",
                inline=False
            )
            
            embed.set_footer(text="Add GEMINI_API_KEY_2 and GEMINI_API_KEY_3 to .env for fallback")
            
            # Send via DM for privacy
            try:
                await ctx.author.send(embed=embed)
                
                # Send confirmation in channel (will be deleted quickly)
                confirm_embed = discord.Embed(
                    description="📨 API status sent to your DMs!",
                    color=0x00FF7F
                )
                confirm_msg = await ctx.send(embed=confirm_embed)
                
                # Delete confirmation after 3 seconds
                import asyncio
                await asyncio.sleep(3)
                await confirm_msg.delete()
                
            except discord.Forbidden:
                # If DM fails, send in channel with warning
                warning_embed = discord.Embed(
                    title="⚠️ DM Failed",
                    description="Couldn't send DM. Sending API status here (will auto-delete in 10 seconds):",
                    color=0xFF9933
                )
                await ctx.send(embed=warning_embed)
                
                msg = await ctx.send(embed=embed)
                
                # Delete after 10 seconds for privacy
                import asyncio
                await asyncio.sleep(10)
                await msg.delete()
                await warning_embed.delete()
                
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description="Failed to get API status.",
                color=0xFF6B6B
            )
            await ctx.send(embed=error_embed)
            print(f"Error in apistatus command: {e}")

    @bot.tree.command(name="apistatus", description="Check API key status and availability")
    async def slash_apistatus(interaction: discord.Interaction):
        """Check API key status and availability (slash command - Owner only)"""
        # Check if user is owner
        if not is_owner_interaction(interaction):
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="You cannot access this command. This command is restricted to the bot owner only.",
                color=0xFF6B6B
            )
            embed.set_footer(text="Only the bot owner can check API status")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            embed = discord.Embed(
                title="🔑 API Key Status",
                color=0x00AFF4
            )
            
            embed.add_field(
                name="Available Keys",
                value=f"{len(bot.api_keys)} API key(s) configured",
                inline=True
            )
            
            embed.add_field(
                name="Current Key",
                value=f"Key #{bot.current_api_key_index + 1}",
                inline=True
            )
            
            # Test current API key
            try:
                test_response = await bot.generate_response("Say 'API test successful'")
                if "API test successful" in test_response or "successful" in test_response.lower():
                    embed.add_field(
                        name="Status",
                        value="✅ Current API key working",
                        inline=False
                    )
                    embed.color = 0x00FF7F
                else:
                    embed.add_field(
                        name="Status",
                        value="⚠️ API response unusual",
                        inline=False
                    )
                    embed.color = 0xFFD700
            except Exception as e:
                embed.add_field(
                    name="Status",
                    value=f"❌ API key failed: {str(e)[:100]}...",
                    inline=False
                )
                embed.color = 0xFF6B6B
            
            embed.add_field(
                name="Fallback System",
                value="✅ Automatic switching enabled" if len(bot.api_keys) > 1 else "⚠️ No backup keys configured",
                inline=False
            )
            
            embed.set_footer(text="Add GEMINI_API_KEY_2 and GEMINI_API_KEY_3 to .env for fallback")
            
            # Send as ephemeral (private) response to owner
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            error_embed = discord.Embed(
                title="❌ Error",
                description="Failed to get API status.",
                color=0xFF6B6B
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            print(f"Error in slash apistatus command: {e}")
    
    # Error handler for owner-only commands
    @list_servers.error
    async def listserver_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            # Silently ignore - don't reveal the command exists
            try:
                await ctx.message.delete()
            except:
                pass
        else:
            print(f"Error in listserver command: {error}")
    
    @api_status.error
    async def apistatus_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            # Silently ignore - don't reveal the command exists
            try:
                await ctx.message.delete()
            except:
                pass
        else:
            print(f"Error in apistatus command: {error}")