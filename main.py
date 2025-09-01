import discord
from discord.ext import commands
import asyncio
import os
from config import BOT_TOKEN, GUILD_ID

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f"🤖 {bot.user} is online and ready!")
    print(f"📊 Connected to {len(bot.guilds)} guild(s)")
    
    # Sync slash commands
    if GUILD_ID:
        print(f"🔄 Syncing slash commands to guild {GUILD_ID}")
        await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    else:
        print("🔄 Syncing slash commands globally")
        await bot.tree.sync()
    
    print("✅ Bot setup complete!")

@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a guild"""
    print(f"🎉 Joined guild: {guild.name} (ID: {guild.id})")
    
    # Sync commands to new guild
    await bot.tree.sync(guild=guild)
    print(f"✅ Synced commands to {guild.name}")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Simple ping command to test bot responsiveness"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: **{latency}ms**",
        color=0x00ff00
    )
    embed.set_footer(text="Moderation Bot")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show available moderation commands")
async def help_command(interaction: discord.Interaction):
    """Help command showing all available moderation features"""
    embed = discord.Embed(
        title="🛡️ Moderation Bot Commands",
        description="Here are all the available moderation commands:",
        color=0x0099ff
    )
    
    # Moderation commands
    embed.add_field(
        name="⚠️ Warning System",
        value="• `/warn` - Warn a user\n• `/warnings` - View user warnings\n• `/clearwarnings` - Clear user warnings",
        inline=False
    )
    
    embed.add_field(
        name="🔇 Mute System",
        value="• `/mute` - Mute a user temporarily\n• `/unmute` - Unmute a user immediately",
        inline=False
    )
    
    embed.add_field(
        name="👢 User Management",
        value="• `/kick` - Kick a user from server\n• `/ban` - Ban a user from server\n• `/unban` - Unban a user",
        inline=False
    )
    
    embed.add_field(
        name="🗑️ Message Management",
        value="• `/purge` - Delete multiple messages\n• `/modinfo` - Get user moderation info",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Utility",
        value="• `/ping` - Check bot latency\n• `/help` - Show this help message",
        inline=False
    )
    
    embed.add_field(
        name="🔐 Permissions",
        value="Commands require moderation permissions:\n• Administrator role\n• Custom admin/moderator roles\n• Manage Messages permission",
        inline=False
    )
    
    embed.set_footer(text="Moderation Bot • Use / before commands")
    await interaction.response.send_message(embed=embed)

async def load_extensions():
    """Load all cog extensions"""
    try:
        await bot.load_extension("cogs.moderation")
        print("✅ Loaded moderation cog")
    except Exception as e:
        print(f"❌ Failed to load moderation cog: {e}")

async def main():
    """Main function to start the bot"""
    async with bot:
        await load_extensions()
        await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token:")
        print("BOT_TOKEN=your_bot_token_here")
        print("GUILD_ID=your_guild_id_here")
        print("LOG_CHANNEL_ID=your_log_channel_id_here")
        print("ADMIN_ROLE_ID=your_admin_role_id_here")
        print("MODERATOR_ROLE_ID=your_moderator_role_id_here")
        exit(1)
    
    print("🚀 Starting Discord Moderation Bot...")
    asyncio.run(main())
