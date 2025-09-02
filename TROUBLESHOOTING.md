# Discord Bot Troubleshooting Guide

## 🚨 Common Error: "Unknown interaction" (Error 10062)

This error occurs when Discord interactions expire or become invalid. Here's how to fix it:

### **What Causes This Error:**
- Interactions timeout after 15 minutes
- Bot takes too long to respond
- Network delays or bot lag
- Discord API issues

### **How to Fix:**

1. **Restart Your Bot**
   ```bash
   # Stop the current bot (Ctrl+C)
   # Then restart:
   python main.py
   ```

2. **Use Guild-Specific Commands**
   - Set `GUILD_ID` in your `.env` file
   - Guild commands sync faster and are more reliable
   - Global commands can take up to 1 hour to appear

3. **Manual Command Sync**
   - Use `/sync` command (requires admin permissions)
   - This forces Discord to update your commands immediately

4. **Check Bot Permissions**
   - Ensure bot has "Send Messages" permission
   - Verify bot role is above users it needs to moderate
   - Check bot has "Use Slash Commands" permission

## 🔧 Quick Fixes

### **Test Basic Commands First:**
1. `/ping` - Should show bot latency
2. `/test` - Should show basic bot info
3. `/help` - Should show command list

### **If Commands Don't Work:**
1. **Check Bot Status:**
   - Bot should show as "Online" in Discord
   - Console should show "Bot setup complete!"

2. **Verify Environment:**
   ```bash
   # Check if .env file exists
   python start_bot.py
   ```

3. **Reinstall Dependencies:**
   ```bash
   pip uninstall discord.py
   pip install discord.py>=2.3.0
   ```

## 📋 Environment Setup Checklist

- [ ] Created `.env` file from `env_template.txt`
- [ ] Set `BOT_TOKEN=your_actual_token`
- [ ] Set `GUILD_ID=your_server_id` (optional but recommended)
- [ ] Bot invited to server with proper permissions
- [ ] Bot role positioned above users it needs to moderate

## 🚀 Bot Startup Process

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Environment File:**
   ```bash
   copy env_template.txt .env
   # Edit .env with your bot token
   ```

3. **Start Bot:**
   ```bash
   python start_bot.py
   # or
   python main.py
   ```

4. **Expected Console Output:**
   ```
   🚀 Starting Discord Moderation Bot...
   📝 Make sure you have created a .env file with your bot token!
   🤖 [Bot Name] is online and ready!
   📊 Connected to 1 guild(s)
   🔄 Syncing slash commands to guild [ID]
   ✅ Commands synced successfully!
   ✅ Bot setup complete!
   ✅ Loaded moderation cog
   ```

## 🆘 Still Having Issues?

### **Check Console for Errors:**
- Look for red ❌ messages
- Check for import errors
- Verify bot token is correct

### **Common Problems:**

**"BOT_TOKEN not found":**
- Create `.env` file
- Set `BOT_TOKEN=your_token`

**"Failed to sync commands":**
- Check bot permissions
- Verify guild ID is correct
- Use `/sync` command manually

**"Interaction expired":**
- Restart bot
- Use guild-specific commands
- Check bot response time

**"Permission denied":**
- Give bot proper permissions
- Position bot role correctly
- Check channel permissions

## 📞 Getting Help

1. **Check this troubleshooting guide first**
2. **Look at console error messages**
3. **Verify your `.env` configuration**
4. **Test with simple commands like `/ping`**
5. **Restart the bot completely**

## 🔍 Debug Mode

To get more detailed error information, you can temporarily add this to your `.env` file:
```env
DEBUG=true
```

This will show more detailed logging in the console.

---

**Remember:** Most interaction errors are resolved by restarting the bot and ensuring proper command syncing. Guild-specific commands are more reliable than global commands.
