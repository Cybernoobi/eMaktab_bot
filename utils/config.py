with open('settings.json', 'r', encoding='utf-8') as f:
    import json
    config = json.load(f)

DATABASE_NAME: str = config['DB_NAME']  # Write your name for db
TG_API: str = config['TG_API']  # Write your token from telegram bot
NOPECHA_API_KEY: str = config['NOPECHA']
DEBUG: bool = config['DEBUG']
