import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from telegram.helpers import escape_markdown

from src.config import BOT_TOKEN
from src.database.db_manager import db
from src.handlers.feature_handlers import (
    password_gen_start, password_seed_process, password_settings_callback,
    qr_gen_start, qr_data_process, qr_settings_callback,
    PASS_SEED, PASS_SETTINGS, QR_DATA, QR_SETTINGS, cancel
)

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.add_user(user.id, user.username)
    
    keyboard = [
        [InlineKeyboardButton("🔐 Password Gen", callback_data='pass_gen')],
        [InlineKeyboardButton("🖼 QR Generator", callback_data='qr_gen')],
        [InlineKeyboardButton("📈 My Stats", callback_data='user_stats')],
        [InlineKeyboardButton("❓ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    escaped_name = escape_markdown(user.first_name or "User", version=2)
    welcome_text = (
        f"🚀 *Welcome to ToolVerseXBot, {escaped_name}*\\!\n\n"
        "Your premium assistant for secure credentials and stunning visual assets\\.\n\n"
        "Select a tool from the menu below to get started\\."
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='MarkdownV2')
    else:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup, parse_mode='MarkdownV2')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *ToolVerseX Help Menu*\n\n"
        "• *🔐 Password Gen*: Generates a personalized high\\-strength password using a custom keyword or name seed\\. Fully customize length, symbols, numbers, and case options\\.\n\n"
        "• *🖼 QR Generator*: Converts text or URLs into customized high\\-quality QR codes\\. Choose from neon color themes, add smooth light aura glows, and embed security/link icons in the center\\.\n\n"
        "Use the buttons to navigate\\! No need to type commands\\."
    )
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='MarkdownV2')
    else:
        await update.callback_query.message.edit_text(help_text, reply_markup=reply_markup, parse_mode='MarkdownV2')

async def show_user_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stats = db.get_user_stats(user_id)
    
    if stats:
        text = (
            "👤 *Your Statistics*\n\n"
            f"📅 Joined: `{escape_markdown(stats[2], version=2)}`\n"
            f"🔢 Commands: `{stats[3]}`\n"
            f"🖼 QRs Made: `{stats[4]}`\n"
            f"🔐 Passwords: `{stats[5]}`"
        )
    else:
        text = "No stats found yet!"
        
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='start')]]
    await update.callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='MarkdownV2')



if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Password Gen Conversation Handler
    pass_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(password_gen_start, pattern='^pass_gen$')],
        states={
            PASS_SEED: [MessageHandler(filters.TEXT & ~filters.COMMAND, password_seed_process)],
            PASS_SETTINGS: [CallbackQueryHandler(password_settings_callback, pattern='^pset_')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )

    # QR Gen Conversation Handler
    qr_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(qr_gen_start, pattern='^qr_gen$')],
        states={
            QR_DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, qr_data_process)],
            QR_SETTINGS: [CallbackQueryHandler(qr_settings_callback, pattern='^qrset_')],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_message=False
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(start, pattern='^start$'))
    app.add_handler(CallbackQueryHandler(help_command, pattern='^help$'))
    app.add_handler(CallbackQueryHandler(show_user_stats, pattern='^user_stats$'))
    app.add_handler(pass_conv)
    app.add_handler(qr_conv)

    print("ToolVerseXBot is running...")
    app.run_polling()
