# finance/admin.py
from django.contrib import admin
from .models import Account

# Admin display for accounts
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'balance')
