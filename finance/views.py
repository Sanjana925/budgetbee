from django.shortcuts import render

def home(request):
    return render(request, 'finance/home.html', {'active': 'home'})

def chart(request):
    return render(request, 'finance/chart.html', {'active': 'chart'})

def accounts(request):
    return render(request, 'finance/accounts.html', {'active': 'accounts'})

def category(request):
    return render(request, 'finance/category.html', {'active': 'category'})


def settings(request):
    return render(request, 'finance/settings.html', {'active': 'settings'})
