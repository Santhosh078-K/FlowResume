# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Google Generative AI Configuration ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")

# --- Poppler (for PDF to Image) Configuration ---
# IMPORTANT: Specify the path to your Poppler's bin directory if you are on Windows.
# Example: POPPLER_PATH = r'C:\Users\YourUser\Downloads\poppler-xxxx\bin'
POPPLER_PATH = None # Set to your poppler bin path if on Windows

# --- wkhtmltopdf (for HTML to PDF) Configuration ---
# IMPORTANT: Specify the path to your wkhtmltopdf executable if it's not in your system's PATH.
# Example for Windows: WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
# Example for macOS: WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'
WKHTMLTOPDF_PATH = None # MAKE SURE THIS IS CORRECTLY SET IF wkhtmltopdf IS NOT IN YOUR SYSTEM PATH
# For example, on Windows, it might be:
# WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

# --- Database Configuration ---
DB_FILE = "app_data.json"

# --- Email Configuration ---
SENDER_EMAIL = "sk2050297@gmail.com" # Your sender email address
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD") # Ensure this is set in .env

# --- Admin Panel Configuration ---
ADMIN_PASS = os.getenv("ADMIN_PASS")