# finance/views.py
import json
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from calendar import monthrange
from datetime import date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Sum

from .forms import AccountForm, CategoryForm, TransactionForm
from .models import Account, Category, Transaction, Budget
from .utils import get_user_or_guest, calculate_totals
from .constants import (
    DEFAULT_ACCOUNTS, DEFAULT_ACCOUNT_ICONS,
    DEFAULT_CATEGORIES, DEFAULT_CATEGORY_ICONS, DEFAULT_CATEGORY_COLORS
)
from .signals import recalc_account_balance

# ---------------- Month Navigation Helpers ----------------
def prev_month(year, month):
    if month == 1:
        return year - 1, 12
    return year, month - 1

def next_month(year, month):
    if month == 12:
        return year + 1, 1
    return year, month + 1

# ---------------- Home Dashboard ----------------
def home(request, year=None, month=None):
    user = get_user_or_guest(request.user)
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])

    txs = Transaction.objects.filter(account__user=user, date__range=(month_start, month_end)) if user else Transaction.objects.none()

    transactions_by_date = defaultdict(lambda: {"items": [], "total_income": 0, "total_expense": 0})
    for tx in txs:
        date_str = str(tx.date)
        transactions_by_date[date_str]["items"].append(tx)
        if tx.type == "income":
            transactions_by_date[date_str]["total_income"] += tx.amount
        else:
            transactions_by_date[date_str]["total_expense"] += tx.amount

    total_income = txs.filter(type="income").aggregate(total=Sum("amount"))["total"] or 0
    total_expense = txs.filter(type="expense").aggregate(total=Sum("amount"))["total"] or 0
    balance = total_income - total_expense
    accounts_list = Account.objects.filter(user=user) if user else []

    prev_year, prev_month_num = prev_month(year, month)
    next_year, next_month_num = next_month(year, month)

    return render(request, 'finance/home.html', {
        "active": "home",
        "accounts": accounts_list,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "transactions_by_date": dict(transactions_by_date),
        "current_year": year,
        "current_month": month,
        "prev_year": prev_year,
        "prev_month": prev_month_num,
        "next_year": next_year,
        "next_month": next_month_num,
        "is_authenticated": bool(user),
    })

# ---------------- Charts ----------------
def chart(request, year=None, month=None):
    user = get_user_or_guest(request.user)
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])

    if not user:
        return render(request, 'finance/chart.html', {
            'active': 'chart',
            'income_json': '{}',
            'expense_json': '{}',
            'monthly_json': '[]',
            'category_colors_json': '{}',
            'current_year': year,
            'current_month': month,
            'is_authenticated': False,
        })

    txs = Transaction.objects.filter(account__user=user, date__range=(month_start, month_end)).select_related('category')
    income_data, expense_data = defaultdict(float), defaultdict(float)
    monthly_totals = []

    for tx in txs:
        cat_name = tx.category.name
        if tx.type == "income":
            income_data[cat_name] += float(tx.amount)
        else:
            expense_data[cat_name] += float(tx.amount)

        date_str = str(tx.date)
        entry = next((x for x in monthly_totals if x["date"] == date_str), None)
        if not entry:
            entry = {"date": date_str, "income": 0, "expense": 0}
            monthly_totals.append(entry)
        if tx.type == "income":
            entry["income"] += float(tx.amount)
        else:
            entry["expense"] += float(tx.amount)

    category_colors = {c.name: c.color for c in Category.objects.filter(user=user)}

    return render(request, 'finance/chart.html', {
        'active': 'chart',
        'income_json': json.dumps(income_data),
        'expense_json': json.dumps(expense_data),
        'monthly_json': json.dumps(monthly_totals),
        'category_colors_json': json.dumps(category_colors),
        'current_year': year,
        'current_month': month,
        'is_authenticated': True,
    })

# ---------------- Transactions CRUD ----------------
def add_transaction(request):
    user = get_user_or_guest(request.user)
    if not user:
        return JsonResponse({"error": "login_required"}, status=403)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = TransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.account = Account.objects.get(id=request.POST.get("account"), user=user)
            tx.category = Category.objects.get(id=request.POST.get("category"), user=user)
            tx.user = user  # ✅ assign the user
            tx.save()

            total_income, total_expense, total_balance = calculate_totals(user)

            return JsonResponse({
                "success": True,
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "balance": float(total_balance),
                "transaction": {
                    "id": tx.id,
                    "amount": float(tx.amount),
                    "type": tx.type,
                    "category_id": tx.category.id,
                    "category_name": tx.category.name,
                    "category_icon": tx.category.icon,
                    "date": str(tx.date),
                    "note": tx.note
                }
            })
        return JsonResponse({"success": False, "error": form.errors.as_json()}, status=400)

    # Render transaction page with budgets
    accounts = Account.objects.filter(user=user)
    categories = Category.objects.filter(user=user)
    budgets = {}
    today = timezone.now().date()
    month, year = today.month, today.year
    txs = Transaction.objects.filter(user=user, type='expense', date__month=month, date__year=year)
    for b in Budget.objects.filter(user=user, month=month, year=year):
        spent = txs.filter(category=b.category).aggregate(total=Sum('amount'))['total'] or 0
        budgets[str(b.category.id)] = {'budget': float(b.amount), 'spent': float(spent)}

    return render(request, 'finance/transaction.html', {
        "accounts": accounts,
        "categories": categories,
        "today": today,
        "budgets_json": json.dumps(budgets),
    })


@login_required
def edit_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, id=transaction_id, account__user=request.user)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        # Save old values before updating
        old_amount = float(tx.amount)
        old_category_id = tx.category.id if tx.category else None

        form = TransactionForm(request.POST, instance=tx)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.account = Account.objects.get(id=request.POST.get("account"), user=request.user)
            tx.category = Category.objects.get(id=request.POST.get("category"), user=request.user)
            tx.user = request.user  # ✅ assign the user
            tx.save()

            total_income, total_expense, total_balance = calculate_totals(request.user)

            return JsonResponse({
                "success": True,
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "balance": float(total_balance),
                "transaction": {
                    "id": tx.id,
                    "amount": float(tx.amount),
                    "type": tx.type,
                    "category_id": tx.category.id,
                    "category_name": tx.category.name,
                    "category_icon": tx.category.icon,
                    "date": str(tx.date),
                    "old_amount": old_amount,
                    "old_category_id": old_category_id,
                    "note": tx.note,
                }
            })
        return JsonResponse({"success": False, "error": form.errors.as_json()}, status=400)

@login_required
def delete_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, id=transaction_id, account__user=request.user)
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tx.delete()
        total_income, total_expense, total_balance = calculate_totals(request.user)
        return JsonResponse({
            "success": True,
            "amount": float(tx.amount),
            "category_id": tx.category.id,
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "balance": float(total_balance),
            "transaction_id": transaction_id
        })
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

# ---------------- Categories CRUD ----------------
def category(request):
    ctype = request.GET.get('type', 'expense')
    user = get_user_or_guest(request.user)

    if user:
        categories = Category.objects.filter(user=user, type=ctype)
    else:
        categories = [
            {"id": i+1, "name": name, "icon": icon, "color": color}
            for i, (name, icon, color) in enumerate(DEFAULT_CATEGORIES.get(ctype, []))
        ]

    return render(request, 'finance/category.html', {
        "categories": categories,
        "category_type": ctype,
        "is_authenticated": bool(user),
        "default_category_icons": DEFAULT_CATEGORY_ICONS,
        "default_category_colors": DEFAULT_CATEGORY_COLORS,
    })

@login_required
def add_category(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": form.errors.as_json()})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": form.errors.as_json()})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        category.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

# ---------------- Accounts CRUD ----------------
def accounts(request):
    user = get_user_or_guest(request.user)
    if user:
        accounts_list = [
            {"id": a.id, "name": a.name, "balance": a.balance, "icon": a.icon} 
            for a in Account.objects.filter(user=user)
        ]
        total_income, total_expense, total_balance = calculate_totals(user)
    else:
        accounts_list = [
            {"id": i+1, "name": name, "balance": balance, "icon": icon} 
            for i, (name, icon, balance) in enumerate(DEFAULT_ACCOUNTS)
        ]
        total_income = total_expense = total_balance = 0.0

    return render(request, 'finance/accounts.html', {
        "active": "accounts",
        "user_accounts": accounts_list,
        "total_balance": total_balance,
        "total_income": total_income,
        "total_expense": total_expense,
        "is_authenticated": bool(user),
        "default_account_icons": DEFAULT_ACCOUNT_ICONS
    })

@login_required
def add_account(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', '💰')
        initial_amount_str = request.POST.get('initial_amount', '').strip()
        try:
            initial_amount = Decimal(initial_amount_str) if initial_amount_str else Decimal(0)
        except InvalidOperation:
            return JsonResponse({"success": False, "error": "Invalid initial amount"}, status=400)
        if not name:
            return JsonResponse({"success": False, "error": "Account name required"})
        Account.objects.create(user=request.user, name=name, initial_amount=initial_amount, balance=initial_amount, icon=icon)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def edit_account(request, account_id):
    account = get_object_or_404(Account, pk=account_id, user=request.user)
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name', '').strip()
        icon = request.POST.get('icon', account.icon)
        initial_amount_str = request.POST.get('initial_amount', '').strip()
        try:
            initial_amount = Decimal(initial_amount_str) if initial_amount_str else account.initial_amount
        except InvalidOperation:
            return JsonResponse({"success": False, "error": "Invalid initial amount"}, status=400)
        if not name:
            return JsonResponse({"success": False, "error": "Account name required"})
        account.name = name
        account.initial_amount = initial_amount
        account.icon = icon
        account.save()
        recalc_account_balance(account)
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def delete_account(request, account_id):
    account = get_object_or_404(Account, pk=account_id, user=request.user)
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        account.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

# ---------------- Settings ----------------
def settings(request):
    user = get_user_or_guest(request.user)
    if not user:
        messages.warning(request, "You must be logged in to access settings.")
        return redirect('userauths:login')
    return render(request, 'finance/settings.html', {'active': 'settings'})

# ---------------- Budget Views ----------------
def budget_default(request):
    today = date.today()
    return redirect('finance:budget', year=today.year, month=today.month)
from collections import defaultdict
from datetime import date
from calendar import monthrange
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.db.models import Sum
from .models import Category, Transaction, Budget

@login_required
def budget(request, year=None, month=None):
    user = request.user
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    # Month start/end
    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])

    # Categories
    categories_qs = Category.objects.filter(user=user, type="expense").order_by("name")

    # Transactions for this month
    transactions = Transaction.objects.filter(user=user, type="expense", date__range=(month_start, month_end))
    spent_map = defaultdict(Decimal)
    for tx in transactions:
        if tx.category_id:
            spent_map[tx.category_id] += tx.amount

    # Budgets for this month
    budgets_qs = Budget.objects.filter(user=user, month=month, year=year)
    budget_map = {b.category_id: b.amount for b in budgets_qs}

    categories = []
    budgets_json = {}
    for cat in categories_qs:
        spent = spent_map.get(cat.id, Decimal("0"))
        budget_amt = budget_map.get(cat.id, Decimal("0"))
        percent = (spent / budget_amt * 100) if budget_amt > 0 else 0

        categories.append({
            "id": cat.id,
            "name": cat.name,
            "icon": cat.icon,
            "spent": float(spent),
            "budget": float(budget_amt),
            "percent": int(min(percent, 100)),
            "exceeded": budget_amt > 0 and spent >= budget_amt
        })

        budgets_json[cat.id] = {
            "spent": float(spent),
            "budget": float(budget_amt),
            "percent": int(min(percent, 100)),
            "name": cat.name,
            "icon": cat.icon,
        }

    # Prev/Next month for navigation
    prev_month = month-1 or 12
    prev_year = year-1 if month == 1 else year
    next_month = month+1 if month < 12 else 1
    next_year = year+1 if month == 12 else year

    context = {
        "active": "budget",
        "categories": categories,
        "budgets_json": budgets_json,
        "current_year": year,
        "current_month": month,
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
    }
    return render(request, "finance/budget.html", context)

@login_required
def save_budget(request):
    if request.method != "POST" or request.headers.get("x-requested-with") != "XMLHttpRequest":
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    category_id = request.POST.get("category")
    amount = request.POST.get("amount")
    month = request.POST.get("month")
    year = request.POST.get("year")

    if not all([category_id, amount, month, year]):
        return JsonResponse({"success": False, "error": "Missing fields"}, status=400)

    try:
        amount = Decimal(amount)
        month = int(month)
        year = int(year)
    except:
        return JsonResponse({"success": False, "error": "Invalid data"}, status=400)

    category = get_object_or_404(Category, id=category_id, user=request.user, type="expense")

    # Save or update budget
    budget_obj, created = Budget.objects.update_or_create(
        user=request.user,
        category=category,
        month=month,
        year=year,
        defaults={"amount": amount}
    )

    # Calculate spent
    spent = Transaction.objects.filter(
        user=request.user,
        type="expense",
        category=category,
        date__year=year,
        date__month=month
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    percent = int(min((spent / amount * 100) if amount > 0 else 0, 100))
    exceeded = spent >= amount if amount > 0 else False

    return JsonResponse({
        "success": True,
        "budget": float(amount),
        "spent": float(spent),
        "percent": percent,
        "exceeded": exceeded,
        "name": category.name,
        "icon": category.icon,
    })
@login_required
def get_budget_spent(request):
    if request.method != "POST" or request.headers.get("x-requested-with") != "XMLHttpRequest":
        return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

    category_id = request.POST.get("category")
    month = request.POST.get("month")
    year = request.POST.get("year")

    if not all([category_id, month, year]):
        return JsonResponse({"success": False, "error": "Missing fields"}, status=400)

    try:
        category_id = int(category_id)
        month = int(month)
        year = int(year)
    except:
        return JsonResponse({"success": False, "error": "Invalid data"}, status=400)

    category = get_object_or_404(Category, id=category_id, user=request.user, type="expense")

    # Budget for this category/month/year
    budget_obj = Budget.objects.filter(user=request.user, category=category, month=month, year=year).first()
    budget_amount = budget_obj.amount if budget_obj else 0

    # Total spent
    spent = Transaction.objects.filter(
        user=request.user,
        type="expense",
        category=category,
        date__year=year,
        date__month=month
    ).aggregate(total=Sum("amount"))["total"] or 0

    percent = int(min((spent / budget_amount * 100) if budget_amount else 0, 100))
    exceeded = spent >= budget_amount if budget_amount else False

    return JsonResponse({
        "success": True,
        "spent": float(spent),
        "budget": float(budget_amount),
        "percent": percent,
        "exceeded": exceeded,
        "name": category.name,
        "icon": category.icon,
    })
