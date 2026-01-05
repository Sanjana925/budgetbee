# finance/models.py
from django.db import models
from userauths.models import User
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# One-to-one customer profile
class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name

# User accounts
class Account(models.Model):
    ICON_CHOICES = [("🏦","Bank"),("💳","Card"),("💰","Cash"),("🐖","Saving")]
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="Untitled")
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    icon = models.CharField(max_length=5, choices=ICON_CHOICES, default="🐖")

    def __str__(self):
        return f"{self.icon} {self.name}"

# Transaction categories
class Category(models.Model):
    CATEGORY_TYPE = (('expense','Expense'),('income','Income'))
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=5, default='📁')
    type = models.CharField(max_length=10, choices=CATEGORY_TYPE)
    color = models.CharField(max_length=7, default='#FFA500')
    def __str__(self):
        return f"{self.name} ({self.type})"

# Transactions
class Transaction(models.Model):
    customer = models.ForeignKey(Customer, null=True, blank=True, on_delete=models.SET_NULL)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=10, choices=[('income','Income'),('expense','Expense')])
    note = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.type} - Rs {self.amount}"

# Auto-update account balance on transaction
@receiver(post_save, sender=Transaction)
def update_balance_on_save(sender, instance, created, **kwargs):
    if created:
        if instance.type == "expense":
            instance.account.balance -= instance.amount
        else:
            instance.account.balance += instance.amount
        instance.account.save()

@receiver(post_delete, sender=Transaction)
def update_balance_on_delete(sender, instance, **kwargs):
    if instance.type == "expense":
        instance.account.balance += instance.amount
    else:
        instance.account.balance -= instance.amount
    instance.account.save()
