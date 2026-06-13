# ToolVerseXBot

ToolVerseXBot is an all-in-one utility Telegram bot built with Python and `python-telegram-bot`. It offers various tools useful for students, engineers, and general users, including a Password Generator, QR Code Generator, Age Calculator, and Attendance Calculator. The bot is designed with a modular architecture, a user-friendly inline keyboard interface, and an SQLite database for user statistics.

## Features

*   **Core Utilities**: Password Generator, QR Code Generator (Neon Theme), Age Calculator, Attendance Calculator.
*   **User Interface**: Inline keyboard buttons and menu-based navigation for a modern and intuitive experience.
*   **Database**: SQLite for storing user information and command usage statistics.
*   **Statistics**: User-specific and global usage reports.
*   **Modular Design**: Easily expandable for future features like AI Assistant, PDF Tools, Currency Converter, etc.

## Project Structure

```
ToolVerseXBot/
├── main.py
├── Procfile
├── requirements.txt
└── src/
    ├── __init__.py
    ├── config.py
    ├── database/
    │   ├── __init__.py
    │   └── db_manager.py
    ├── handlers/
    │   ├── __init__.py
    │   └── feature_handlers.py
    └── utils/
        ├── __init__.py
        └── tools.py
```

### File Explanations

*   `main.py`: The main entry point of the bot. It initializes the Telegram bot, registers all command and callback query handlers, and starts the polling process. It also handles the `/start` and `/help` commands, and displays user/global statistics.
*   `Procfile`: Used by deployment platforms like Railway and Render to specify the command to run the application.
*   `requirements.txt`: Lists all Python dependencies required for the project.
*   `src/config.py`: Contains configuration variables for the bot, such as the bot token, database path, and QR code settings. It uses `python-dotenv` to load environment variables.
*   `src/database/db_manager.py`: Manages all interactions with the SQLite database. It handles user registration, logging command usage, and retrieving user and global statistics.
*   `src/handlers/feature_handlers.py`: Contains the callback and message handlers for each specific bot feature (e.g., Password Generator, QR Code Generator, Age Calculator, Attendance Calculator). It also defines conversation states for multi-step interactions.
*   `src/utils/tools.py`: Provides utility functions for the various bot features, such as generating passwords, creating QR codes, calculating age, and calculating attendance.

## Installation (Local)

To run ToolVerseXBot locally, follow these steps:

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/ToolVerseXBot.git
    cd ToolVerseXBot
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Create a `.env` file:**

    Create a file named `.env` in the root directory of the project (`ToolVerseXBot/`) and add your Telegram Bot Token:

    ```
    BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
    ```

    Replace `YOUR_TELEGRAM_BOT_TOKEN` with the token you get from BotFather on Telegram.

5.  **Run the bot:**

    ```bash
    python3 main.py
    ```

    Your bot should now be running and accessible on Telegram.

## Deployment

### Deploying on Railway

1.  **Prepare your repository:**
    Ensure your project is pushed to a Git repository (e.g., GitHub, GitLab, Bitbucket).

2.  **Create a new project on Railway:**
    *   Go to [Railway.app](https://railway.app/) and log in.
    *   Click "New Project" and then "Deploy from Git Repo".
    *   Connect your Git provider and select your `ToolVerseXBot` repository.

3.  **Configure Environment Variables:**
    *   In your Railway project settings, go to the "Variables" tab.
    *   Add a new variable: `BOT_TOKEN` with your Telegram Bot Token as its value.

4.  **Build and Deploy:**
    *   Railway will automatically detect the `Procfile` and `requirements.txt` and deploy your bot.
    *   If it doesn't deploy automatically, you might need to manually trigger a deployment from the "Deployments" tab.

### Deploying on Render

1.  **Prepare your repository:**
    Ensure your project is pushed to a Git repository (e.g., GitHub, GitLab, Bitbucket).

2.  **Create a new Web Service on Render:**
    *   Go to [Render.com](https://render.com/) and log in.
    *   Click "New" -> "Web Service".
    *   Connect your Git provider and select your `ToolVerseXBot` repository.

3.  **Configure Web Service Settings:**
    *   **Name**: `toolversexbot` (or your preferred name)
    *   **Region**: Choose a region close to your users.
    *   **Branch**: `main` (or your default branch)
    *   **Root Directory**: `/` (if your `main.py` is in the root)
    *   **Runtime**: `Python 3`
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `python3 main.py`

4.  **Add Environment Variables:**
    *   Under "Advanced" -> "Environment Variables", add a new variable:
        *   **Key**: `BOT_TOKEN`
        *   **Value**: Your Telegram Bot Token

5.  **Create Web Service:**
    *   Click "Create Web Service". Render will now build and deploy your bot.

## Future Expansion

The modular design of ToolVerseXBot allows for easy integration of new features. Potential future additions include:

*   AI Assistant
*   PDF Tools
*   Currency Converter
*   Weather API Integration
*   Notes Generator
*   Student Dashboard

Feel free to contribute or suggest new features!
