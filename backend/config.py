import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
parentdir = os.path.dirname(basedir)
dotenv_path = os.path.join(parentdir, '.env')
load_dotenv(dotenv_path)

class Config:
    # Twilio Settings
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Flask Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-this')
    
    # Paths
    UPLOAD_FOLDER = os.path.join(parentdir, 'uploads')
    CAMPAIGNS_FOLDER = os.path.join(parentdir, 'campaigns')
    DATABASE_PATH = os.path.join(parentdir, 'database.db')
    
    # Call Settings
    CALL_DELAY_SECONDS = 2
    MAX_MESSAGE_LENGTH = 500

# Validate required settings
def validate_config():
    missing = []
    if not Config.TWILIO_ACCOUNT_SID or Config.TWILIO_ACCOUNT_SID == 'ACyour_account_sid_here':
        missing.append('TWILIO_ACCOUNT_SID')
    if not Config.TWILIO_AUTH_TOKEN or Config.TWILIO_AUTH_TOKEN == 'your_auth_token_here':
        missing.append('TWILIO_AUTH_TOKEN')
    if not Config.TWILIO_PHONE_NUMBER or Config.TWILIO_PHONE_NUMBER == '+your_twilio_number_here':
        missing.append('TWILIO_PHONE_NUMBER')
    if not Config.SECRET_KEY or Config.SECRET_KEY == 'your_random_secret_key_here_change_this':
        missing.append('SECRET_KEY')
    
    if missing:
        raise ValueError(f"Missing required config in .env file: {', '.join(missing)}")
    
    return True