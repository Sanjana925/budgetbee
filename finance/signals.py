# finance/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from userauths.models import User
from .models import Category, Account

# Default categories per new user
DEFAULT_CATEGORIES = {
    "income":[("Salary","💼"),("Business","🏢"),("Gift","🎁"),("Investment","📈"),("Other Income","💵")],
    "expense":[("Food","🍔"),("Transport","🚌"),("Shopping","🛍️"),("Bills","💡"),("Entertainment","🎬")]
}

@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        for c_type, items in DEFAULT_CATEGORIES.items():
            for name, icon in items:
                Category.objects.create(user=instance, name=name, type=c_type, icon=icon)

# Default accounts per new user
DEFAULT_ACCOUNTS = [("Bank","🏦",0.0),("Card","💳",0.0),("Cash","💰",0.0),("Saving","🐖",0.0)]

@receiver(post_save, sender=User)
def create_default_accounts(sender, instance, created, **kwargs):
    if created:
        for name, icon, balance in DEFAULT_ACCOUNTS:
            Account.objects.create(user=instance, name=name, icon=icon, balance=balance)
