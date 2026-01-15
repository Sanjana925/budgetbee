# Finance App Utility Functions
import json
from decimal import Decimal
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from .models import Account, Transaction, Category


# ---------------------------
# GET USER OR RETURN NONE
# ---------------------------
def get_user_or_guest(user):
    """
    Returns the authenticated user or None for guests.
    """
    return user if user.is_authenticated else None


# ---------------------------
# CALCULATE TOTALS
# ---------------------------
def calculate_totals(user):
    """
    Returns total_income, total_expense, total_balance
    """
    if not user:
        return 0, 0, 0

    accounts = Account.objects.filter(user=user)

    # Total income
    total_income = Transaction.objects.filter(
        account__user=user, type='income'
    ).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']

    # Total expense
    total_expense = Transaction.objects.filter(
        account__user=user, type='expense'
    ).aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']

    # Total balance = initial_amount + income - expense per account
    total_balance = 0
    for a in accounts:
        income = Transaction.objects.filter(account=a, type='income').aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
        )['total']
        expense = Transaction.objects.filter(account=a, type='expense').aggregate(
            total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
        )['total']
        total_balance += a.initial_amount + income - expense

    return total_income, total_expense, total_balance


# ---------------------------
# PREPARE CHART DATA
# ---------------------------
def prepare_chart_data(user):
    """
    Prepares JSON data for charts: income, expense, monthly, category colors
    """
    if not user:
        return {'income_json': '{}', 'expense_json': '{}', 'monthly_json': '[]', 'category_colors_json': '{}'}

    transactions = Transaction.objects.filter(account__user=user).select_related('category')
    categories = Category.objects.filter(user=user)

    income_data, expense_data, category_colors = {}, {}, {}
    
    # Category colors
    for cat in categories:
        category_colors[cat.name] = getattr(cat, 'color', '#ddd')

    # Income / Expense totals per category
    for t in transactions:
        target = income_data if t.type == 'income' else expense_data
        target[t.category.name] = target.get(t.category.name, 0) + t.amount

    # Monthly totals
    monthly_data = []
    months = sorted({t.date.replace(day=1) for t in transactions})
    for m in months:
        month_income = transactions.filter(
            date__year=m.year, date__month=m.month, type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        month_expense = transactions.filter(
            date__year=m.year, date__month=m.month, type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_data.append({
            'date': m.strftime("%b %Y"),
            'income': float(month_income),
            'expense': float(month_expense)
        })

    return {
        'income_json': json.dumps({k: float(v) for k, v in income_data.items()}),
        'expense_json': json.dumps({k: float(v) for k, v in expense_data.items()}),
        'monthly_json': json.dumps(monthly_data),
        'category_colors_json': json.dumps(category_colors)
    }
