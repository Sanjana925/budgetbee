#userauths/views.py
from django.shortcuts import render, redirect
from userauths.forms import UserRegistrationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from userauths.models import User
from finance.models import Customer
# Register your views here.

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save() 
            Customer.objects.create(user=new_user, name=new_user.username, email=new_user.email)
            auth_login(request, new_user) 
            return redirect('finance:index') 
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = UserRegistrationForm()

    return render(request, 'userauths/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "Hey, you are already logged in.")
        return redirect("finance:index") 
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            auth_login(request, user) 
            return redirect('finance:index') 
        else:
            messages.warning(request, 'Invalid email or password.')
            return render(request, 'userauths/login.html')
        
    return render(request, 'userauths/login.html')

def logout_view(request):
    auth_logout(request)  
    messages.success(request, "You have been logged out.")
    return redirect('userauths:login')  