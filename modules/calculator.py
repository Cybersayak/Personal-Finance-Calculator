"""
Core calculation functions for personal finance calculator.
"""

"""
Calculator Module 
Handles all core financial calculations including income, expenses, and savings.
This module provides the mathematical foundation for the entire application.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.data_handler import load_transactions, validate_positive_number, validate_currency
from modules.currency import convert_currency, get_exchange_rate
from config.settings import (
    DEFAULT_CURRENCY, DECIMAL_PRECISION, DATE_FORMAT,
    format_currency, format_percentage
)

# =============================================
# TRANSACTION MANAGEMENT
# =============================================

def add_income(amount: float, category: str, date: str = None, 
               currency: str = DEFAULT_CURRENCY, description: str = "") -> Dict[str, Any]:
    """
    Create an income transaction.
    
    Args:
        amount: Income amount
        category: Income category (e.g., 'Salary', 'Freelance')
        date: Transaction date (defaults to today)
        currency: Currency code
        description: Optional description
        
    Returns:
        Dict: Transaction dictionary
        
    Logic:
        1. Validate input parameters
        2. Set default date if not provided
        3. Create transaction dictionary
        4. Return structured transaction data
    """
    # Validate amount
    validated_amount = validate_positive_number(amount)
    if validated_amount is None:
        raise ValueError("Invalid amount. Must be a positive number.")
    
    # Validate currency
    validated_currency = validate_currency(currency)
    if validated_currency is None:
        raise ValueError(f"Invalid currency code: {currency}")
    
    # Set default date if not provided
    if date is None:
        date = datetime.now().strftime(DATE_FORMAT)
    
    # Create transaction dictionary
    transaction = {
        'date': date,
        'type': 'income',
        'amount': round(validated_amount, DECIMAL_PRECISION),
        'category': category.strip(),
        'currency': validated_currency,
        'description': description.strip()
    }
    
    return transaction

def add_expense(amount: float, category: str, date: str = None,
                currency: str = DEFAULT_CURRENCY, description: str = "") -> Dict[str, Any]:
    """
    Create an expense transaction.
    
    Args:
        amount: Expense amount
        category: Expense category (e.g., 'Food', 'Transportation')
        date: Transaction date (defaults to today)
        currency: Currency code
        description: Optional description
        
    Returns:
        Dict: Transaction dictionary
        
    Logic:
        1. Validate input parameters
        2. Set default date if not provided
        3. Create transaction dictionary
        4. Return structured transaction data
    """
    # Validate amount
    validated_amount = validate_positive_number(amount)
    if validated_amount is None:
        raise ValueError("Invalid amount. Must be a positive number.")
    
    # Validate currency
    validated_currency = validate_currency(currency)
    if validated_currency is None:
        raise ValueError(f"Invalid currency code: {currency}")
    
    # Set default date if not provided
    if date is None:
        date = datetime.now().strftime(DATE_FORMAT)
    
    # Create transaction dictionary
    transaction = {
        'date': date,
        'type': 'expense',
        'amount': round(validated_amount, DECIMAL_PRECISION),
        'category': category.strip(),
        'currency': validated_currency,
        'description': description.strip()
    }
    
    return transaction

# =============================================
# CALCULATION FUNCTIONS
# =============================================

def calculate_total_income(transactions: List[Dict[str, Any]], 
                          start_date: str = None, end_date: str = None,
                          target_currency: str = DEFAULT_CURRENCY) -> float:
    """
    Calculate total income from transactions.
    
    Args:
        transactions: List of transaction dictionaries
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        target_currency: Currency to convert all amounts to
        
    Returns:
        float: Total income amount in target currency
        
    Logic:
        1. Filter transactions by date range if specified
        2. Filter for income transactions only
        3. Convert all amounts to target currency
        4. Sum up all income amounts
    """
    total_income = 0.0
    
    for transaction in transactions:
        # Skip if not income
        if transaction['type'] != 'income':
            continue
            
        # Apply date filters if specified
        if start_date and transaction['date'] < start_date:
            continue
        if end_date and transaction['date'] > end_date:
            continue
            
        # Convert amount to target currency
        amount = transaction['amount']
        from_currency = transaction['currency']
        
        if from_currency != target_currency:
            converted_amount = convert_currency(amount, from_currency, target_currency)
            if converted_amount is not None:
                amount = converted_amount
            # If conversion fails, use original amount (should log warning in production)
            
        total_income += amount
    
    return round(total_income, DECIMAL_PRECISION)

def calculate_total_expenses(transactions: List[Dict[str, Any]], 
                           start_date: str = None, end_date: str = None,
                           target_currency: str = DEFAULT_CURRENCY) -> float:
    """
    Calculate total expenses from transactions.
    
    Args:
        transactions: List of transaction dictionaries
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        target_currency: Currency to convert all amounts to
        
    Returns:
        float: Total expenses amount in target currency
        
    Logic:
        1. Filter transactions by date range if specified
        2. Filter for expense transactions only
        3. Convert all amounts to target currency
        4. Sum up all expense amounts
    """
    total_expenses = 0.0
    
    for transaction in transactions:
        # Skip if not expense
        if transaction['type'] != 'expense':
            continue
            
        # Apply date filters if specified
        if start_date and transaction['date'] < start_date:
            continue
        if end_date and transaction['date'] > end_date:
            continue
            
        # Convert amount to target currency
        amount = transaction['amount']
        from_currency = transaction['currency']
        
        if from_currency != target_currency:
            converted_amount = convert_currency(amount, from_currency, target_currency)
            if converted_amount is not None:
                amount = converted_amount
            # If conversion fails, use original amount (should log warning in production)
            
        total_expenses += amount
    
    return round(total_expenses, DECIMAL_PRECISION)

def calculate_savings(transactions: List[Dict[str, Any]], 
                     start_date: str = None, end_date: str = None,
                     target_currency: str = DEFAULT_CURRENCY) -> float:
    """
    Calculate savings (income - expenses).
    
    Args:
        transactions: List of transaction dictionaries
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        target_currency: Currency to convert all amounts to
        
    Returns:
        float: Savings amount (positive = surplus, negative = deficit)
        
    Logic:
        1. Calculate total income for the period
        2. Calculate total expenses for the period
        3. Return the difference (income - expenses)
    """
    total_income = calculate_total_income(transactions, start_date, end_date, target_currency)
    total_expenses = calculate_total_expenses(transactions, start_date, end_date, target_currency)
    
    savings = total_income - total_expenses
    return round(savings, DECIMAL_PRECISION)

def calculate_savings_rate(transactions: List[Dict[str, Any]], 
                          start_date: str = None, end_date: str = None,
                          target_currency: str = DEFAULT_CURRENCY) -> float:
    """
    Calculate savings rate as a percentage of income.
    
    Args:
        transactions: List of transaction dictionaries
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        target_currency: Currency to convert all amounts to
        
    Returns:
        float: Savings rate as percentage (0-100)
        
    Logic:
        1. Calculate total income
        2. Calculate savings amount
        3. Return (savings / income) * 100
        4. Handle zero income case
    """
    total_income = calculate_total_income(transactions, start_date, end_date, target_currency)
    
    if total_income == 0:
        return 0.0
    
    savings = calculate_savings(transactions, start_date, end_date, target_currency)
    savings_rate = (savings / total_income) * 100
    
    return round(savings_rate, 1)

# =============================================
# ANALYSIS FUNCTIONS
# =============================================

def get_expense_breakdown(transactions: List[Dict[str, Any]], 
                         start_date: str = None, end_date: str = None,
                         target_currency: str = DEFAULT_CURRENCY) -> Dict[str, float]:
    """
    Get breakdown of expenses by category.
    
    Args:
        transactions: List of transaction dictionaries
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        target_currency: Currency to convert all amounts to
        
    Returns:
        Dict: Category names mapped to total amounts
        
    Logic:
        1. Filter expense transactions by date range
        2. Group by category
        3. Sum amounts for each category
        4. Convert to target currency
    """
    category_totals = defaultdict(float)
    
    for transaction in transactions:
        # Skip if not expense
        if transaction['type'] != 'expense':
            continue
            
        # Apply date filters if specified
        if start_date and transaction['date'] < start_date:
            continue
        if end_date and transaction['date'] > end_date:
            continue
            
        # Convert amount to target currency
        amount = transaction['amount']
        from_currency = transaction['currency']
        
        if from_currency != target_currency:
            converted_amount = convert_currency(amount, from_currency, target_currency)
            if converted_amount is not None:
                amount = converted_amount
        
        category_totals[transaction['category']] += amount
    
    # Round all values
    return {category: round(amount, DECIMAL_PRECISION) 
            for category, amount in category_totals.items()}

def get_income_breakdown(transactions: List[Dict[str, Any]], 
                        start_date: str = None, end_date: str = None,
                        target_currency: str = DEFAULT_CURRENCY) -> Dict[str, float]:
    """
    Get breakdown of income by category.
    
    Args:
        transactions: List of transaction dictionaries
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        target_currency: Currency to convert all amounts to
        
    Returns:
        Dict: Category names mapped to total amounts
    """
    category_totals = defaultdict(float)
    
    for transaction in transactions:
        # Skip if not income
        if transaction['type'] != 'income':
            continue
            
        # Apply date filters if specified
        if start_date and transaction['date'] < start_date:
            continue
        if end_date and transaction['date'] > end_date:
            continue
            
        # Convert amount to target currency
        amount = transaction['amount']
        from_currency = transaction['currency']
        
        if from_currency != target_currency:
            converted_amount = convert_currency(amount, from_currency, target_currency)
            if converted_amount is not None:
                amount = converted_amount
        
        category_totals[transaction['category']] += amount
    
    # Round all values
    return {category: round(amount, DECIMAL_PRECISION) 
            for category, amount in category_totals.items()}

def get_monthly_summary(transactions: List[Dict[str, Any]], 
                       target_currency: str = DEFAULT_CURRENCY) -> Dict[str, Dict[str, float]]:
    """
    Get monthly financial summary.
    
    Args:
        transactions: List of transaction dictionaries
        target_currency: Currency to convert all amounts to
        
    Returns:
        Dict: Monthly summaries with income, expenses, and savings
        
    Logic:
        1. Group transactions by month
        2. Calculate totals for each month
        3. Return structured monthly data
    """
    monthly_data = defaultdict(lambda: {'income': 0.0, 'expenses': 0.0, 'savings': 0.0})
    
    for transaction in transactions:
        # Extract year-month from date
        date_obj = datetime.strptime(transaction['date'], DATE_FORMAT)
        month_key = date_obj.strftime('%Y-%m')
        
        # Convert amount to target currency
        amount = transaction['amount']
        from_currency = transaction['currency']
        
        if from_currency != target_currency:
            converted_amount = convert_currency(amount, from_currency, target_currency)
            if converted_amount is not None:
                amount = converted_amount
        
        # Add to appropriate category
        if transaction['type'] == 'income':
            monthly_data[month_key]['income'] += amount
        elif transaction['type'] == 'expense':
            monthly_data[month_key]['expenses'] += amount
    
    # Calculate savings for each month
    for month_key in monthly_data:
        monthly_data[month_key]['savings'] = (
            monthly_data[month_key]['income'] - monthly_data[month_key]['expenses']
        )
        
        # Round all values
        for key in monthly_data[month_key]:
            monthly_data[month_key][key] = round(monthly_data[month_key][key], DECIMAL_PRECISION)
    
    return dict(monthly_data)

def get_financial_summary(transactions: List[Dict[str, Any]], 
                         target_currency: str = DEFAULT_CURRENCY) -> Dict[str, Any]:
    """
    Generate comprehensive financial summary.
    
    Args:
        transactions: List of transaction dictionaries
        target_currency: Currency to convert all amounts to
        
    Returns:
        Dict: Complete financial summary
        
    Logic:
        1. Calculate all key metrics
        2. Get category breakdowns
        3. Compile into comprehensive summary
    """
    # Calculate totals
    total_income = calculate_total_income(transactions, target_currency=target_currency)
    total_expenses = calculate_total_expenses(transactions, target_currency=target_currency)
    savings = calculate_savings(transactions, target_currency=target_currency)
    savings_rate = calculate_savings_rate(transactions, target_currency=target_currency)
    
    # Get breakdowns
    expense_breakdown = get_expense_breakdown(transactions, target_currency=target_currency)
    income_breakdown = get_income_breakdown(transactions, target_currency=target_currency)
    monthly_summary = get_monthly_summary(transactions, target_currency=target_currency)
    
    # Compile summary
    summary = {
        'currency': target_currency,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'savings': savings,
        'savings_rate': savings_rate,
        'expense_breakdown': expense_breakdown,
        'income_breakdown': income_breakdown,
        'monthly_summary': monthly_summary,
        'transaction_count': len(transactions),
        'date_range': _get_date_range(transactions)
    }
    
    return summary

# =============================================
# UTILITY FUNCTIONS
# =============================================

def _get_date_range(transactions: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Get the date range of transactions.
    
    Args:
        transactions: List of transaction dictionaries
        
    Returns:
        Dict: Start and end dates
    """
    if not transactions:
        return {'start': None, 'end': None}
    
    dates = [transaction['date'] for transaction in transactions]
    return {
        'start': min(dates),
        'end': max(dates)
    }

def get_transactions_by_period(transactions: List[Dict[str, Any]], 
                              period: str = 'month') -> List[Dict[str, Any]]:
    """
    Filter transactions by time period.
    
    Args:
        transactions: List of transaction dictionaries
        period: Time period ('week', 'month', 'quarter', 'year')
        
    Returns:
        List: Filtered transactions
        
    Logic:
        1. Calculate start date based on period
        2. Filter transactions from start date to now
        3. Return filtered list
    """
    today = datetime.now()
    
    if period == 'week':
        start_date = today - timedelta(days=7)
    elif period == 'month':
        start_date = today - timedelta(days=30)
    elif period == 'quarter':
        start_date = today - timedelta(days=90)
    elif period == 'year':
        start_date = today - timedelta(days=365)
    else:
        return transactions  # Return all if invalid period
    
    start_date_str = start_date.strftime(DATE_FORMAT)
    
    filtered_transactions = []
    for transaction in transactions:
        if transaction['date'] >= start_date_str:
            filtered_transactions.append(transaction)
    
    return filtered_transactions

def format_financial_summary(summary: Dict[str, Any]) -> str:
    """
    Format financial summary for display.
    
    Args:
        summary: Financial summary dictionary
        
    Returns:
        str: Formatted summary string
    """
    currency = summary['currency']
    
    output = []
    output.append("=" * 50)
    output.append("FINANCIAL SUMMARY")
    output.append("=" * 50)
    output.append(f"Currency: {currency}")
    output.append(f"Total Income: {format_currency(summary['total_income'], currency)}")
    output.append(f"Total Expenses: {format_currency(summary['total_expenses'], currency)}")
    output.append(f"Savings: {format_currency(summary['savings'], currency)}")
    output.append(f"Savings Rate: {format_percentage(summary['savings_rate'])}")
    output.append(f"Transactions: {summary['transaction_count']}")
    
    if summary['date_range']['start'] and summary['date_range']['end']:
        output.append(f"Date Range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    
    output.append("\n" + "-" * 30)
    output.append("EXPENSE BREAKDOWN")
    output.append("-" * 30)
    
    for category, amount in summary['expense_breakdown'].items():
        output.append(f"{category}: {format_currency(amount, currency)}")
    
    return "\n".join(output)