import discord
from discord.ext import commands
import asyncio
import contextlib
import os
import asyncio
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
    
    # Wait a bit before syncing commands
    await asyncio.sleep(2)
    
    # Sync slash commands
    try:
        if GUILD_ID:
            print(f"🔄 Syncing slash commands to guild {GUILD_ID}")
            # Ensure global commands are available in the target guild immediately
            bot.tree.copy_global_to(guild=discord.Object(id=GUILD_ID))
            await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        else:
            print("🔄 Syncing slash commands globally")
            await bot.tree.sync()
        print("✅ Commands synced successfully!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
    
    print("✅ Bot setup complete!")

@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a guild"""
    print(f"🎉 Joined guild: {guild.name} (ID: {guild.id})")
    
    # Wait a bit before syncing commands
    await asyncio.sleep(2)
    
    # Sync commands to new guild
    try:
        # Ensure global commands are copied to the new guild before syncing
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
        print(f"✅ Synced commands to {guild.name}")
    except Exception as e:
        print(f"❌ Failed to sync commands to {guild.name}: {e}")

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Simple ping command to test bot responsiveness"""
    try:
        latency = round(bot.latency * 1000)
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=0x00ff00
        )
        embed.set_footer(text="Moderation Bot")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="test", description="Test command to verify bot is working")
async def test_command(interaction: discord.Interaction):
    """Simple test command"""
    try:
        embed = discord.Embed(
            title="✅ Bot Test",
            description="The bot is working correctly!",
            color=0x00ff00
        )
        embed.add_field(name="Server", value=interaction.guild.name, inline=True)
        embed.add_field(name="Channel", value=interaction.channel.name, inline=True)
        embed.add_field(name="User", value=interaction.user.display_name, inline=True)
        embed.set_footer(text="Moderation Bot Test")
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Test failed: {str(e)}", ephemeral=True)

@bot.tree.command(name="help", description="Show available moderation commands")
async def help_command(interaction: discord.Interaction):
    """Help command showing all available moderation features"""
    try:
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
            value="• `/ping` - Check bot latency\n• `/test` - Test bot functionality\n• `/help` - Show this help message",
            inline=False
        )
        
        embed.add_field(
            name="🔐 Permissions",
            value="Commands require moderation permissions:\n• Administrator role\n• Custom admin/moderator roles\n• Manage Messages permission",
            inline=False
        )
        
        embed.set_footer(text="Moderation Bot • Use / before commands")
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)


class RespectView(discord.ui.View):
    """Interactive view allowing users to press F to pay respect"""
    def __init__(self, initiator: discord.User, subject_text: str, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.initiator = initiator
        self.subject_text = subject_text
        self._user_ids_who_paid: set[int] = set()

    def _build_embed(self) -> discord.Embed:
        paid_count = len(self._user_ids_who_paid)
        embed = discord.Embed(
            title="🕯️ Pay Respects",
            description=f"Press the button below to pay your respects to **{self.subject_text}**.",
            color=0x2b2d31
        )
        embed.add_field(name="Respects Paid", value=str(paid_count), inline=True)
        if paid_count > 0:
            names_preview = ", ".join(f"<@{uid}>" for uid in list(self._user_ids_who_paid)[:5])
            embed.add_field(name="Recently", value=names_preview, inline=False)
        embed.set_footer(text="Press F to pay respect")
        return embed

    @discord.ui.button(label="Press F to pay respect", style=discord.ButtonStyle.primary, emoji="🇫")
    async def press_f(self, interaction: discord.Interaction, button: discord.ui.Button):  # type: ignore[override]
        if interaction.user.id in self._user_ids_who_paid:
            await interaction.response.send_message("You already paid your respect.", ephemeral=True)
            return
        self._user_ids_who_paid.add(interaction.user.id)
        try:
            await interaction.response.edit_message(embed=self._build_embed(), view=self)
        except Exception as e:
            try:
                await interaction.followup.send(f"❌ Couldn't update: {str(e)}", ephemeral=True)
            except:
                pass

    async def on_timeout(self) -> None:
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True


@bot.tree.command(name="respect", description="Start a 'press F to pay respect' moment")
@discord.app_commands.describe(subject="What are we paying respect to?")
async def respect(interaction: discord.Interaction, subject: str | None = None):
    try:
        subject_text = subject.strip() if subject else "this moment"
        view = RespectView(interaction.user, subject_text)
        await interaction.response.send_message(embed=view._build_embed(), view=view)
    except Exception as e:
        if not interaction.response.is_done():
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="sync", description="Sync slash commands (Admin only)")
async def sync_commands(interaction: discord.Interaction):
    """Sync slash commands manually"""
    # Check if user has admin permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
        return
    
    try:
        await interaction.response.defer()
        
        # Sync commands
        if interaction.guild_id:
            # Copy global commands into this guild and sync
            bot.tree.copy_global_to(guild=interaction.guild)
            await bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send("✅ Commands synced to this server!")
        else:
            await bot.tree.sync()
            await interaction.followup.send("✅ Commands synced globally!")
            
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to sync commands: {str(e)}")

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
        # Start the FastAPI server in the background
        try:
            from web import serve as start_web
            web_task = asyncio.create_task(start_web())
            print("🌐 Web server starting...")
        except Exception as e:
            print(f"⚠️ Failed to start web server: {e}")
            web_task = None
        # Start the Discord bot (blocking until shutdown)
        await bot.start(BOT_TOKEN)
        # When bot stops, cancel web server if it's running
        if web_task:
            web_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await web_task

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in environment variables!")
        print("Please create a .env file with your bot token:")
        print("1. Copy env_template.txt to .env")
        print("2. Fill in your bot token and other settings")
        print("3. Restart the bot")
        print("\nRequired environment variables:")
        print("BOT_TOKEN=your_bot_token_here")
        print("GUILD_ID=your_guild_id_here (optional)")
        print("LOG_CHANNEL_ID=your_log_channel_id_here (optional)")
        print("ADMIN_ROLE_ID=your_admin_role_id_here (optional)")
        print("MODERATOR_ROLE_ID=your_moderator_role_id_here (optional)")
        exit(1)
    
    print("🚀 Starting Discord Moderation Bot...")
    print("📝 Make sure you have created a .env file with your bot token!")
    asyncio.run(main())
