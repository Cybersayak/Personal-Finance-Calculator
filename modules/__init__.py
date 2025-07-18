"""
Personal Finance Calculator - Modules Package
This package contains all the core modules for the personal finance calculator.

Modules:
- calculator: Core financial calculations
- budget: Budget planning and tracking
- currency: Currency conversion functionality
- data_handler: Data management and persistence
- utils: Common utility functions
"""

# Version information
__version__ = "1.0.0"
__author__ = "Sayak Ghosh"

# Import all modules for easy access
from . import calculator
from . import budget
from . import currency
from . import data_handler
from . import utils

# Define what gets imported with "from modules import *"
__all__ = [
    'calculator',
    'budget', 
    'currency',
    'data_handler',
    'utils'
]