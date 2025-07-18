"""
Configuration settings for Personal Finance Calculator
Contains all constants, default values, and configuration parameters.
"""

import os
from datetime import datetime

# =============================================
# CURRENCY SETTINGS
# =============================================
DEFAULT_CURRENCY = "USD"
DECIMAL_PRECISION = 2

# Supported currencies with their symbols
SUPPORTED_CURRENCIES = {
    'USD': '$',
    'EUR': '€', 
    'GBP': '£',
    'JPY': '¥',
    'CAD': 'C$',
    'AUD': 'A$',
    'CHF': 'Fr',
    'CNY': '¥',
    'INR': '₹',
    'BRL': 'R$'
}

# Default exchange rates (USD as base)
DEFAULT_EXCHANGE_RATES = {
    'USD': 1.0,
    'EUR': 0.85,
    'GBP': 0.73,
    'JPY': 110.0,
    'CAD': 1.25,
    'AUD': 1.35,
    'CHF': 0.92,
    'CNY': 6.45,
    'INR': 74.5,
    'BRL': 5.2
}

# =============================================
# FILE PATHS
# =============================================
# Data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

# Data files
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.txt')
BUDGETS_FILE = os.path.join(DATA_DIR, 'budgets.txt')
EXCHANGE_RATES_FILE = os.path.join(DATA_DIR, 'exchange_rates.txt')

# Backup directory
BACKUP_DIR = os.path.join(DATA_DIR, 'backups')

# =============================================
# DISPLAY FORMATS
# =============================================
# Date format for displays
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Number formatting
CURRENCY_FORMAT = "{symbol}{amount:,.{precision}f}"
PERCENTAGE_FORMAT = "{value:.1f}%"

# =============================================
# BUDGET CATEGORIES
# =============================================
DEFAULT_BUDGET_CATEGORIES = [
    'Housing',
    'Food & Dining',
    'Transportation', 
    'Healthcare',
    'Entertainment',
    'Shopping',
    'Utilities',
    'Insurance',
    'Savings',
    'Other'
]

# Recommended budget percentages (50/30/20 rule)
RECOMMENDED_BUDGET_PERCENTAGES = {
    'Housing': 25,
    'Food & Dining': 12,
    'Transportation': 10,
    'Healthcare': 5,
    'Entertainment': 10,
    'Shopping': 10,
    'Utilities': 8,
    'Insurance': 5,
    'Savings': 20,
    'Other': 5
}

# =============================================
# VALIDATION LIMITS
# =============================================
MAX_TRANSACTION_AMOUNT = 1000000.0  # Maximum transaction amount
MIN_TRANSACTION_AMOUNT = 0.01       # Minimum transaction amount
MAX_BUDGET_PERCENTAGE = 100         # Maximum total budget percentage
MIN_BUDGET_PERCENTAGE = 0           # Minimum category percentage

# =============================================
# USER INTERFACE SETTINGS
# =============================================
# Menu options
MAIN_MENU_OPTIONS = [
    "Add Income",
    "Add Expense", 
    "View Financial Summary",
    "Create Budget",
    "View Budget Performance",
    "Currency Conversion",
    "Export Data",
    "Settings",
    "Exit"
]

# Display settings
TERMINAL_WIDTH = 80
SEPARATOR_CHAR = "="
HEADER_CHAR = "-"

# Progress bar settings
PROGRESS_BAR_WIDTH = 30
PROGRESS_BAR_FILL = "█"
PROGRESS_BAR_EMPTY = "░"

# =============================================
# ERROR MESSAGES
# =============================================
ERROR_MESSAGES = {
    'INVALID_NUMBER': "Invalid number format. Please enter a valid number.",
    'NEGATIVE_AMOUNT': "Amount cannot be negative. Please enter a positive number.",
    'INVALID_CURRENCY': "Invalid currency code. Supported currencies: {currencies}",
    'FILE_NOT_FOUND': "Data file not found. Starting with empty data.",
    'FILE_WRITE_ERROR': "Error writing to file. Please check permissions.",
    'BUDGET_EXCEEDED': "Budget percentage exceeds 100%. Please adjust.",
    'INVALID_DATE': "Invalid date format. Please use YYYY-MM-DD format.",
    'AMOUNT_TOO_LARGE': f"Amount exceeds maximum limit of {MAX_TRANSACTION_AMOUNT:,.2f}",
    'AMOUNT_TOO_SMALL': f"Amount below minimum limit of {MIN_TRANSACTION_AMOUNT:.2f}"
}

# =============================================
# SUCCESS MESSAGES
# =============================================
SUCCESS_MESSAGES = {
    'TRANSACTION_ADDED': "Transaction added successfully!",
    'BUDGET_CREATED': "Budget created successfully!",
    'DATA_EXPORTED': "Data exported successfully!",
    'SETTINGS_UPDATED': "Settings updated successfully!",
    'DATA_SAVED': "Data saved successfully!"
}

# =============================================
# UTILITY FUNCTIONS
# =============================================
def get_current_date():
    """Get current date in the standard format."""
    return datetime.now().strftime(DATE_FORMAT)

def get_current_datetime():
    """Get current datetime in the standard format."""
    return datetime.now().strftime(DATETIME_FORMAT)

def format_currency(amount, currency=DEFAULT_CURRENCY):
    """Format amount with currency symbol."""
    symbol = SUPPORTED_CURRENCIES.get(currency, '$')
    return CURRENCY_FORMAT.format(
        symbol=symbol,
        amount=amount,
        precision=DECIMAL_PRECISION
    )

def format_percentage(value):
    """Format percentage value."""
    return PERCENTAGE_FORMAT.format(value=value)

def ensure_data_directory():
    """Ensure data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)