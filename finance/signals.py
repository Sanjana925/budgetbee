from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
from .models import Account, Transaction, Category
from .constants import DEFAULT_CATEGORIES, DEFAULT_ACCOUNTS

User = get_user_model()

# -----------------------------
# Default categories/accounts
# -----------------------------
def create_default_categories(user):
    for c_type, items in DEFAULT_CATEGORIES.items():
        for name, icon, color in items:
            Category.objects.get_or_create(
                user=user,
                name=name,
                type=c_type,
                defaults={'icon': icon, 'color': color}
            )

def create_default_accounts(user):
    for name, icon, amount in DEFAULT_ACCOUNTS:
        Account.objects.get_or_create(
            user=user,
            name=name,
            defaults={'icon': icon, 'initial_amount': amount, 'balance': amount}
        )

# -----------------------------
# Guest user
# -----------------------------
def get_or_create_guest_user():
    guest, created = User.objects.get_or_create(
        username="Guest",
        defaults={"email": "guest@example.com", "is_active": False}
    )
    if created:
        guest.set_unusable_password()
        guest.save()
        create_default_categories(guest)
        create_default_accounts(guest)
    return guest

# -----------------------------
# Recalculate account balance
# -----------------------------
def recalc_account_balance(account):
    """
    Recalculate balance: initial_amount + sum(income) - sum(expense)
    """
    income = Transaction.objects.filter(account=account, type='income').aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']
    
    expense = Transaction.objects.filter(account=account, type='expense').aggregate(
        total=Coalesce(Sum('amount'), 0, output_field=DecimalField())
    )['total']
    
    account.balance = account.initial_amount + income - expense
    account.save()

# -----------------------------
# Signals for transactions
# -----------------------------
@receiver(post_save, sender=Transaction)
def update_account_balance_on_save(sender, instance, created, **kwargs):
    recalc_account_balance(instance.account)

@receiver(post_delete, sender=Transaction)
def update_account_balance_on_delete(sender, instance, **kwargs):
    recalc_account_balance(instance.account)

# -----------------------------
# Signal for new users
# -----------------------------
@receiver(post_save, sender=User)
def create_defaults_for_new_user(sender, instance, created, **kwargs):
    if created:
        create_default_categories(instance)
        create_default_accounts(instance)
