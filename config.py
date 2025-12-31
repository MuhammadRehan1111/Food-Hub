"""
Configuration file for the Restaurant Ordering System.
Defines paths and constants used throughout the application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent

# Data directory
DATA_DIR = BASE_DIR / "data"

# Data files
MENU_FILE = DATA_DIR / "menu.json"
ORDERS_FILE = DATA_DIR / "orders.json"
DEALS_FILE = DATA_DIR / "deals.json"
CATEGORIES_FILE = DATA_DIR / "categories.json"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Images directory
IMAGES_DIR = DATA_DIR / "images"

# Authentication
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# API Keys
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Payment Methods
PAYMENT_METHODS = ["Cash", "Credit Card", "Debit Card", "Online Transfer"]
