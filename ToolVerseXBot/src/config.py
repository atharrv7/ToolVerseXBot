import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Database Configuration
DB_PATH = "toolversex.db"

# QR Code Settings
QR_TEMP_DIR = "temp_qr"
os.makedirs(QR_TEMP_DIR, exist_ok=True)

# Branding
BOT_NAME = "ToolVerseX"
BRANDING_TEXT = "Powered by ToolVerseX"
