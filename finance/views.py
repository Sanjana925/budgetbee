# Finance App Views
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
from django.db.models import Sum

from .forms import AccountForm, CategoryForm, TransactionForm
from .models import Account, Category, Transaction
from .utils import get_user_or_guest, calculate_totals
from .constants import (
    DEFAULT_ACCOUNTS, DEFAULT_ACCOUNT_ICONS,
    DEFAULT_CATEGORIES, DEFAULT_CATEGORY_ICONS, DEFAULT_CATEGORY_COLORS
)
from .signals import recalc_account_balance


# Get previous month and year
def prev_month(year, month):
    return (year - 1, 12) if month == 1 else (year, month - 1)


# Get next month and year
def next_month(year, month):
    return (year + 1, 1) if month == 12 else (year, month + 1)


# Home dashboard view
def home(request, year=None, month=None):
    user = get_user_or_guest(request.user)
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])

    txs = Transaction.objects.filter(
        account__user=user,
        date__range=(month_start, month_end)
    ).order_by('-date') if user else []

    transactions_by_date = defaultdict(lambda: {"items": [], "total_income": 0, "total_expense": 0})

    for tx in txs:
        d = str(tx.date)
        transactions_by_date[d]["items"].append(tx)
        if tx.type == "income":
            transactions_by_date[d]["total_income"] += tx.amount
        else:
            transactions_by_date[d]["total_expense"] += tx.amount

    total_income = txs.filter(type="income").aggregate(total=Sum("amount"))["total"] or 0
    total_expense = txs.filter(type="expense").aggregate(total=Sum("amount"))["total"] or 0
    balance = total_income - total_expense

    prev_year, prev_m = prev_month(year, month)
    next_year, next_m = next_month(year, month)

    return render(request, "finance/home.html", {
        "active": "home",
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "transactions_by_date": dict(transactions_by_date),
        "current_year": year,
        "current_month": month,
        "prev_year": prev_year,
        "prev_month": prev_m,
        "next_year": next_year,
        "next_month": next_m,
        "is_authenticated": bool(user),
    })


# Charts view
def chart(request, year=None, month=None):
    user = get_user_or_guest(request.user)
    today = date.today()
    year = int(year) if year else today.year
    month = int(month) if month else today.month

    month_start = date(year, month, 1)
    month_end = date(year, month, monthrange(year, month)[1])

    if not user:
        return render(request, "finance/chart.html", {
            "active": "chart",
            "income_json": "{}",
            "expense_json": "{}",
            "monthly_json": "[]",
            "category_colors_json": "{}",
            "current_year": year,
            "current_month": month,
            "is_authenticated": False,
        })

    txs = Transaction.objects.filter(
        account__user=user,
        date__range=(month_start, month_end)
    ).select_related("category")

    income_data = defaultdict(float)
    expense_data = defaultdict(float)
    monthly_totals = []

    for tx in txs:
        cname = tx.category.name
        if tx.type == "income":
            income_data[cname] += float(tx.amount)
        else:
            expense_data[cname] += float(tx.amount)

        d = str(tx.date)
        row = next((x for x in monthly_totals if x["date"] == d), None)
        if not row:
            row = {"date": d, "income": 0, "expense": 0}
            monthly_totals.append(row)

        if tx.type == "income":
            row["income"] += float(tx.amount)
        else:
            row["expense"] += float(tx.amount)

    category_colors = {c.name: c.color for c in Category.objects.filter(user=user)}

    return render(request, "finance/chart.html", {
        "active": "chart",
        "income_json": json.dumps(income_data),
        "expense_json": json.dumps(expense_data),
        "monthly_json": json.dumps(monthly_totals),
        "category_colors_json": json.dumps(category_colors),
        "current_year": year,
        "current_month": month,
        "is_authenticated": True,
    })


# Add new transaction
def add_transaction(request):
    user = get_user_or_guest(request.user)
    if not user:
        return JsonResponse({"error": "login_required"}, status=403)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = TransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.account = Account.objects.get(id=request.POST["account"], user=user)
            tx.category = Category.objects.get(id=request.POST["category"], user=user)
            tx.save()

            total_income, total_expense, total_balance = calculate_totals(user)
            return JsonResponse({
                "success": True,
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "balance": float(total_balance),
            })

        return JsonResponse({"success": False, "error": form.errors.as_json()}, status=400)

    return JsonResponse({"success": False}, status=400)


# Edit transaction
@login_required
def edit_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, id=transaction_id, account__user=request.user)

    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        form = TransactionForm(request.POST, instance=tx)
        if form.is_valid():
            form.save()
            total_income, total_expense, total_balance = calculate_totals(request.user)
            return JsonResponse({
                "success": True,
                "total_income": float(total_income),
                "total_expense": float(total_expense),
                "balance": float(total_balance),
            })

        return JsonResponse({"success": False, "error": form.errors.as_json()}, status=400)


# Delete transaction
@login_required
def delete_transaction(request, transaction_id):
    tx = get_object_or_404(Transaction, id=transaction_id, account__user=request.user)
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        tx.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False}, status=400)


# Category list page
def category(request):
    ctype = request.GET.get("type", "expense")
    user = get_user_or_guest(request.user)

    categories = Category.objects.filter(user=user, type=ctype) if user else []
    return render(request, "finance/category.html", {
        "categories": categories,
        "category_type": ctype,
        "is_authenticated": bool(user),
    })


# Accounts page
def accounts(request):
    user = get_user_or_guest(request.user)

    accounts_list = Account.objects.filter(user=user) if user else []
    total_income, total_expense, total_balance = calculate_totals(user) if user else (0, 0, 0)

    return render(request, "finance/accounts.html", {
        "active": "accounts",
        "user_accounts": accounts_list,
        "total_balance": total_balance,
        "total_income": total_income,
        "total_expense": total_expense,
        "is_authenticated": bool(user),
    })


# Settings page
def settings(request):
    user = get_user_or_guest(request.user)
    if not user:
        messages.warning(request, "Login required.")
        return redirect("userauths:login")
    return render(request, "finance/settings.html", {"active": "settings"})
