# finance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .forms import AccountForm, CategoryForm
from .models import Account, Category, Transaction
from .utils import get_user_or_guest, calculate_totals, prepare_chart_data


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


# ---------------------------
# CATEGORY VIEWS
# ---------------------------
def category(request):
    """
    List categories.
    Guests see empty/default categories.
    """
    ctype = request.GET.get('type', 'expense')
    user = get_user_or_guest(request.user)

    if user:
        categories = Category.objects.filter(user=user, type=ctype)
    else:
        categories = []  # could provide default categories

    return render(request, 'finance/category.html', {
        'categories': categories,
        'category_type': ctype,
        'is_authenticated': bool(user),
    })


def add_category(request):
    user = get_user_or_guest(request.user)
    if not user:
        messages.warning(request, "You must be logged in to add a category.")
        return redirect('userauths:login')

    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = user
            cat.save()
            messages.success(request, "Category added.")
            return redirect(f"{reverse('finance:category')}?type={cat.type}")
    else:
        form = CategoryForm()

    return render(request, 'finance/category_modal.html', {'form': form, 'action': 'Add'})


def edit_category(request, category_id):
    user = get_user_or_guest(request.user)
    if not user:
        messages.warning(request, "You must be logged in to edit a category.")
        return redirect('userauths:login')

    category = get_object_or_404(Category, id=category_id, user=user)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect(f"{reverse('finance:category')}?type={form.cleaned_data['type']}")
    else:
        form = CategoryForm(instance=category)

    return render(request,'finance/category_modal.html',{'form': form, 'action': 'Edit'})


def delete_category(request, category_id):
    user = get_user_or_guest(request.user)
    if not user:
        messages.warning(request, "You must be logged in to delete a category.")
        return redirect('userauths:login')

    category = get_object_or_404(Category, id=category_id, user=user)
    if request.method == "POST":
        ctype = category.type
        category.delete()
        messages.success(request, "Category deleted.")
        return redirect(f"{reverse('finance:category')}?type={ctype}")
    return render(request, 'finance/delete_category_modal.html', {'category': category})


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Account
from .utils import get_user_or_guest, calculate_totals

# ---------------------------
# ACCOUNTS PAGE
# ---------------------------
# finance/views.py
from django.shortcuts import render
from .utils import get_user_or_guest, calculate_totals
from .constants import DEFAULT_ACCOUNTS, DEFAULT_ACCOUNT_ICONS

def accounts(request):
    """
    Accounts page with summary cards and scrollable account list.
    Shows default accounts for guests using DEFAULT_ACCOUNTS from constants.py
    """
    user = get_user_or_guest(request.user)
    
    if user:
        # Logged-in user: fetch real accounts
        accounts_list = [
            {
                "id": acc.id,
                "name": acc.name,
                "balance": acc.balance,
                "icon": acc.icon
            } for acc in Account.objects.filter(user=user)
        ]
        total_balance, total_income, total_expense = calculate_totals(user)
    else:
        # Guest: use DEFAULT_ACCOUNTS from constants.py
        accounts_list = [
            {"id": i+1, "name": name, "balance": balance, "icon": icon}
            for i, (name, icon, balance) in enumerate(DEFAULT_ACCOUNTS)
        ]
        total_balance, total_income, total_expense = 0.0, 0.0, 0.0

    return render(request, 'finance/accounts.html', {
        "active": "accounts",
        "user_accounts": accounts_list,
        "total_balance": total_balance,
        "total_income": total_income,
        "total_expense": total_expense,
        "is_authenticated": bool(user),
        "default_account_icons": DEFAULT_ACCOUNT_ICONS,  # for Add/Edit popup
    })


# ---------------------------
# ADD ACCOUNT (AJAX)
# ---------------------------
@login_required
def add_account(request):
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name', '').strip()
        initial_amount = float(request.POST.get('initial_amount') or 0)
        icon = request.POST.get('icon', '💰')

        if not name:
            return JsonResponse({"success": False, "error": "Account name is required."})

        account = Account.objects.create(
            user=request.user,
            name=name,
            initial_amount=initial_amount,
            balance=initial_amount,
            icon=icon
        )
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


# ---------------------------
# EDIT ACCOUNT (AJAX)
# ---------------------------
@login_required
def edit_account(request, account_id):
    account = get_object_or_404(Account, pk=account_id, user=request.user)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        name = request.POST.get('name', '').strip()
        initial_amount = float(request.POST.get('initial_amount') or account.balance)
        icon = request.POST.get('icon', account.icon)

        if not name:
            return JsonResponse({"success": False, "error": "Account name is required."})

        account.name = name
        account.initial_amount = initial_amount
        account.balance = initial_amount
        account.icon = icon
        account.save()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)


# ---------------------------
# DELETE ACCOUNT (AJAX)
# ---------------------------
@login_required
def delete_account(request, account_id):
    account = get_object_or_404(Account, pk=account_id, user=request.user)

    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        account.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request."}, status=400)

# ---------------------------
# SETTINGS PAGE
# ---------------------------
def settings(request):
    user = get_user_or_guest(request.user)
    if not user:
        messages.warning(request, "You must be logged in to access settings.")
        return redirect('userauths:login')

    return render(request, 'finance/settings.html', {'active':'settings'})

