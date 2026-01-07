# finance/context_processors.py
from .models import Account, Transaction
from .utils import get_user_or_guest

def user_financial_data(request):
    """
    Returns accounts, totals, and progress % for all templates.
    Safe for guest users.
    """
    user = get_user_or_guest(request.user)

    # Accounts: provide empty/default accounts if guest
    if user:
        accounts = Account.objects.filter(user=user)
    else:
        accounts = [
            {"name": "Bank", "balance": 0, "icon": "🏦"},
            {"name": "Card", "balance": 0, "icon": "💳"},
            {"name": "Cash", "balance": 0, "icon": "💰"},
            {"name": "Saving", "balance": 0, "icon": "🐖"},
        ]

    # Transactions only if user exists
    if user:
        transactions = Transaction.objects.filter(account__user=user)
        total_income = sum(t.amount for t in transactions if t.type == "income")
        total_expense = sum(t.amount for t in transactions if t.type == "expense")
    else:
        total_income = total_expense = 0

    # Balance
    total_balance = sum(a.balance for a in accounts) if user else sum(a["balance"] for a in accounts)

    # Progress bars
    total = total_income + total_expense
    if total > 0:
        earning_percent = (total_income / total) * 100
        spent_percent = (total_expense / total) * 100
    else:
        earning_percent = spent_percent = 0

    return {
        "user_accounts": accounts,
        "total_balance": total_balance,
        "total_income": total_income,
        "total_expense": total_expense,
        "earning_percent": round(earning_percent),
        "spent_percent": round(spent_percent),
    }
