import discord
from typing import Optional, Tuple
from config import ADMIN_ROLE_ID, MODERATOR_ROLE_ID, EMBED_COLORS

def has_mod_permissions(member: discord.Member) -> bool:
    """Check if a member has moderation permissions"""
    if member.guild_permissions.administrator:
        return True
    
    if ADMIN_ROLE_ID and discord.utils.get(member.roles, id=ADMIN_ROLE_ID):
        return True
    
    if MODERATOR_ROLE_ID and discord.utils.get(member.roles, id=MODERATOR_ROLE_ID):
        return True
    
    return member.guild_permissions.manage_messages or member.guild_permissions.kick_members

def can_moderate_target(moderator: discord.Member, target: discord.Member) -> Tuple[bool, str]:
    """Check if moderator can moderate the target user"""
    if target.guild_permissions.administrator:
        return False, "Cannot moderate administrators"
    
    if target.guild_permissions.manage_messages and not moderator.guild_permissions.administrator:
        return False, "Cannot moderate users with manage messages permission"
    
    if target.top_role >= moderator.top_role:
        return False, "Cannot moderate users with equal or higher role"
    
    return True, ""

def create_moderation_embed(
    title: str,
    description: str,
    color: str = "info",
    user: Optional[discord.Member] = None,
    moderator: Optional[discord.Member] = None,
    reason: Optional[str] = None,
    **kwargs
) -> discord.Embed:
    """Create a standardized moderation embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=EMBED_COLORS.get(color, EMBED_COLORS['info']),
        timestamp=discord.utils.utcnow()
    )
    
    if user:
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
    
    if moderator:
        embed.add_field(name="Moderator", value=f"{moderator.mention} ({moderator.id})", inline=True)
    
    if reason:
        embed.add_field(name="Reason", value=reason, inline=False)
    
    for key, value in kwargs.items():
        embed.add_field(name=key.title(), value=str(value), inline=True)
    
    embed.set_footer(text="Moderation Bot")
    return embed

def parse_duration(duration_str: str) -> Optional[int]:
    """Parse duration string (e.g., '5m', '1h', '2d') to seconds"""
    if not duration_str:
        return None
    
    duration_str = duration_str.lower().strip()
    total_seconds = 0
    
    try:
        if duration_str.endswith('s'):
            total_seconds = int(duration_str[:-1])
        elif duration_str.endswith('m'):
            total_seconds = int(duration_str[:-1]) * 60
        elif duration_str.endswith('h'):
            total_seconds = int(duration_str[:-1]) * 3600
        elif duration_str.endswith('d'):
            total_seconds = int(duration_str[:-1]) * 86400
        else:
            # Assume minutes if no unit specified
            total_seconds = int(duration_str) * 60
    except ValueError:
        return None
    
    return total_seconds if total_seconds > 0 else None

def format_duration(seconds: int) -> str:
    """Format seconds to human readable string"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours}h"
    else:
        days = seconds // 86400
        return f"{days}d"

def sanitize_reason(reason: str, max_length: int = 1000) -> str:
    """Sanitize and truncate reason text"""
    if not reason:
        return "No reason provided"
    
    # Remove excessive whitespace and newlines
    sanitized = " ".join(reason.split())
    
    # Truncate if too long
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length-3] + "..."
    
    return sanitized
