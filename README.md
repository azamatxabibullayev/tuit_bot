# Official telegram bot for AKTSIM faculty of 'Tashkent University of Information Technologies named after Muhammad ibn Musa al-Khwarizmi' (TUIT) 🤖

This is a Telegram bot built using [Aiogram](https://docs.aiogram.dev/en/dev-3.x/) v3 to facilitate communication
between students and university administration. The bot allows students to submit applications to their faculty, while
admins can manage and edit info sections dynamically.

## Features

- `/start` command to initiate interaction with the bot.
- `/help` command that explains the bot’s purpose.
- Multilingual support: Uzbek 🇺🇿 and Russian 🇷🇺.
- Student and Admin user roles.
- Admins can:
    - View and edit informational sections.
    - Receive and reply to student applications.
- FSM (Finite State Machine) for managing user input steps.
- SQLite database for storing and managing data.

## Technologies Used

- Python 3.10+
- Aiogram v3 (Async Telegram bot framework)
- SQLite (Lightweight database)
- FSM (aiogram.fsm.state) for user interactions
- Logging for debugging and monitoring


