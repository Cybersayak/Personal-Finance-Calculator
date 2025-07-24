"""
Budget Module - Personal Finance Calculator
Handles budget creation, tracking, and performance analysis.
This module provides comprehensive budget management functionality.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.calculator import (
    calculate_total_expenses, get_expense_breakdown,
    get_transactions_by_period
)
from modules.currency import convert_currency, normalize_to_base_currency
from modules.data_handler import (
    validate_positive_number, save_budget, load_budget
)
from config.settings import (
    DEFAULT_BUDGET_CATEGORIES, RECOMMENDED_BUDGET_PERCENTAGES,
    DEFAULT_CURRENCY, DECIMAL_PRECISION, MAX_BUDGET_PERCENTAGE,
    format_currency, format_percentage, get_current_date,
    PROGRESS_BAR_WIDTH, PROGRESS_BAR_FILL, PROGRESS_BAR_EMPTY
)

# =============================================
# BUDGET CREATION
# =============================================

class Budget:
    """
    Budget class to manage budget data and operations.
    
    This class encapsulates all budget-related functionality including
    creation, modification, and tracking.
    """
    
    def __init__(self, monthly_income: float, currency: str = DEFAULT_CURRENCY):
        """
        Initialize a new budget.
        
        Args:
            monthly_income: Total monthly income
            currency: Budget currency
        """
        self.monthly_income = round(monthly_income, DECIMAL_PRECISION)
        self.currency = currency
        self.categories = {}
        self.created_date = get_current_date()
        self.last_updated = get_current_date()
        
    def add_category(self, category: str, amount: float) -> bool:
        """
        Add or update a budget category.
        
        Args:
            category: Category name
            amount: Budget amount for this category
            
        Returns:
            bool: True if successful, False otherwise
            
        Logic:
            1. Validate category name and amount
            2. Check if total budget doesn't exceed income
            3. Add/update category
            4. Update last modified date
        """
        # Validate inputs
        if not category or not category.strip():
            return False
            
        validated_amount = validate_positive_number(amount)
        if validated_amount is None:
            return False
        
        # Store current amount for rollback
        old_amount = self.categories.get(category, 0.0)
        
        # Temporarily set new amount
        self.categories[category] = validated_amount
        
        # Check if total budget exceeds income
        if self.get_total_budget() > self.monthly_income:
            # Rollback if exceeds income
            if old_amount > 0:
                self.categories[category] = old_amount
            else:
                del self.categories[category]
            return False
        
        # Update timestamp
        self.last_updated = get_current_date()
        return True
    
    def remove_category(self, category: str) -> bool:
        """
        Remove a budget category.
        
        Args:
            category: Category name to remove
            
        Returns:
            bool: True if successful, False if category not found
        """
        if category in self.categories:
            del self.categories[category]
            self.last_updated = get_current_date()
            return True
        return False
    
    def get_category_amount(self, category: str) -> float:
        """Get budget amount for a specific category."""
        return self.categories.get(category, 0.0)
    
    def get_category_percentage(self, category: str) -> float:
        """Get budget percentage for a specific category."""
        if self.monthly_income == 0:
            return 0.0
        
        amount = self.get_category_amount(category)
        return round((amount / self.monthly_income) * 100, 1)
    
    def get_total_budget(self) -> float:
        """Get total budgeted amount across all categories."""
        return round(sum(self.categories.values()), DECIMAL_PRECISION)
    
    def get_remaining_budget(self) -> float:
        """Get remaining unallocated budget."""
        return round(self.monthly_income - self.get_total_budget(), DECIMAL_PRECISION)
    
    def get_budget_utilization(self) -> float:
        """Get budget utilization as percentage."""
        if self.monthly_income == 0:
            return 0.0
        return round((self.get_total_budget() / self.monthly_income) * 100, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert budget to dictionary for storage."""
        return {
            'monthly_income': self.monthly_income,
            'currency': self.currency,
            'categories': self.categories.copy(),
            'created_date': self.created_date,
            'last_updated': self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Budget':
        """Create budget from dictionary."""
        budget = cls(data['monthly_income'], data.get('currency', DEFAULT_CURRENCY))
        budget.categories = data.get('categories', {})
        budget.created_date = data.get('created_date', get_current_date())
        budget.last_updated = data.get('last_updated', get_current_date())
        return budget

def create_budget(monthly_income: float, currency: str = DEFAULT_CURRENCY) -> Budget:
    """
    Create a new budget with the given monthly income.
    
    Args:
        monthly_income: Total monthly income
        currency: Budget currency
        
    Returns:
        Budget: New budget instance
        
    Logic:
        1. Validate monthly income
        2. Create budget instance
        3. Return for further configuration
    """
    validated_income = validate_positive_number(monthly_income)
    if validated_income is None:
        raise ValueError("Invalid monthly income. Must be a positive number.")
    
    return Budget(validated_income, currency)

def create_budget_from_template(monthly_income: float, 
                               template: str = "50/30/20",
                               currency: str = DEFAULT_CURRENCY) -> Budget:
    """
    Create budget using a predefined template.
    
    Args:
        monthly_income: Total monthly income
        template: Budget template name
        currency: Budget currency
        
    Returns:
        Budget: Budget with template allocations
        
    Logic:
        1. Create base budget
        2. Apply template percentages
        3. Distribute amounts across categories
    """
    budget = create_budget(monthly_income, currency)
    
    if template == "50/30/20":
        # 50% needs, 30% wants, 20% savings
        needs_amount = monthly_income * 0.5
        wants_amount = monthly_income * 0.3
        savings_amount = monthly_income * 0.2
        
        # Distribute needs (50%)
        budget.add_category("Housing", needs_amount * 0.5)  # 25% of total
        budget.add_category("Food & Dining", needs_amount * 0.24)  # 12% of total
        budget.add_category("Transportation", needs_amount * 0.2)  # 10% of total
        budget.add_category("Utilities", needs_amount * 0.16)  # 8% of total
        budget.add_category("Healthcare", needs_amount * 0.1)  # 5% of total
        
        # Distribute wants (30%)
        budget.add_category("Entertainment", wants_amount * 0.33)  # 10% of total
        budget.add_category("Shopping", wants_amount * 0.33)  # 10% of total
        budget.add_category("Other", wants_amount * 0.33)  # 10% of total
        
        # Savings (20%)
        budget.add_category("Savings", savings_amount)  # 20% of total
        
    elif template == "zero_based":
        # Start with recommended percentages
        for category, percentage in RECOMMENDED_BUDGET_PERCENTAGES.items():
            amount = (monthly_income * percentage) / 100
            budget.add_category(category, amount)
    
    return budget

# =============================================
# BUDGET TRACKING
# =============================================

def track_spending_vs_budget(budget: Budget, transactions: List[Dict[str, Any]], 
                            period: str = 'month') -> Dict[str, Dict[str, float]]:
    """
    Track actual spending against budget.
    
    Args:
        budget: Budget instance to track against
        transactions: List of transactions
        period: Time period to analyze ('week', 'month', 'quarter', 'year')
        
    Returns:
        Dict: Spending vs budget analysis for each category
        
    Logic:
        1. Filter transactions for the specified period
        2. Get expense breakdown by category
        3. Compare against budget allocations
        4. Calculate variances and percentages
    """
    # Filter transactions for the period
    period_transactions = get_transactions_by_period(transactions, period)
    
    # Normalize currencies if needed
    if budget.currency != DEFAULT_CURRENCY:
        period_transactions = normalize_to_base_currency(period_transactions, budget.currency)
    
    # Get actual spending by category
    actual_spending = get_expense_breakdown(period_transactions, target_currency=budget.currency)
    
    # Build comparison
    comparison = {}
    total_budgeted = 0.0
    total_spent = 0.0
    
    # Process each budget category
    for category, budgeted_amount in budget.categories.items():
        actual_amount = actual_spending.get(category, 0.0)
        variance = actual_amount - budgeted_amount
        
        if budgeted_amount > 0:
            percentage_used = (actual_amount / budgeted_amount) * 100
        else:
            percentage_used = 0.0 if actual_amount == 0 else float('inf')
        
        comparison[category] = {
            'budgeted': round(budgeted_amount, DECIMAL_PRECISION),
            'actual': round(actual_amount, DECIMAL_PRECISION),
            'variance': round(variance, DECIMAL_PRECISION),
            'percentage_used': round(percentage_used, 1),
            'status': 'over' if variance > 0 else 'under' if variance < 0 else 'exact'
        }
        
        total_budgeted += budgeted_amount
        total_spent += actual_amount
    
    # Add categories with spending but no budget
    for category, amount in actual_spending.items():
        if category not in budget.categories:
            comparison[category] = {
                'budgeted': 0.0,
                'actual': round(amount, DECIMAL_PRECISION),
                'variance': round(amount, DECIMAL_PRECISION),
                'percentage_used': float('inf'),
                'status': 'unbudgeted'
            }
            total_spent += amount
    
    # Add summary
    comparison['_summary'] = {
        'total_budgeted': round(total_budgeted, DECIMAL_PRECISION),
        'total_spent': round(total_spent, DECIMAL_PRECISION),
        'total_variance': round(total_spent - total_budgeted, DECIMAL_PRECISION),
        'budget_utilization': round((total_spent / total_budgeted * 100), 1) if total_budgeted > 0 else 0.0
    }
    
    return comparison

def calculate_budget_variance(budget: Budget, transactions: List[Dict[str, Any]], 
                            category: str = None) -> Dict[str, float]:
    """
    Calculate budget variance for specific category or overall.
    
    Args:
        budget: Budget instance
        transactions: List of transactions
        category: Specific category (None for overall)
        
    Returns:
        Dict: Variance analysis
    """
    spending_comparison = track_spending_vs_budget(budget, transactions)
    
    if category:
        if category in spending_comparison:
            return {
                'category': category,
                'variance': spending_comparison[category]['variance'],
                'percentage_variance': spending_comparison[category]['percentage_used'] - 100,
                'status': spending_comparison[category]['status']
            }
        else:
            return {
                'category': category,
                'variance': 0.0,
                'percentage_variance': -100.0,
                'status': 'no_spending'
            }
    else:
        summary = spending_comparison['_summary']
        return {
            'total_variance': summary['total_variance'],
            'budget_utilization': summary['budget_utilization'],
            'over_budget': summary['total_variance'] > 0
        }

def get_budget_status(budget: Budget, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Get comprehensive budget status.
    
    Args:
        budget: Budget instance
        transactions: List of transactions
        
    Returns:
        Dict: Complete budget status information
    """
    spending_comparison = track_spending_vs_budget(budget, transactions)
    summary = spending_comparison['_summary']
    
    # Categorize spending status
    over_budget_categories = []
    under_budget_categories = []
    unbudgeted_categories = []
    
    for category, data in spending_comparison.items():
        if category == '_summary':
            continue
            
        if data['status'] == 'over':
            over_budget_categories.append({
                'category': category,
                'variance': data['variance'],
                'percentage_over': data['percentage_used'] - 100
            })
        elif data['status'] == 'under':
            under_budget_categories.append({
                'category': category,
                'remaining': -data['variance'],
                'percentage_used': data['percentage_used']
            })
        elif data['status'] == 'unbudgeted':
            unbudgeted_categories.append({
                'category': category,
                'amount': data['actual']
            })
    
    return {
        'budget_health': 'healthy' if summary['total_variance'] <= 0 else 'over_budget',
        'total_budgeted': summary['total_budgeted'],
        'total_spent': summary['total_spent'],
        'remaining_budget': budget.get_remaining_budget(),
        'budget_utilization': summary['budget_utilization'],
        'over_budget_categories': over_budget_categories,
        'under_budget_categories': under_budget_categories,
        'unbudgeted_categories': unbudgeted_categories,
        'categories_count': len(budget.categories),
        'currency': budget.currency
    }

# =============================================
# BUDGET PERFORMANCE & REPORTING
# =============================================

def generate_budget_performance_report(budget: Budget, 
                                     transactions: List[Dict[str, Any]]) -> str:
    """
    Generate a formatted budget performance report.
    
    Args:
        budget: Budget instance
        transactions: List of transactions
        
    Returns:
        str: Formatted report
    """
    spending_comparison = track_spending_vs_budget(budget, transactions)
    status = get_budget_status(budget, transactions)
    
    output = []
    
    # Header
    output.append("=" * 60)
    output.append("BUDGET PERFORMANCE REPORT")
    output.append("=" * 60)
    output.append(f"Budget Period: Monthly")
    output.append(f"Currency: {budget.currency}")
    output.append(f"Report Date: {get_current_date()}")
    output.append("")
    
    # Overall Summary
    output.append("OVERALL SUMMARY")
    output.append("-" * 30)
    output.append(f"Monthly Income:    {format_currency(budget.monthly_income, budget.currency)}")
    output.append(f"Total Budgeted:    {format_currency(status['total_budgeted'], budget.currency)}")
    output.append(f"Total Spent:       {format_currency(status['total_spent'], budget.currency)}")
    output.append(f"Budget Utilization: {format_percentage(status['budget_utilization'])}")
    output.append(f"Budget Health:     {status['budget_health'].upper()}")
    output.append("")
    
    # Category Breakdown
    output.append("CATEGORY BREAKDOWN")
    output.append("-" * 60)
    output.append(f"{'Category':<20} {'Budgeted':<12} {'Actual':<12} {'Variance':<12} {'Usage':<8}")
    output.append("-" * 60)
    
    for category, data in spending_comparison.items():
        if category == '_summary':
            continue
            
        # Create progress bar
        if data['budgeted'] > 0:
            usage_ratio = min(data['actual'] / data['budgeted'], 1.0)
        else:
            usage_ratio = 1.0 if data['actual'] > 0 else 0.0
            
        progress_bar = create_progress_bar(usage_ratio, PROGRESS_BAR_WIDTH)
        
        # Format variance with color indication
        variance_str = f"{data['variance']:+.2f}"
        if data['variance'] > 0:
            variance_str = f"+{data['variance']:.2f} ⚠️"
        elif data['variance'] < 0:
            variance_str = f"{data['variance']:.2f} ✓"
        
        output.append(f"{category:<20} "
                     f"{data['budgeted']:>8.2f} "
                     f"{data['actual']:>8.2f} "
                     f"{variance_str:>12} "
                     f"{data['percentage_used']:>5.1f}%")
        output.append(f"{'':<20} {progress_bar}")
        output.append("")
    
    # Alerts and Recommendations
    if status['over_budget_categories']:
        output.append("⚠️  OVER-BUDGET CATEGORIES")
        output.append("-" * 30)
        for item in status['over_budget_categories']:
            output.append(f"• {item['category']}: "
                         f"{format_currency(item['variance'], budget.currency)} over budget "
                         f"({item['percentage_over']:+.1f}%)")
        output.append("")
    
    if status['unbudgeted_categories']:
        output.append("📝 UNBUDGETED SPENDING")
        output.append("-" * 30)
        for item in status['unbudgeted_categories']:
            output.append(f"• {item['category']}: "
                         f"{format_currency(item['amount'], budget.currency)}")
        output.append("")
    
    # Recommendations
    output.append("💡 RECOMMENDATIONS")
    output.append("-" * 30)
    
    if status['budget_health'] == 'over_budget':
        output.append("• Review over-budget categories and reduce spending")
        output.append("• Consider adjusting budget allocations")
        
    if status['unbudgeted_categories']:
        output.append("• Add budget categories for untracked spending")
        
    if status['remaining_budget'] > 0:
        output.append(f"• You have {format_currency(status['remaining_budget'], budget.currency)} "
                     f"unallocated in your budget")
    
    return "\n".join(output)

def create_progress_bar(ratio: float, width: int = PROGRESS_BAR_WIDTH) -> str:
    """
    Create a text-based progress bar.
    
    Args:
        ratio: Progress ratio (0.0 to 1.0)
        width: Width of progress bar
        
    Returns:
        str: Progress bar string
    """
    filled_width = int(ratio * width)
    bar = PROGRESS_BAR_FILL * filled_width + PROGRESS_BAR_EMPTY * (width - filled_width)
    return f"[{bar}] {ratio*100:.1f}%"

# =============================================
# BUDGET MANAGEMENT
# =============================================

def save_budget_to_file(budget: Budget) -> bool:
    """
    Save budget to file.
    
    Args:
        budget: Budget instance to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        budget_data = budget.to_dict()
        return save_budget(budget_data)
    except Exception as e:
        print(f"Error saving budget: {e}")
        return False

def load_budget_from_file() -> Optional[Budget]:
    """
    Load budget from file.
    
    Returns:
        Budget: Loaded budget instance or None if not found
    """
    try:
        budget_data = load_budget()
        if budget_data:
            return Budget.from_dict(budget_data)
        return None
    except Exception as e:
        print(f"Error loading budget: {e}")
        return None

def update_budget_income(budget: Budget, new_income: float) -> bool:
    """
    Update budget income and adjust categories proportionally.
    
    Args:
        budget: Budget instance to update
        new_income: New monthly income
        
    Returns:
        bool: True if successful, False otherwise
        
    Logic:
        1. Validate new income
        2. Calculate scaling factor
        3. Scale all categories proportionally
        4. Update income
    """
    validated_income = validate_positive_number(new_income)
    if validated_income is None:
        return False
    
    if budget.monthly_income == 0:
        budget.monthly_income = validated_income
        return True
    
    # Calculate scaling factor
    scale_factor = validated_income / budget.monthly_income
    
    # Scale all categories
    for category in budget.categories:
        old_amount = budget.categories[category]
        new_amount = old_amount * scale_factor
        budget.categories[category] = round(new_amount, DECIMAL_PRECISION)
    
    # Update income
    budget.monthly_income = validated_income
    budget.last_updated = get_current_date()
    
    return True

def suggest_budget_adjustments(budget: Budget, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Suggest budget adjustments based on spending patterns.
    
    Args:
        budget: Current budget
        transactions: Transaction history
        
    Returns:
        List: List of suggested adjustments
        
    Logic:
        1. Analyze spending patterns vs budget
        2. Identify consistently over/under budget categories
        3. Suggest realistic adjustments
        4. Consider income constraints
    """
    suggestions = []
    spending_comparison = track_spending_vs_budget(budget, transactions)
    
    # Analyze each category
    for category, data in spending_comparison.items():
        if category == '_summary':
            continue
        
        budgeted = data['budgeted']
        actual = data['actual']
        variance = data['variance']
        
        # Suggest increases for consistently over-budget categories
        if data['status'] == 'over' and variance > budgeted * 0.1:  # More than 10% over
            suggested_increase = variance * 1.2  # Add 20% buffer
            suggestions.append({
                'category': category,
                'type': 'increase',
                'current_amount': budgeted,
                'suggested_amount': round(budgeted + suggested_increase, DECIMAL_PRECISION),
                'reason': f'Consistently over budget by {format_currency(variance, budget.currency)}',
                'priority': 'high' if variance > budgeted * 0.25 else 'medium'
            })
        
        # Suggest decreases for significantly under-budget categories
        elif data['status'] == 'under' and abs(variance) > budgeted * 0.3:  # More than 30% under
            suggested_decrease = abs(variance) * 0.5  # Reduce by half the unused amount
            new_amount = max(budgeted - suggested_decrease, actual * 1.1)  # Keep 10% buffer above actual
            suggestions.append({
                'category': category,
                'type': 'decrease',
                'current_amount': budgeted,
                'suggested_amount': round(new_amount, DECIMAL_PRECISION),
                'reason': f'Consistently under budget by {format_currency(abs(variance), budget.currency)}',
                'priority': 'low'
            })
        
        # Suggest adding budget for unbudgeted spending
        elif data['status'] == 'unbudgeted' and actual > 0:
            suggested_amount = actual * 1.2  # Add 20% buffer
            suggestions.append({
                'category': category,
                'type': 'add',
                'current_amount': 0.0,
                'suggested_amount': round(suggested_amount, DECIMAL_PRECISION),
                'reason': f'Unbudgeted spending of {format_currency(actual, budget.currency)}',
                'priority': 'medium'
            })
    
    # Sort by priority
    priority_order = {'high': 3, 'medium': 2, 'low': 1}
    suggestions.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
    
    return suggestions

# =============================================
# INTERACTIVE BUDGET INTERFACE
# =============================================

def interactive_budget_creation():
    """
    Interactive budget creation interface.
    
    This function guides users through creating a comprehensive budget
    with category-by-category input and validation.
    """
    print("\n" + "=" * 50)
    print("BUDGET CREATION WIZARD")
    print("=" * 50)
    
    try:
        # Get monthly income
        while True:
            income_input = input("Enter your monthly income: ").strip()
            income = validate_positive_number(income_input)
            if income is not None:
                break
            print("Invalid income. Please enter a positive number.")
        
        # Get currency
        currency = input(f"Currency ({DEFAULT_CURRENCY}): ").strip().upper()
        if not currency:
            currency = DEFAULT_CURRENCY
        
        # Create budget
        budget = create_budget(income, currency)
        
        print(f"\nCreating budget with {format_currency(income, currency)} monthly income")
        print("\nChoose budget creation method:")
        print("1. Use 50/30/20 template (recommended)")
        print("2. Use zero-based template")
        print("3. Create custom budget")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            budget = create_budget_from_template(income, "50/30/20", currency)
            print("✓ Applied 50/30/20 budget template")
        elif choice == "2":
            budget = create_budget_from_template(income, "zero_based", currency)
            print("✓ Applied zero-based budget template")
        elif choice == "3":
            print("\nCustom Budget Creation")
            print("Enter budget amounts for each category (0 to skip):")
            
            for category in DEFAULT_BUDGET_CATEGORIES:
                while True:
                    amount_input = input(f"{category}: ").strip()
                    if not amount_input or amount_input == "0":
                        break
                    
                    amount = validate_positive_number(amount_input)
                    if amount is not None:
                        if budget.add_category(category, amount):
                            remaining = budget.get_remaining_budget()
                            print(f"  Added. Remaining budget: {format_currency(remaining, currency)}")
                            break
                        else:
                            print("  Amount exceeds remaining budget. Try a smaller amount.")
                    else:
                        print("  Invalid amount. Please enter a positive number.")
        
        # Show budget summary
        print("\n" + "-" * 40)
        print("BUDGET SUMMARY")
        print("-" * 40)
        print(f"Monthly Income: {format_currency(budget.monthly_income, currency)}")
        print(f"Total Budgeted: {format_currency(budget.get_total_budget(), currency)}")
        print(f"Remaining:      {format_currency(budget.get_remaining_budget(), currency)}")
        print(f"Utilization:    {format_percentage(budget.get_budget_utilization())}")
        
        print("\nCategory Breakdown:")
        for category, amount in budget.categories.items():
            percentage = budget.get_category_percentage(category)
            print(f"  {category:<20} {format_currency(amount, currency):>12} ({format_percentage(percentage)})")
        
        # Ask to save
        save_choice = input("\nSave this budget? (y/n): ").strip().lower()
        if save_choice == 'y':
            if save_budget_to_file(budget):
                print("✓ Budget saved successfully!")
            else:
                print("✗ Failed to save budget.")
        
        return budget
        
    except KeyboardInterrupt:
        print("\nBudget creation cancelled.")
        return None
    except Exception as e:
        print(f"Error creating budget: {e}")
        return None

def interactive_budget_tracking(budget: Budget, transactions: List[Dict[str, Any]]):
    """
    Interactive budget tracking interface.
    
    Args:
        budget: Budget to track against
        transactions: List of transactions
    """
    print("\n" + "=" * 50)
    print("BUDGET TRACKING")
    print("=" * 50)
    
    while True:
        print("\nBudget Tracking Options:")
        print("1. View budget performance report")
        print("2. Compare spending vs budget")
        print("3. Get budget adjustment suggestions")
        print("4. Update budget categories")
        print("5. Export budget report")
        print("6. Back to main menu")
        
        choice = input("\nEnter choice (1-6): ").strip()
        
        if choice == "1":
            report = generate_budget_performance_report(budget, transactions)
            print("\n" + report)
            
        elif choice == "2":
            comparison = track_spending_vs_budget(budget, transactions)
            _display_spending_comparison(comparison, budget.currency)
            
        elif choice == "3":
            suggestions = suggest_budget_adjustments(budget, transactions)
            _display_budget_suggestions(suggestions, budget.currency)
            
        elif choice == "4":
            _interactive_budget_update(budget)
            
        elif choice == "5":
            _export_budget_report(budget, transactions)
            
        elif choice == "6":
            break
            
        else:
            print("Invalid choice. Please try again.")

def _display_spending_comparison(comparison: Dict[str, Dict[str, float]], currency: str):
    """Display spending vs budget comparison."""
    print("\n" + "=" * 60)
    print("SPENDING VS BUDGET COMPARISON")
    print("=" * 60)
    
    print(f"{'Category':<20} {'Budgeted':<12} {'Actual':<12} {'Variance':<12} {'Status'}")
    print("-" * 60)
    
    for category, data in comparison.items():
        if category == '_summary':
            continue
        
        status_emoji = {
            'over': '🔴',
            'under': '🟢', 
            'exact': '🟡',
            'unbudgeted': '⚪'
        }.get(data['status'], '')
        
        print(f"{category:<20} "
              f"{format_currency(data['budgeted'], currency):>12} "
              f"{format_currency(data['actual'], currency):>12} "
              f"{data['variance']:>+8.2f} "
              f"{status_emoji} {data['status']}")
    
    # Summary
    summary = comparison['_summary']
    print("-" * 60)
    print(f"{'TOTAL':<20} "
          f"{format_currency(summary['total_budgeted'], currency):>12} "
          f"{format_currency(summary['total_spent'], currency):>12} "
          f"{summary['total_variance']:>+8.2f}")
    print(f"Budget Utilization: {format_percentage(summary['budget_utilization'])}")

def _display_budget_suggestions(suggestions: List[Dict[str, Any]], currency: str):
    """Display budget adjustment suggestions."""
    if not suggestions:
        print("\n✓ No budget adjustments needed. Your budget looks good!")
        return
    
    print("\n" + "=" * 60)
    print("BUDGET ADJUSTMENT SUGGESTIONS")  
    print("=" * 60)
    
    for suggestion in suggestions:
        priority_emoji = {
            'high': '🔥',
            'medium': '⚠️',
            'low': '💡'
        }.get(suggestion['priority'], '')
        
        print(f"\n{priority_emoji} {suggestion['category']} ({suggestion['priority'].upper()} PRIORITY)")
        print(f"   Action: {suggestion['type'].upper()}")
        print(f"   Current: {format_currency(suggestion['current_amount'], currency)}")
        print(f"   Suggested: {format_currency(suggestion['suggested_amount'], currency)}")
        print(f"   Reason: {suggestion['reason']}")

def _interactive_budget_update(budget: Budget):
    """Interactive budget update interface."""
    print("\n" + "=" * 40)
    print("UPDATE BUDGET")
    print("=" * 40)
    
    print("Current Categories:")
    for i, (category, amount) in enumerate(budget.categories.items(), 1):
        percentage = budget.get_category_percentage(category)
        print(f"{i:2d}. {category:<20} {format_currency(amount, budget.currency):>12} ({format_percentage(percentage)})")
    
    print(f"\nRemaining Budget: {format_currency(budget.get_remaining_budget(), budget.currency)}")
    
    while True:
        print("\nUpdate Options:")
        print("1. Add new category")
        print("2. Update existing category")
        print("3. Remove category")
        print("4. Update monthly income")
        print("5. Done")
        
        choice = input("Enter choice (1-5): ").strip()
        
        if choice == "1":
            category = input("Category name: ").strip()
            if category:
                amount_input = input("Amount: ").strip()
                amount = validate_positive_number(amount_input)
                if amount is not None:
                    if budget.add_category(category, amount):
                        print(f"✓ Added {category}")
                    else:
                        print("✗ Failed to add category (exceeds remaining budget)")
                else:
                    print("✗ Invalid amount")
        
        elif choice == "2":
            category = input("Category to update: ").strip()
            if category in budget.categories:
                current = budget.get_category_amount(category)
                print(f"Current amount: {format_currency(current, budget.currency)}")
                amount_input = input("New amount: ").strip()
                amount = validate_positive_number(amount_input)
                if amount is not None:
                    if budget.add_category(category, amount):  # add_category also updates
                        print(f"✓ Updated {category}")
                    else:
                        print("✗ Failed to update (exceeds budget)")
                else:
                    print("✗ Invalid amount")
            else:
                print("✗ Category not found")
        
        elif choice == "3":
            category = input("Category to remove: ").strip()
            if budget.remove_category(category):
                print(f"✓ Removed {category}")
            else:
                print("✗ Category not found")
        
        elif choice == "4":
            current = budget.monthly_income
            print(f"Current income: {format_currency(current, budget.currency)}")
            income_input = input("New monthly income: ").strip()
            income = validate_positive_number(income_input)
            if income is not None:
                if update_budget_income(budget, income):
                    print("✓ Updated income and scaled categories proportionally")
                else:
                    print("✗ Failed to update income")
            else:
                print("✗ Invalid income amount")
        
        elif choice == "5":
            break
        
        else:
            print("Invalid choice")

def _export_budget_report(budget: Budget, transactions: List[Dict[str, Any]]):
    """Export budget report to file."""
    try:
        report = generate_budget_performance_report(budget, transactions)
        
        filename = f"budget_report_{get_current_date().replace('-', '')}.txt"
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✓ Budget report exported to: {filename}")
        
    except Exception as e:
        print(f"✗ Failed to export report: {e}")

# =============================================
# UTILITY FUNCTIONS
# =============================================

def get_budget_health_score(budget: Budget, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate a comprehensive budget health score.
    
    Args:
        budget: Budget instance
        transactions: List of transactions
        
    Returns:
        Dict: Health score and analysis
    """
    status = get_budget_status(budget, transactions)
    comparison = track_spending_vs_budget(budget, transactions)
    
    # Calculate health score (0-100)
    score = 100
    
    # Penalize over-budget categories
    over_budget_penalty = len(status['over_budget_categories']) * 10
    score -= over_budget_penalty
    
    # Penalize unbudgeted spending
    unbudgeted_penalty = len(status['unbudgeted_categories']) * 5
    score -= unbudgeted_penalty
    
    # Penalize high budget utilization (over 95%)
    if status['budget_utilization'] > 95:
        score -= (status['budget_utilization'] - 95) * 2
    
    # Bonus for good budget allocation (80-90% utilization)
    if 80 <= status['budget_utilization'] <= 90:
        score += 10
    
    # Ensure score is between 0 and 100
    score = max(0, min(100, score))
    
    # Determine health level
    if score >= 80:
        health_level = "Excellent"
    elif score >= 60:
        health_level = "Good"
    elif score >= 40:
        health_level = "Fair"
    else:
        health_level = "Poor"
    
    return {
        'score': round(score, 1),
        'health_level': health_level,
        'budget_utilization': status['budget_utilization'],
        'over_budget_count': len(status['over_budget_categories']),
        'unbudgeted_count': len(status['unbudgeted_categories']),
        'recommendations_count': len(suggest_budget_adjustments(budget, transactions))
    }

def format_budget_summary(budget: Budget) -> str:
    """
    Format budget summary for display.
    
    Args:
        budget: Budget instance
        
    Returns:
        str: Formatted budget summary
    """
    output = []
    output.append("=" * 50)
    output.append("BUDGET SUMMARY")
    output.append("=" * 50)
    output.append(f"Monthly Income: {format_currency(budget.monthly_income, budget.currency)}")
    output.append(f"Total Budgeted: {format_currency(budget.get_total_budget(), budget.currency)}")
    output.append(f"Remaining:      {format_currency(budget.get_remaining_budget(), budget.currency)}")
    output.append(f"Utilization:    {format_percentage(budget.get_budget_utilization())}")
    output.append(f"Created:        {budget.created_date}")
    output.append(f"Last Updated:   {budget.last_updated}")
    output.append("")
    
    output.append("CATEGORY BREAKDOWN")
    output.append("-" * 50)
    output.append(f"{'Category':<25} {'Amount':<15} {'Percentage'}")
    output.append("-" * 50)
    
    for category, amount in sorted(budget.categories.items()):
        percentage = budget.get_category_percentage(category)
        output.append(f"{category:<25} {format_currency(amount, budget.currency):<15} {format_percentage(percentage)}")
    
    return "\n".join(output)