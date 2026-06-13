from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.helpers import escape_markdown
from ..utils.tools import generate_advanced_password, generate_advanced_qr
from ..database.db_manager import db
import os

# States for ConversationHandler
PASS_SEED, PASS_SETTINGS, QR_DATA, QR_SETTINGS = range(4)

# ----------------- PASSWORD GENERATOR HANDLERS -----------------

async def password_gen_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📝 *Enter a name, word, or keyword to base your password on:*\n"
        "_(e.g., your name, business, or a memorable word)_",
        parse_mode='Markdown'
    )
    return PASS_SEED

def get_pass_settings_keyboard(context):
    length = context.user_data.get('pass_length', 16)
    symbols = context.user_data.get('pass_symbols', True)
    numbers = context.user_data.get('pass_numbers', True)
    uppercase = context.user_data.get('pass_uppercase', True)
    style = context.user_data.get('pass_style', 'memorable')
    
    style_text = "🎭 Style: Memorable" if style == 'memorable' else "🧩 Style: Random"
    sym_text = "🔣 Symbols: ✅" if symbols else "🔣 Symbols: ❌"
    num_text = "🔢 Numbers: ✅" if numbers else "🔢 Numbers: ❌"
    upper_text = "🔠 Uppercase: ✅" if uppercase else "🔠 Uppercase: ❌"
    
    # Length buttons
    len_buttons = [
        InlineKeyboardButton("12", callback_data="pset_len_12"),
        InlineKeyboardButton("16", callback_data="pset_len_16"),
        InlineKeyboardButton("20", callback_data="pset_len_20"),
        InlineKeyboardButton("24", callback_data="pset_len_24")
    ]
    for idx, btn in enumerate(len_buttons):
        if int(btn.text) == length:
            len_buttons[idx] = InlineKeyboardButton(f"• {btn.text} •", callback_data=btn.callback_data)
            
    keyboard = [
        [InlineKeyboardButton(style_text, callback_data="pset_toggle_style")],
        [InlineKeyboardButton(num_text, callback_data="pset_toggle_nums"),
         InlineKeyboardButton(sym_text, callback_data="pset_toggle_syms")],
        [InlineKeyboardButton(upper_text, callback_data="pset_toggle_upper")],
        len_buttons,
        [InlineKeyboardButton("⚡ Generate Password", callback_data="pset_generate")],
        [InlineKeyboardButton("🔙 Cancel", callback_data="pset_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_pass_settings_text(seed, context):
    length = context.user_data.get('pass_length', 16)
    symbols = context.user_data.get('pass_symbols', True)
    numbers = context.user_data.get('pass_numbers', True)
    uppercase = context.user_data.get('pass_uppercase', True)
    style = context.user_data.get('pass_style', 'memorable')
    
    style_str = "Memorable (smart leet-subs on base word)" if style == 'memorable' else "Random (fully obfuscated mix)"
    opt_list = []
    if numbers: opt_list.append("Numbers")
    if symbols: opt_list.append("Symbols")
    if uppercase: opt_list.append("Uppercase")
    options_str = ", ".join(opt_list) if opt_list else "None"
    
    escaped_seed = escape_markdown(seed, version=2)
    escaped_style = escape_markdown(style_str, version=2)
    escaped_options = escape_markdown(options_str, version=2)
    
    text = (
        f"🔐 *ToolVerseX Password Configurator*\n\n"
        f"Base keyword: `{escaped_seed}`\n\n"
        f"• *Style*: {escaped_style}\n"
        f"• *Length*: `{length}`\n"
        f"• *Active Options*: {escaped_options}\n\n"
        f"Adjust the configuration using the buttons below:"
    )
    return text

async def password_seed_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    seed = update.message.text
    context.user_data['pass_seed'] = seed
    
    context.user_data.setdefault('pass_length', 16)
    context.user_data.setdefault('pass_symbols', True)
    context.user_data.setdefault('pass_numbers', True)
    context.user_data.setdefault('pass_uppercase', True)
    context.user_data.setdefault('pass_style', 'memorable')
    
    text = get_pass_settings_text(seed, context)
    keyboard = get_pass_settings_keyboard(context)
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='MarkdownV2')
    return PASS_SETTINGS

async def password_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "pset_cancel":
        await query.message.edit_text("❌ Password generation cancelled.")
        return ConversationHandler.END
        
    elif data == "pset_generate":
        seed = context.user_data.get('pass_seed')
        length = context.user_data.get('pass_length', 16)
        symbols = context.user_data.get('pass_symbols', True)
        numbers = context.user_data.get('pass_numbers', True)
        uppercase = context.user_data.get('pass_uppercase', True)
        style = context.user_data.get('pass_style', 'memorable')
        
        db.log_command(update.effective_user.id, "password_generator")
        
        password = generate_advanced_password(
            seed=seed,
            length=length,
            use_symbols=symbols,
            use_numbers=numbers,
            use_uppercase=uppercase,
            style=style
        )
        
        escaped_pass = escape_markdown(password, version=2)
        
        text = (
            f"⚡ *Your Premium Password is Ready*\\!\n\n"
            f"🔑 Monospace \\(tap to copy\\):\n"
            f"`{escaped_pass}`\n\n"
            f"🔒 _Keep this password safe and secure\\._"
        )
        await query.message.edit_text(text, parse_mode='MarkdownV2')
        return ConversationHandler.END
        
    elif data == "pset_toggle_style":
        current = context.user_data.get('pass_style', 'memorable')
        context.user_data['pass_style'] = 'random' if current == 'memorable' else 'memorable'
        
    elif data == "pset_toggle_nums":
        current = context.user_data.get('pass_numbers', True)
        context.user_data['pass_numbers'] = not current
        
    elif data == "pset_toggle_syms":
        current = context.user_data.get('pass_symbols', True)
        context.user_data['pass_symbols'] = not current
        
    elif data == "pset_toggle_upper":
        current = context.user_data.get('pass_uppercase', True)
        context.user_data['pass_uppercase'] = not current
        
    elif data.startswith("pset_len_"):
        val = int(data.split("_")[2])
        context.user_data['pass_length'] = val
        
    seed = context.user_data.get('pass_seed')
    text = get_pass_settings_text(seed, context)
    keyboard = get_pass_settings_keyboard(context)
    await query.message.edit_text(text, reply_markup=keyboard, parse_mode='MarkdownV2')
    return PASS_SETTINGS


# ----------------- QR GENERATOR HANDLERS -----------------

async def qr_gen_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(
        "📝 *Send the URL or text you want to convert into a Premium QR Code:*",
        parse_mode='Markdown'
    )
    return QR_DATA

def get_qr_settings_keyboard(context):
    theme = context.user_data.get('qr_theme', 'plain')
    glow = context.user_data.get('qr_glow', False)
    center = context.user_data.get('qr_center', 'none')
    
    themes = [
        ("Cyan 🌌", "neon_cyan"),
        ("Pink 🌸", "neon_pink"),
        ("Green 🟢", "neon_green"),
        ("Gold 🏆", "luxury_gold"),
        ("Dark ⚪", "classic_dark"),
        ("Plain BW 🔳", "plain")
    ]
    theme_buttons = []
    for label, val in themes:
        btn_label = f"• {label} •" if theme == val else label
        theme_buttons.append(InlineKeyboardButton(btn_label, callback_data=f"qrset_theme_{val}"))
        
    glow_text = "✨ Glow: ON ✅" if glow else "✨ Glow: OFF ❌"
    
    center_labels = [
        ("None ❌", "none"),
        ("Lock 🔒", "lock"),
        ("Link 🔗", "link")
    ]
    center_buttons = []
    for label, val in center_labels:
        btn_label = f"• {label} •" if center == val else label
        center_buttons.append(InlineKeyboardButton(btn_label, callback_data=f"qrset_center_{val}"))
        
    keyboard = [
        theme_buttons[:3], # Cyan, Pink, Green
        theme_buttons[3:], # Gold, Dark, Plain
        [InlineKeyboardButton(glow_text, callback_data="qrset_toggle_glow")],
        center_buttons,
        [InlineKeyboardButton("🎨 Render QR Code", callback_data="qrset_generate")],
        [InlineKeyboardButton("🔙 Cancel", callback_data="qrset_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_qr_settings_text(data, context):
    theme = context.user_data.get('qr_theme', 'plain')
    glow = context.user_data.get('qr_glow', False)
    center = context.user_data.get('qr_center', 'none')
    
    theme_names = {
        "neon_cyan": "Neon Cyan (Cyan on Black)",
        "neon_pink": "Neon Pink (Pink on Black)",
        "neon_green": "Neon Green (Green on Black)",
        "luxury_gold": "Luxury Gold (Gold on Charcoal)",
        "classic_dark": "Classic Dark (White on Black)",
        "plain": "Plain BW (Black on White - Recommended)"
    }
    theme_str = theme_names.get(theme, theme)
    glow_str = "Enabled (Gaussian Blur Aura)" if glow else "Disabled"
    center_str = "None" if center == 'none' else center.capitalize()
    
    escaped_data = escape_markdown(data, version=2)
    escaped_theme = escape_markdown(theme_str, version=2)
    escaped_glow = escape_markdown(glow_str, version=2)
    escaped_center = escape_markdown(center_str, version=2)
    
    text = (
        f"🖼 *ToolVerseX QR Designer*\n\n"
        f"Payload data: `{escaped_data}`\n\n"
        f"• *Theme*: {escaped_theme}\n"
        f"• *Neon Glow*: {escaped_glow}\n"
        f"• *Center Icon*: {escaped_center}\n\n"
        f"Customize the visual output using the buttons below:"
    )
    return text

async def qr_data_process(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payload = update.message.text
    context.user_data['qr_text'] = payload
    
    context.user_data.setdefault('qr_theme', 'plain')
    context.user_data.setdefault('qr_glow', False)
    context.user_data.setdefault('qr_center', 'none')
    
    text = get_qr_settings_text(payload, context)
    keyboard = get_qr_settings_keyboard(context)
    
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode='MarkdownV2')
    return QR_SETTINGS

async def qr_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "qrset_cancel":
        await query.message.edit_text("❌ QR code generation cancelled.")
        return ConversationHandler.END
        
    elif data == "qrset_generate":
        payload = context.user_data.get('qr_text')
        theme = context.user_data.get('qr_theme', 'plain')
        glow = context.user_data.get('qr_glow', False)
        center = context.user_data.get('qr_center', 'none')
        
        db.log_command(update.effective_user.id, "qr_generator")
        
        await query.message.edit_text("🎨 *Rendering visual assets\\.\\.\\. Please wait\\.*", parse_mode='MarkdownV2')
        
        path = generate_advanced_qr(
            data=payload,
            theme=theme,
            glow=glow,
            center_icon=center
        )
        
        # Send photo
        with open(path, 'rb') as photo:
            await query.message.reply_photo(
                photo=photo,
                caption="✨ *QR Code by ToolVerseX*\n\n"
                        f"🎨 Theme: `{theme.replace('_', ' ').title()}`\n"
                        f"⚡ Glow Effect: `{'Enabled' if glow else 'Disabled'}`\n"
                        f"🛡 Center Icon: `{center.capitalize()}`",
                parse_mode='MarkdownV2'
            )
            
        # Clean up file
        try:
            os.remove(path)
        except Exception:
            pass
            
        await query.message.delete()
        return ConversationHandler.END
        
    elif data == "qrset_toggle_glow":
        current = context.user_data.get('qr_glow', False)
        context.user_data['qr_glow'] = not current
        
    elif data.startswith("qrset_theme_"):
        theme_val = data.replace("qrset_theme_", "")
        context.user_data['qr_theme'] = theme_val
        if theme_val == "plain":
            context.user_data['qr_glow'] = False
            context.user_data['qr_center'] = "none"
        else:
            context.user_data['qr_glow'] = True
        
    elif data.startswith("qrset_center_"):
        center_val = data.replace("qrset_center_", "")
        context.user_data['qr_center'] = center_val
        
    payload = context.user_data.get('qr_text')
    text = get_qr_settings_text(payload, context)
    keyboard = get_qr_settings_keyboard(context)
    await query.message.edit_text(text, reply_markup=keyboard, parse_mode='MarkdownV2')
    return QR_SETTINGS


# ----------------- GENERAL HANDLERS -----------------

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operation cancelled.")
    return ConversationHandler.END
