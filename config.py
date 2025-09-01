import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID', 0))  # Your Discord server ID

# Moderation Settings
MAX_WARNINGS = 3  # Maximum warnings before auto-ban
MUTE_DURATION = 300  # Default mute duration in seconds (5 minutes)
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', 0))  # Channel for moderation logs

# Role IDs (you'll need to set these in your Discord server)
ADMIN_ROLE_ID = int(os.getenv('ADMIN_ROLE_ID', 0))
MODERATOR_ROLE_ID = int(os.getenv('MODERATOR_ROLE_ID', 0))

# Colors for embeds
EMBED_COLORS = {
    'success': 0x00ff00,  # Green
    'warning': 0xffff00,  # Yellow
    'error': 0xff0000,    # Red
    'info': 0x0099ff      # Blue
}
