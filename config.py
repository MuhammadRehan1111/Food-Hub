"""
Configuration file for the Restaurant Ordering System.
Contains API keys, admin credentials, and app settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# GOOGLE GEMINI API CONFIGURATION
# =============================================================================
# Set your API key here or use environment variable GEMINI_API_KEY
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyB2NLt-FuFpQZ6r1CffB8f9WY_-nGLIIzo")

# =============================================================================
# ADMIN CREDENTIALS
# =============================================================================
# Change these before deployment!
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Cashier Credentials
CASHIER_USERNAME = "cashier"
CASHIER_PASSWORD = "cashier123"

# =============================================================================
# APP SETTINGS
# =============================================================================
APP_NAME = "Restaurant Ordering System"
CURRENCY = "SAR"
SUPPORTED_LANGUAGES = ["English", "Urdu", "Arabic"]

# Categories for the menu
MENU_CATEGORIES = [
    "Fast Food",
    "Pizza", 
    "Meat & BBQ",
    "Tea",
    "Ice Cream"
]

# Payment methods
PAYMENT_METHODS = ["Cash", "Card"]

# =============================================================================
# DATA FILE PATHS
# =============================================================================
import pathlib

BASE_DIR = pathlib.Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

MENU_FILE = DATA_DIR / "menu.json"
ORDERS_FILE = DATA_DIR / "orders.json"
DEALS_FILE = DATA_DIR / "deals.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)
