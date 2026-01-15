# User Authentication Views
from django.shortcuts import render, redirect
from userauths.forms import UserRegistrationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from userauths.models import User
from finance.models import Customer

# Profile & Password Management
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Password Reset
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)

# ---------------- Registration ----------------
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            Customer.objects.create(
                user=new_user, 
                name=new_user.username, 
                email=new_user.email
            )
            auth_login(request, new_user)
            return redirect('userauths:login')
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = UserRegistrationForm()

    return render(request, 'userauths/signup.html', {'form': form})


# ---------------- Login ----------------
def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, "Hey, you are already logged in.")
        return redirect("finance:home")

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user:
            auth_login(request, user)
            return redirect('finance:home')
        else:
            messages.warning(request, 'Invalid email or password.')

    return render(request, 'userauths/login.html')


# ---------------- Logout ----------------
def logout_view(request):
    auth_logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('finance:home')


# ---------------- Profile / Edit User Info ----------------
@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        # Update username
        if "update_name" in request.POST:
            new_name = request.POST.get("username")
            if new_name:
                user.username = new_name
                user.save()
                messages.success(request, "Username updated successfully.")

        # Update avatar
        if "update_avatar" in request.FILES:
            user.profile_image = request.FILES["avatar"]
            user.save()
            messages.success(request, "Avatar updated successfully.")

        # Change password
        if "change_password" in request.POST:
            form = PasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, form.user)
                messages.success(request, "Password changed successfully.")
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(user)

    return render(request, "userauths/profile.html", {"form": form})


# ---------------- Password Reset Views ----------------
class CustomPasswordResetView(PasswordResetView):
    template_name = 'userauths/password_reset.html'
    email_template_name = 'userauths/password_reset_email.html'
    success_url = '/user/password-reset/done/'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'userauths/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'userauths/password_reset_confirm.html'
    success_url = '/user/password-reset-complete/'


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'userauths/password_reset_complete.html'


# ---------------- Change Password ----------------
@login_required
def change_password_view(request):
    user = request.user

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Password updated successfully!')
            return redirect('userauths:profile')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = PasswordChangeForm(user)

    return render(request, 'userauths/change_password.html', {'form': form})
