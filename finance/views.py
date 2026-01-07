# finance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .forms import AccountForm, CategoryForm
from .models import Account, Category, Transaction
from .utils import get_user_or_guest, calculate_totals, prepare_chart_data

# finance/views.py
from .constants import DEFAULT_CATEGORY_ICONS, DEFAULT_CATEGORY_COLORS, DEFAULT_CATEGORIES
from django.contrib.auth.decorators import login_required

# ---------------------------
# HOME DASHBOARD
# ---------------------------
def home(request):
    """
    Home dashboard: shows accounts, balance, income/expense.
    Guests see empty/default accounts.
    """
    user = get_user_or_guest(request.user)
    total_income, total_expense, balance = calculate_totals(user)

    accounts = Account.objects.filter(user=user) if user else []

    return render(request, 'finance/home.html', {
        "active": "home",
        "accounts": accounts,
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": balance,
        "is_authenticated": bool(user),
    })


# ---------------------------
# ADD TRANSACTION (Modal)
# ---------------------------
def add_transaction(request):
    """
    Add transaction via modal.
    Guests are blocked and receive JSON error.
    """
    user = get_user_or_guest(request.user)
    if not user:
        return JsonResponse({"error": "login_required"}, status=403)

    accounts = Account.objects.filter(user=user)
    categories = Category.objects.filter(user=user)
    today = timezone.now().date()

    if request.method == "POST":
        try:
            account = Account.objects.get(id=request.POST.get("account"), user=user)
            category = Category.objects.get(id=request.POST.get("category"), user=user)
            amount = float(request.POST.get("amount"))
            t_type = request.POST.get("type")
            note = request.POST.get("note")
            date = request.POST.get("date")

            if amount <= 0:
                return JsonResponse({"error": "Amount must be greater than 0"}, status=400)

            Transaction.objects.create(
                account=account, category=category, amount=amount, type=t_type, note=note, date=date
            )

            # Recalculate totals
            total_income, total_expense, balance = calculate_totals(user)

            return JsonResponse({
                "success": True,
                "total_income": total_income,
                "total_expense": total_expense,
                "balance": balance
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, 'finance/transaction_modal.html', {
        'accounts': accounts,
        'categories': categories,
        'today': today
    })


# ---------------------------
# CHART VIEW
# ---------------------------
def chart(request):
    """
    Chart view: income/expense per category & monthly totals.
    Guests see empty charts.
    """
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


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Category
from .forms import CategoryForm
from .utils import get_user_or_guest

def category(request):
    """
    Return categories list (guest defaults or user-specific).
    """
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


def add_category(request):
    user = get_user_or_guest(request.user)
    if not user:
        return JsonResponse({"success": False, "error": "Login required"}, status=403)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = user
            cat.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": form.errors.as_json()})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def edit_category(request, category_id):
    user = get_user_or_guest(request.user)
    if not user:
        return JsonResponse({"success": False, "error": "Login required"}, status=403)

    category = get_object_or_404(Category, id=category_id, user=user)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return JsonResponse({"success": True})
        return JsonResponse({"success": False, "error": form.errors.as_json()})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)


def delete_category(request, category_id):
    user = get_user_or_guest(request.user)
    if not user:
        return JsonResponse({"success": False, "error": "Login required"}, status=403)

    category = get_object_or_404(Category, id=category_id, user=user)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        category.delete()
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Account
from .utils import get_user_or_guest, calculate_totals
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Account
from .utils import get_user_or_guest, calculate_totals
from .constants import DEFAULT_ACCOUNTS, DEFAULT_ACCOUNT_ICONS

def accounts(request):
    user = get_user_or_guest(request.user)

    if user:
        accounts_list = [{"id":a.id, "name":a.name, "balance":a.balance, "icon":a.icon} for a in Account.objects.filter(user=user)]
        total_income, total_expense, total_balance = calculate_totals(user)
    else:
        accounts_list = [{"id":i+1, "name":name, "balance":balance, "icon":icon} for i,(name,icon,balance) in enumerate(DEFAULT_ACCOUNTS)]
        total_income, total_expense, total_balance = 0.0, 0.0, 0.0

    return render(request,'finance/accounts.html',{
        "active":"accounts",
        "user_accounts":accounts_list,
        "total_balance":total_balance,
        "total_income":total_income,
        "total_expense":total_expense,
        "is_authenticated": bool(user),
        "default_account_icons": DEFAULT_ACCOUNT_ICONS
    })

@login_required
def add_account(request):
    if request.method=="POST" and request.headers.get('x-requested-with')=='XMLHttpRequest':
        name = request.POST.get('name','').strip()
        initial_amount = float(request.POST.get('initial_amount') or 0)
        icon = request.POST.get('icon','💰')
        if not name: return JsonResponse({"success":False,"error":"Account name required"})
        Account.objects.create(user=request.user,name=name,initial_amount=initial_amount,balance=initial_amount,icon=icon)
        return JsonResponse({"success":True})
    return JsonResponse({"success":False,"error":"Invalid request"},status=400)

@login_required
def edit_account(request,account_id):
    account = get_object_or_404(Account,pk=account_id,user=request.user)
    if request.method=="POST" and request.headers.get('x-requested-with')=='XMLHttpRequest':
        name = request.POST.get('name','').strip()
        initial_amount = float(request.POST.get('initial_amount') or account.initial_amount)
        icon = request.POST.get('icon',account.icon)
        if not name: return JsonResponse({"success":False,"error":"Account name required"})
        account.name=name
        account.initial_amount=initial_amount
        account.icon=icon
        account.save()
        # Recalculate balance based on transactions
        from .signals import recalc_account_balance
        recalc_account_balance(account)
        return JsonResponse({"success":True})
    return JsonResponse({"success":False,"error":"Invalid request"},status=400)

@login_required
def delete_account(request,account_id):
    account = get_object_or_404(Account,pk=account_id,user=request.user)
    if request.method=="POST" and request.headers.get('x-requested-with')=='XMLHttpRequest':
        account.delete()
        return JsonResponse({"success":True})
    return JsonResponse({"success":False,"error":"Invalid request"},status=400)

# ---------------------------
# SETTINGS PAGE
# ---------------------------
def settings(request):
    user = get_user_or_guest(request.user)
    if not user:
        messages.warning(request, "You must be logged in to access settings.")
        return redirect('userauths:login')

    return render(request, 'finance/settings.html', {'active':'settings'})

