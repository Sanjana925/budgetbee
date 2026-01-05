# finance/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import AccountForm, CategoryForm
from .models import Account, Category, Transaction, Customer

# Home dashboard
@login_required
def home(request):
    accounts = Account.objects.filter(user=request.user)
    transactions = Transaction.objects.filter(account__user=request.user).select_related('account', 'category')
    total_income = sum(t.amount for t in transactions if t.type=="income")
    total_expense = sum(t.amount for t in transactions if t.type=="expense")
    balance = sum(a.balance for a in accounts)
    return render(request, 'finance/home.html', {
        "active":"home", "accounts":accounts,
        "total_income":total_income, "total_expense":total_expense,
        "balance":balance
    })

# Add transaction via modal
@login_required
def add_transaction(request):
    accounts = Account.objects.filter(user=request.user)
    categories = Category.objects.filter(user=request.user)
    today = timezone.now().date()

    if request.method=="POST":
        try:
            account = Account.objects.get(id=request.POST.get("account"), user=request.user)
            category = Category.objects.get(id=request.POST.get("category"), user=request.user)
            amount = float(request.POST.get("amount"))
            t_type = request.POST.get("type")
            note = request.POST.get("note")
            date = request.POST.get("date")
            if amount<=0:
                return JsonResponse({"error":"Amount must be greater than 0"}, status=400)
            Transaction.objects.create(account=account, category=category, amount=amount, type=t_type, note=note, date=date)
            total_income = sum(t.amount for t in Transaction.objects.filter(account__user=request.user) if t.type=="income")
            total_expense = sum(t.amount for t in Transaction.objects.filter(account__user=request.user) if t.type=="expense")
            balance = sum(a.balance for a in Account.objects.filter(user=request.user))
            return JsonResponse({"success":True, "total_income":total_income, "total_expense":total_expense, "balance":balance})
        except Exception as e:
            return JsonResponse({"error":str(e)}, status=400)

    return render(request, 'finance/transaction_modal.html', {'accounts':accounts,'categories':categories,'today':today})

# Chart view
# finance/views.py
import json
from django.db.models import Sum
from django.utils import timezone

@login_required
def chart(request):
    # Get all transactions for the user
    transactions = Transaction.objects.filter(account__user=request.user).select_related('category')

    # Prepare income and expense category totals
    income_data = {}
    expense_data = {}
    category_colors = {}

    categories = Category.objects.filter(user=request.user)
    for cat in categories:
        category_colors[cat.name] = cat.color if hasattr(cat, 'color') else '#ddd'  # default color

    for t in transactions:
        target_dict = income_data if t.type == "income" else expense_data
        if t.category.name in target_dict:
            target_dict[t.category.name] += t.amount
        else:
            target_dict[t.category.name] = t.amount

    # Prepare monthly totals
    monthly_data = []
    # Group transactions by month
    from django.db.models.functions import TruncMonth
    monthly_qs = transactions.annotate(month=TruncMonth('date')).values('month').order_by('month')
    months = sorted(set(item['month'] for item in monthly_qs))

    for m in months:
        month_income = transactions.filter(date__year=m.year, date__month=m.month, type='income').aggregate(total=Sum('amount'))['total'] or 0
        month_expense = transactions.filter(date__year=m.year, date__month=m.month, type='expense').aggregate(total=Sum('amount'))['total'] or 0
        monthly_data.append({
            "date": m.strftime("%b %Y"),
            "income": float(month_income),
            "expense": float(month_expense)
        })

    # Ensure JSON serializable
    income_json = json.dumps({k: float(v) for k, v in income_data.items()})
    expense_json = json.dumps({k: float(v) for k, v in expense_data.items()})
    monthly_json = json.dumps(monthly_data)
    category_colors_json = json.dumps(category_colors)

    return render(request, 'finance/chart.html', {
        'active': 'chart',
        'income_json': income_json,
        'expense_json': expense_json,
        'monthly_json': monthly_json,
        'category_colors_json': category_colors_json,
    })

# Category list
@login_required
def category(request):
    ctype = request.GET.get('type','expense')
    categories = Category.objects.filter(user=request.user,type=ctype)
    return render(request, 'finance/category.html', {'categories':categories,'category_type':ctype})

@login_required
def add_category(request):
    if request.method=="POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=False)
            cat.user = request.user
            cat.save()
            messages.success(request,"Category added.")
            return redirect(f"{reverse('finance:category')}?type={cat.type}")
    else:
        form = CategoryForm()
    return render(request, 'finance/category_modal.html', {'form':form,'action':'Add'})

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category,id=category_id,user=request.user)
    if request.method=="POST":
        form = CategoryForm(request.POST,instance=category)
        if form.is_valid():
            form.save()
            messages.success(request,"Category updated.")
            return redirect(f"{reverse('finance:category')}?type={form.cleaned_data['type']}")
    else:
        form = CategoryForm(instance=category)
    return render(request,'finance/category_modal.html',{'form':form,'action':'Edit'})

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category,id=category_id,user=request.user)
    if request.method=="POST":
        ctype = category.type
        category.delete()
        messages.success(request,"Category deleted.")
        return redirect(f"{reverse('finance:category')}?type={ctype}")
    return render(request,'finance/delete_category_modal.html',{'category':category})

# Accounts CRUD
@login_required
def accounts(request):
    acc_list = Account.objects.filter(user=request.user)
    total_balance = sum(a.balance for a in acc_list)
    if request.method=="POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.user = request.user
            account.save()
            messages.success(request,"Account added successfully.")
            return redirect('finance:accounts')
    return render(request,'finance/accounts.html',{"active":"accounts","accounts":acc_list,"total_balance":total_balance})

@login_required
def edit_account(request, account_id):
    account = get_object_or_404(Account,pk=account_id,user=request.user)
    if request.method=="POST":
        form = AccountForm(request.POST,instance=account)
        if form.is_valid():
            form.save()
            messages.success(request,"Account updated.")
            return redirect('finance:accounts')
    else:
        form = AccountForm(instance=account)
    return render(request,'finance/edit_account.html',{"form":form,"account":account})

@login_required
def delete_account(request, account_id):
    account = get_object_or_404(Account,pk=account_id,user=request.user)
    if request.method=="POST":
        account.delete()
        messages.success(request,"Account deleted.")
        return redirect('finance:accounts')
    return render(request,'finance/delete_account.html',{"account":account})

# Settings page
@login_required
def settings(request):
    return render(request,'finance/settings.html',{'active':'settings'})

# Common context for templates
def common_context(request):
    accounts = Account.objects.filter(user=request.user) if request.user.is_authenticated else []
    return {'user_accounts':accounts}
