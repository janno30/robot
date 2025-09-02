import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import asyncio
from datetime import datetime, timedelta

from config import MAX_WARNINGS, MUTE_DURATION, LOG_CHANNEL_ID, EMBED_COLORS
from database import ModerationDB
from utils import (
    has_mod_permissions, can_moderate_target, create_moderation_embed,
    parse_duration, format_duration, sanitize_reason
)

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = ModerationDB()
        self.muted_role_name = "Muted"
    
    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        """Handle errors in moderation commands"""
        try:
            # Check if interaction is still valid
            if interaction.response.is_done():
                # Interaction already responded to, try to send a new message
                try:
                    await interaction.followup.send(
                        f"❌ An error occurred: {str(error)}",
                        ephemeral=True
                    )
                except discord.NotFound:
                    # Interaction completely expired, can't send anything
                    print(f"Interaction expired, couldn't send error: {error}")
                except Exception as e:
                    print(f"Failed to send error via followup: {e}")
            else:
                # Interaction still valid, respond normally
                try:
                    if isinstance(error, app_commands.CommandInvokeError):
                        await interaction.response.send_message(
                            f"❌ An error occurred: {str(error.original)}",
                            ephemeral=True
                        )
                    else:
                        await interaction.response.send_message(
                            f"❌ Command error: {str(error)}",
                            ephemeral=True
                        )
                except Exception as e:
                    print(f"Failed to send error response: {e}")
                    
        except Exception as e:
            # Final fallback - just print to console
            print(f"Failed to handle command error: {e}")
            print(f"Original error: {error}")
    
    async def log_moderation_action(self, embed: discord.Embed):
        """Log moderation action to log channel"""
        if LOG_CHANNEL_ID:
            try:
                log_channel = self.bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    await log_channel.send(embed=embed)
            except Exception as e:
                print(f"Failed to log moderation action: {e}")
    
    async def get_or_create_muted_role(self, guild: discord.Guild) -> Optional[discord.Role]:
        """Get or create muted role"""
        muted_role = discord.utils.get(guild.roles, name=self.muted_role_name)
        
        if not muted_role:
            try:
                muted_role = await guild.create_role(
                    name=self.muted_role_name,
                    color=discord.Color.dark_grey(),
                    reason="Moderation bot muted role"
                )
                
                # Set permissions for all channels
                for channel in guild.channels:
                    if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                        await channel.set_permissions(muted_role, send_messages=False, speak=False)
                
            except discord.Forbidden:
                return None
        
        return muted_role
    
    @app_commands.command(name="warn", description="Warn a user for breaking rules")
    @app_commands.describe(
        user="The user to warn",
        reason="Reason for the warning"
    )
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        """Warn a user"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            can_mod, error_msg = can_moderate_target(interaction.user, user)
            if not can_mod:
                await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            # Sanitize reason
            sanitized_reason = sanitize_reason(reason)
            
            # Add warning to database
            warning = self.db.add_warning(user.id, interaction.user.id, sanitized_reason)
            warnings = self.db.get_warnings(user.id)
            
            # Create embed
            embed = create_moderation_embed(
                title="⚠️ User Warned",
                description=f"{user.mention} has been warned.",
                color="warning",
                user=user,
                moderator=interaction.user,
                reason=sanitized_reason,
                Warning_ID=warning['warning_id'],
                Total_Warnings=len(warnings)
            )
            
            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(embed)
            
            # Check if user should be auto-banned
            if len(warnings) >= MAX_WARNINGS:
                try:
                    await user.ban(reason=f"Auto-ban: Reached {MAX_WARNINGS} warnings")
                    ban_embed = create_moderation_embed(
                        title="🚫 User Auto-Banned",
                        description=f"{user.mention} has been automatically banned for reaching {MAX_WARNINGS} warnings.",
                        color="error",
                        user=user,
                        moderator=self.bot.user,
                        reason=f"Auto-ban: Reached {MAX_WARNINGS} warnings"
                    )
                    await interaction.followup.send(embed=ban_embed)
                    await self.log_moderation_action(ban_embed)
                except discord.Forbidden:
                    await interaction.followup.send("⚠️ User reached max warnings but couldn't be banned due to permissions.")
                    
        except Exception as e:
            print(f"Error in warn command: {e}")
            # Try to send error message if interaction is still valid
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for warn command: {e}")
    
    @app_commands.command(name="warnings", description="View warnings for a user")
    @app_commands.describe(user="The user to check warnings for")
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        """View user warnings"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            warnings = self.db.get_warnings(user.id)
            
            if not warnings:
                embed = create_moderation_embed(
                    title="📋 User Warnings",
                    description=f"{user.mention} has no warnings.",
                    color="success",
                    user=user
                )
            else:
                embed = create_moderation_embed(
                    title="📋 User Warnings",
                    description=f"{user.mention} has {len(warnings)} warning(s):",
                    color="info",
                    user=user
                )
                
                for warning in warnings:
                    embed.add_field(
                        name=f"Warning #{warning['warning_id']}",
                        value=f"**Reason:** {warning['reason']}\n**Moderator:** <@{warning['moderator_id']}>\n**Date:** <t:{int(datetime.fromisoformat(warning['timestamp']).timestamp())}:R>",
                        inline=False
                    )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Error in warnings command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for warnings command: {e}")
    
    @app_commands.command(name="clearwarnings", description="Clear all warnings for a user")
    @app_commands.describe(user="The user to clear warnings for")
    async def clear_warnings(self, interaction: discord.Interaction, user: discord.Member):
        """Clear user warnings"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            warnings = self.db.get_warnings(user.id)
            if not warnings:
                await interaction.followup.send(f"❌ {user.mention} has no warnings to clear.")
                return
            
            self.db.clear_warnings(user.id)
            
            embed = create_moderation_embed(
                title="🧹 Warnings Cleared",
                description=f"All warnings for {user.mention} have been cleared.",
                color="success",
                user=user,
                moderator=interaction.user,
                Warnings_Cleared=len(warnings)
            )
            
            await interaction.followup.send(embed=embed)
            await self.log_moderation_action(embed)
            
        except Exception as e:
            print(f"Error in clear_warnings command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for clear_warnings command: {e}")
    
    @app_commands.command(name="mute", description="Mute a user temporarily")
    @app_commands.describe(
        user="The user to mute",
        duration="Duration (e.g., 5m, 1h, 2d)",
        reason="Reason for the mute"
    )
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str = "No reason provided"):
        """Mute a user"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            can_mod, error_msg = can_moderate_target(interaction.user, user)
            if not can_mod:
                await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            # Parse duration
            duration_seconds = parse_duration(duration)
            if not duration_seconds:
                await interaction.followup.send("❌ Invalid duration format. Use: 5m, 1h, 2d, etc.")
                return
            
            # Sanitize reason
            sanitized_reason = sanitize_reason(reason)
            
            try:
                # Get or create muted role
                muted_role = await self.get_or_create_muted_role(interaction.guild)
                if not muted_role:
                    await interaction.followup.send("❌ Could not create or find muted role.")
                    return
                
                # Add muted role to user
                await user.add_roles(muted_role, reason=f"Muted by {interaction.user}: {sanitized_reason}")
                
                # Add to database
                mute_record = self.db.add_mute(user.id, interaction.user.id, duration_seconds, sanitized_reason)
                
                # Create embed
                embed = create_moderation_embed(
                    title="🔇 User Muted",
                    description=f"{user.mention} has been muted.",
                    color="warning",
                    user=user,
                    moderator=interaction.user,
                    reason=sanitized_reason,
                    Duration=format_duration(duration_seconds),
                    Expires=f"<t:{int(datetime.fromisoformat(mute_record['expires_at']).timestamp())}:R>"
                )
                
                await interaction.followup.send(embed=embed)
                await self.log_moderation_action(embed)
                
                # Schedule unmute
                self.bot.loop.create_task(self.schedule_unmute(user, duration_seconds, interaction.guild))
                
            except discord.Forbidden:
                await interaction.followup.send("❌ Could not mute user. Check bot permissions.")
            except Exception as e:
                await interaction.followup.send(f"❌ An error occurred: {str(e)}")
                
        except Exception as e:
            print(f"Error in mute command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for mute command: {e}")
    
    async def schedule_unmute(self, user: discord.Member, duration: int, guild: discord.Guild):
        """Schedule automatic unmute"""
        await asyncio.sleep(duration)
        
        try:
            # Check if user is still in the guild
            member = guild.get_member(user.id)
            if not member:
                return
            
            # Remove muted role
            muted_role = discord.utils.get(guild.roles, name=self.muted_role_name)
            if muted_role and muted_role in member.roles:
                await member.remove_roles(muted_role, reason="Mute expired")
                
                # Remove from database
                self.db.remove_mute(user.id)
                
                # Send unmute notification
                embed = create_moderation_embed(
                    title="🔊 User Unmuted",
                    description=f"{user.mention} has been automatically unmuted.",
                    color="success",
                    user=user,
                    reason="Mute duration expired"
                )
                
                # Try to DM user
                try:
                    await user.send(embed=embed)
                except:
                    pass
                
                # Log unmute
                await self.log_moderation_action(embed)
                
        except Exception as e:
            print(f"Error in scheduled unmute: {e}")
    
    @app_commands.command(name="unmute", description="Unmute a user immediately")
    @app_commands.describe(user="The user to unmute")
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        """Unmute a user"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            muted_role = discord.utils.get(interaction.guild.roles, name=self.muted_role_name)
            if not muted_role or muted_role not in user.roles:
                await interaction.followup.send(f"❌ {user.mention} is not muted.")
                return
            
            try:
                await user.remove_roles(muted_role, reason=f"Unmuted by {interaction.user}")
                self.db.remove_mute(user.id)
                
                embed = create_moderation_embed(
                    title="🔊 User Unmuted",
                    description=f"{user.mention} has been unmuted.",
                    color="success",
                    user=user,
                    moderator=interaction.user
                )
                
                await interaction.followup.send(embed=embed)
                await self.log_moderation_action(embed)
                
            except discord.Forbidden:
                await interaction.followup.send("❌ Could not unmute user. Check bot permissions.")
                
        except Exception as e:
            print(f"Error in unmute command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for unmute command: {e}")
    
    @app_commands.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(
        user="The user to kick",
        reason="Reason for the kick"
    )
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Kick a user"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            can_mod, error_msg = can_moderate_target(interaction.user, user)
            if not can_mod:
                await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            # Sanitize reason
            sanitized_reason = sanitize_reason(reason)
            
            try:
                await user.kick(reason=f"Kicked by {interaction.user}: {sanitized_reason}")
                
                # Log kick
                self.db.log_kick(user.id, interaction.user.id, sanitized_reason)
                
                embed = create_moderation_embed(
                    title="👢 User Kicked",
                    description=f"{user.mention} has been kicked from the server.",
                    color="warning",
                    user=user,
                    moderator=interaction.user,
                    reason=sanitized_reason
                )
                
                await interaction.followup.send(embed=embed)
                await self.log_moderation_action(embed)
                
            except discord.Forbidden:
                await interaction.followup.send("❌ Could not kick user. Check bot permissions.")
                
        except Exception as e:
            print(f"Error in kick command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for kick command: {e}")
    
    @app_commands.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        user="The user to ban",
        reason="Reason for the ban"
    )
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Ban a user"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            can_mod, error_msg = can_moderate_target(interaction.user, user)
            if not can_mod:
                await interaction.response.send_message(f"❌ {error_msg}", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            # Sanitize reason
            sanitized_reason = sanitize_reason(reason)
            
            try:
                await user.ban(reason=f"Banned by {interaction.user}: {sanitized_reason}")
                
                # Add to database
                self.db.add_ban(user.id, interaction.user.id, sanitized_reason)
                
                embed = create_moderation_embed(
                    title="🚫 User Banned",
                    description=f"{user.mention} has been banned from the server.",
                    color="error",
                    user=user,
                    moderator=interaction.user,
                    reason=sanitized_reason
                )
                
                await interaction.followup.send(embed=embed)
                await self.log_moderation_action(embed)
                
            except discord.Forbidden:
                await interaction.followup.send("❌ Could not ban user. Check bot permissions.")
                
        except Exception as e:
            print(f"Error in ban command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for ban command: {e}")
    
    @app_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user_id="The ID of the user to unban",
        reason="Reason for the unban"
    )
    async def unban(self, interaction: discord.Interaction, user_id: str, reason: str = "No reason provided"):
        """Unban a user"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            try:
                user_id = int(user_id)
                user = await self.bot.fetch_user(user_id)
                
                # Check if user is banned
                ban_entry = await interaction.guild.fetch_ban(user)
                if not ban_entry:
                    await interaction.followup.send("❌ This user is not banned.")
                    return
                
                await interaction.guild.unban(user, reason=f"Unbanned by {interaction.user}: {reason}")
                
                # Remove from database
                self.db.remove_ban(user_id)
                
                embed = create_moderation_embed(
                    title="✅ User Unbanned",
                    description=f"{user.mention} has been unbanned from the server.",
                    color="success",
                    user=user,
                    moderator=interaction.user,
                    reason=reason
                )
                
                await interaction.followup.send(embed=embed)
                await self.log_moderation_action(embed)
                
            except ValueError:
                await interaction.followup.send("❌ Invalid user ID format.")
            except discord.NotFound:
                await interaction.followup.send("❌ User not found.")
            except discord.Forbidden:
                await interaction.followup.send("❌ Could not unban user. Check bot permissions.")
                
        except Exception as e:
            print(f"Error in unban command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for unban command: {e}")
    
    @app_commands.command(name="purge", description="Delete multiple messages")
    @app_commands.describe(
        amount="Number of messages to delete (1-100)",
        user="Only delete messages from this user (optional)"
    )
    async def purge(self, interaction: discord.Interaction, amount: int, user: Optional[discord.Member] = None):
        """Purge messages"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            if amount < 1 or amount > 100:
                await interaction.response.send_message("❌ Amount must be between 1 and 100.", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            try:
                def check(msg):
                    if user:
                        return msg.author == user
                    return True
                
                deleted = await interaction.channel.purge(limit=amount, check=check)
                
                embed = create_moderation_embed(
                    title="🗑️ Messages Purged",
                    description=f"Deleted {len(deleted)} message(s).",
                    color="success",
                    moderator=interaction.user,
                    Channel=interaction.channel.mention,
                    Amount=len(deleted)
                )
                
                if user:
                    embed.add_field(name="User Filter", value=user.mention, inline=True)
                
                await interaction.followup.send(embed=embed, delete_after=10)
                await self.log_moderation_action(embed)
                
            except discord.Forbidden:
                await interaction.followup.send("❌ Could not delete messages. Check bot permissions.")
                
        except Exception as e:
            print(f"Error in purge command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for purge command: {e}")
    
    @app_commands.command(name="modinfo", description="Get moderation information about a user")
    @app_commands.describe(user="The user to check")
    async def modinfo(self, interaction: discord.Interaction, user: discord.Member):
        """Get moderation info for a user"""
        try:
            if not has_mod_permissions(interaction.user):
                await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
                return
            
            await interaction.response.defer()
            
            warnings = self.db.get_warnings(user.id)
            mute_record = self.db.get_mute(user.id)
            ban_record = self.db.get_bans(user.id) if hasattr(self.db, 'get_bans') else None
            
            embed = create_moderation_embed(
                title="📊 Moderation Info",
                description=f"Moderation information for {user.mention}",
                color="info",
                user=user
            )
            
            embed.add_field(name="Warnings", value=len(warnings), inline=True)
            embed.add_field(name="Currently Muted", value="Yes" if mute_record else "No", inline=True)
            embed.add_field(name="Banned", value="Yes" if ban_record else "No", inline=True)
            
            if warnings:
                recent_warning = warnings[-1]
                embed.add_field(
                    name="Latest Warning",
                    value=f"**{recent_warning['reason']}**\n<@{recent_warning['moderator_id']}> • <t:{int(datetime.fromisoformat(recent_warning['timestamp']).timestamp())}:R>",
                    inline=False
                )
            
            if mute_record:
                embed.add_field(
                    name="Mute Details",
                    value=f"**Reason:** {mute_record['reason']}\n**Duration:** {format_duration(mute_record['duration'])}\n**Expires:** <t:{int(datetime.fromisoformat(mute_record['expires_at']).timestamp())}:R>",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Error in modinfo command: {e}")
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ An error occurred: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ An error occurred: {str(e)}", ephemeral=True)
            except:
                print(f"Could not send error message for modinfo command: {e}")

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
