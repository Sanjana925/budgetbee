# Finance App Views
from decimal import Decimal, InvalidOperation
from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from .forms import AccountForm, CategoryForm, TransactionForm
from .models import Account, Category, Transaction
from .utils import get_user_or_guest, calculate_totals, prepare_chart_data
from .constants import (
    DEFAULT_ACCOUNTS, DEFAULT_ACCOUNT_ICONS,
    DEFAULT_CATEGORIES, DEFAULT_CATEGORY_ICONS, DEFAULT_CATEGORY_COLORS
)
from .signals import recalc_account_balance


# ---------------------------
# HOME DASHBOARD
# ---------------------------
def home(request):
    user = get_user_or_guest(request.user)
    total_income, total_expense, total_balance = calculate_totals(user)
    accounts_list = Account.objects.filter(user=user) if user else []

    # Group transactions by date
    transactions_by_date = defaultdict(lambda: {"items": [], "total_income": 0, "total_expense": 0})
    if user:
        txs = Transaction.objects.filter(account__user=user).order_by('-date')
        for tx in txs:
            date_str = str(tx.date)
            transactions_by_date[date_str]["items"].append(tx)
            if tx.type == "income":
                transactions_by_date[date_str]["total_income"] += tx.amount
            else:
                transactions_by_date[date_str]["total_expense"] += tx.amount

    return render(request, 'finance/home.html', {
        "active": "home",
        "accounts": accounts_list,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_balance,
        "transactions_by_date": dict(transactions_by_date),
        "is_authenticated": bool(user),
    })


# ---------------------------
# TRANSACTIONS CRUD
# ---------------------------
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
                    "category_name": tx.category.name,
                    "category_icon": tx.category.icon,
                    "date": str(tx.date),
                    "note": tx.note
                }
            })
        return JsonResponse({"success": False, "error": form.errors.as_json()}, status=400)

    # GET → render modal
    accounts = Account.objects.filter(user=user)
    categories = Category.objects.filter(user=user)
    today = timezone.now().date()
    return render(request, 'finance/transaction.html', {
        "accounts": accounts,
        "categories": categories,
        "today": today,
    })


@login_required
def edit_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, id=transaction_id, account__user=request.user)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = TransactionForm(request.POST, instance=tx)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.account = Account.objects.get(id=request.POST.get("account"), user=request.user)
            tx.category = Category.objects.get(id=request.POST.get("category"), user=request.user)
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
                    "category_name": tx.category.name,
                    "category_icon": tx.category.icon,
                    "date": str(tx.date),
                    "note": tx.note
                }
            })
        return JsonResponse({"success": False, "error": form.errors.as_json()}, status=400)

    accounts = Account.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    return render(request, 'finance/transaction.html', {
        "transaction": tx,
        "accounts": accounts,
        "categories": categories,
        "today": tx.date,
    })


@login_required
def delete_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, id=transaction_id, account__user=request.user)
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        tx.delete()
        total_income, total_expense, total_balance = calculate_totals(request.user)
        return JsonResponse({
            "success": True,
            "total_income": float(total_income),
            "total_expense": float(total_expense),
            "balance": float(total_balance),
            "transaction_id": transaction_id
        })
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


# ---------------------------
# CHARTS
# ---------------------------
def chart(request):
    user = get_user_or_guest(request.user)
    chart_data = prepare_chart_data(user)
    return render(request, 'finance/chart.html', {
        'active': 'chart',
        'income_json': chart_data['income_json'],
        'expense_json': chart_data['expense_json'],
        'monthly_json': chart_data['monthly_json'],
        'category_colors_json': chart_data['category_colors_json'],
        'is_authenticated': bool(user),
    })


# ---------------------------
# CATEGORY CRUD
# ---------------------------
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


# ---------------------------
# ACCOUNTS CRUD
# ---------------------------
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
        Account.objects.create(
            user=request.user, name=name,
            initial_amount=initial_amount, balance=initial_amount,
            icon=icon
        )
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


# ---------------------------
# SETTINGS PAGE
# ---------------------------
def settings(request):
    user = get_user_or_guest(request.user)
    if not user:
        messages.warning(request, "You must be logged in to access settings.")
        return redirect('userauths:login')
    return render(request, 'finance/settings.html', {'active': 'settings'})
