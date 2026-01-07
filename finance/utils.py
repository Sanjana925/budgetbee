# location: finance/utils.py
import json
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Account, Transaction, Category
from django.contrib.auth.models import AnonymousUser


def get_user_or_guest(user):
    """
    Returns the actual user if logged in, otherwise None.
    Use user_id filters in queries to avoid errors with AnonymousUser.
    """
    if user.is_authenticated:
        return user
    return None  # safe fallback for queries


def calculate_totals(user):
    """
    Returns total_income, total_expense, balance for a user.
    """
    if not user:
        return 0, 0, 0  # Guest user gets zeros

    transactions = Transaction.objects.filter(account__user=user)
    accounts = Account.objects.filter(user=user)
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    balance = sum(a.balance for a in accounts)
    return total_income, total_expense, balance


def prepare_chart_data(user):
    """
    Prepares chart and monthly table data.
    Returns JSON strings for income, expense, monthly summary, and category colors.
    """
    if not user:
        return {
            'income_json': json.dumps({}),
            'expense_json': json.dumps({}),
            'monthly_json': json.dumps([]),
            'category_colors_json': json.dumps({})
        }

    transactions = Transaction.objects.filter(account__user=user).select_related('category')
    categories = Category.objects.filter(user=user)

    income_data, expense_data, category_colors = {}, {}, {}
    for cat in categories:
        category_colors[cat.name] = getattr(cat, 'color', '#ddd')

    for t in transactions:
        target = income_data if t.type == "income" else expense_data
        target[t.category.name] = target.get(t.category.name, 0) + t.amount

    monthly_data = []
    monthly_qs = transactions.annotate(month=TruncMonth('date')).values('month').order_by('month')
    months = sorted({item['month'] for item in monthly_qs})
    for m in months:
        month_income = transactions.filter(
            date__year=m.year, date__month=m.month, type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0
        month_expense = transactions.filter(
            date__year=m.year, date__month=m.month, type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        monthly_data.append({
            "date": m.strftime("%b %Y"),
            "income": float(month_income),
            "expense": float(month_expense)
        })

    return {
        'income_json': json.dumps({k: float(v) for k, v in income_data.items()}),
        'expense_json': json.dumps({k: float(v) for k, v in expense_data.items()}),
        'monthly_json': json.dumps(monthly_data),
        'category_colors_json': json.dumps(category_colors)
    }
