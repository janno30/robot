# Discord Moderation Bot

A powerful Discord bot built with Python and discord.py that provides comprehensive moderation features using slash commands.

## 🚀 Features

### ⚠️ Warning System
- **`/warn`** - Issue warnings to users with reasons
- **`/warnings`** - View all warnings for a specific user
- **`/clearwarnings`** - Clear all warnings for a user
- Auto-ban system when users reach maximum warnings

### 🔇 Mute System
- **`/mute`** - Temporarily mute users with custom duration
- **`/unmute`** - Immediately unmute users
- Automatic unmute after duration expires
- Customizable mute durations (seconds, minutes, hours, days)

### 👢 User Management
- **`/kick`** - Remove users from the server
- **`/ban`** - Permanently ban users from the server
- **`/unban`** - Remove bans from users

### 🗑️ Message Management
- **`/purge`** - Bulk delete messages (with optional user filtering)
- **`/modinfo`** - Get comprehensive moderation history for users

### 🔐 Permission System
- Role-based permission system
- Custom admin and moderator roles
- Fallback to Discord's built-in permissions
- Hierarchical moderation (can't moderate users with equal/higher roles)

### 📊 Logging & Monitoring
- Comprehensive moderation action logging
- Configurable log channel
- Detailed audit trails for all actions
- Beautiful embed-based notifications

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Discord bot token
- Discord server with appropriate permissions

### Step 1: Clone/Download
Download or clone this repository to your local machine.

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Bot Setup
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" section
4. Create a bot and copy the token
5. Enable the following bot permissions:
   - Send Messages
   - Embed Links
   - Manage Messages
   - Kick Members
   - Ban Members
   - Manage Roles
   - Read Message History

### Step 4: Configuration
1. Copy `env_example.txt` to `.env`
2. Fill in your configuration:
   ```env
   BOT_TOKEN=your_actual_bot_token
   GUILD_ID=your_server_id
   LOG_CHANNEL_ID=your_log_channel_id
   ADMIN_ROLE_ID=your_admin_role_id
   MODERATOR_ROLE_ID=your_moderator_role_id
   ```

### Step 5: Invite Bot
1. Go to OAuth2 > URL Generator in Discord Developer Portal
2. Select "bot" scope
3. Select required permissions
4. Use the generated URL to invite the bot to your server

### Step 6: Run the Bot
```bash
python main.py
```

## 📋 Available Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/warn` | Warn a user | `/warn @user reason` |
| `/warnings` | View user warnings | `/warnings @user` |
| `/clearwarnings` | Clear user warnings | `/clearwarnings @user` |
| `/mute` | Mute a user | `/mute @user 5m reason` |
| `/unmute` | Unmute a user | `/unmute @user` |
| `/kick` | Kick a user | `/kick @user reason` |
| `/ban` | Ban a user | `/ban @user reason` |
| `/unban` | Unban a user | `/unban user_id reason` |
| `/purge` | Delete messages | `/purge 10 @user` |
| `/modinfo` | User moderation info | `/modinfo @user` |
| `/ping` | Check bot latency | `/ping` |
| `/help` | Show help menu | `/help` |

## ⚙️ Configuration Options

### Environment Variables
- **`BOT_TOKEN`** - Your Discord bot token (required)
- **`GUILD_ID`** - Your Discord server ID (optional, for guild-specific commands)
- **`LOG_CHANNEL_ID`** - Channel ID for moderation logs (optional)
- **`ADMIN_ROLE_ID`** - Custom admin role ID (optional)
- **`MODERATOR_ROLE_ID`** - Custom moderator role ID (optional)

### Bot Settings (in `config.py`)
- **`MAX_WARNINGS`** - Maximum warnings before auto-ban (default: 3)
- **`MUTE_DURATION`** - Default mute duration in seconds (default: 300)
- **`EMBED_COLORS`** - Custom colors for different types of embeds

## 🔧 Customization

### Adding New Commands
1. Create a new cog in the `cogs/` directory
2. Inherit from `commands.Cog`
3. Use `@app_commands.command()` decorator for slash commands
4. Add the cog to `main.py` in the `load_extensions()` function

### Modifying Permissions
- Edit the `has_mod_permissions()` function in `utils.py`
- Modify role IDs in your `.env` file
- Adjust permission checks in individual commands

### Database Customization
- The bot uses a simple JSON-based database
- Modify `database.py` to add new data types
- Extend the `ModerationDB` class for additional functionality

## 🚨 Troubleshooting

### Common Issues

**Bot doesn't respond to commands:**
- Check if slash commands are synced
- Verify bot has proper permissions
- Ensure bot is online and connected

**Permission errors:**
- Verify bot has required permissions in your server
- Check role hierarchy (bot's role must be above users it moderates)
- Ensure custom role IDs are correct

**Commands not showing up:**
- Wait for Discord to update (can take up to 1 hour for global commands)
- Use guild-specific commands for immediate testing
- Check bot logs for sync errors

### Getting Help
1. Check the console output for error messages
2. Verify your `.env` configuration
3. Ensure all dependencies are installed
4. Check Discord Developer Portal bot settings

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📞 Support

If you need help setting up or using the bot:
1. Check the troubleshooting section above
2. Review Discord.py documentation
3. Open an issue on this repository

---

**Note:** This bot is designed for educational and practical use. Always ensure you comply with Discord's Terms of Service and your server's rules when using moderation features.
