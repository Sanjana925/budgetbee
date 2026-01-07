from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Category, Account
from .constants import DEFAULT_CATEGORIES, DEFAULT_ACCOUNTS

User = get_user_model()


def create_default_categories(user):
    for c_type, items in DEFAULT_CATEGORIES.items():
        for name, icon, color in items:
            Category.objects.get_or_create(
                user=user, name=name, type=c_type, defaults={'icon': icon, 'color': color}
            )


def create_default_accounts(user):
    for name, icon, amount in DEFAULT_ACCOUNTS:
        Account.objects.get_or_create(
            user=user, name=name, defaults={'icon': icon, 'initial_amount': amount, 'balance': amount}
        )


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


@receiver(post_save, sender=User)
def create_defaults_for_new_user(sender, instance, created, **kwargs):
    if created:
        create_default_categories(instance)
        create_default_accounts(instance)
