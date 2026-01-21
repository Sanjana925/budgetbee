from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from userauths.models import User

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .constants import DEFAULT_ACCOUNT_ICONS

class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)

    def __str__(self):
        return self.name or "Guest"


class Account(models.Model):
    ICON_CHOICES = DEFAULT_ACCOUNT_ICONS

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, default="Untitled")
    initial_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    icon = models.CharField(max_length=5, choices=ICON_CHOICES, default="🐖")

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.icon} {self.name}"


class Category(models.Model):
    CATEGORY_TYPE = (('expense', 'Expense'), ('income', 'Income'))

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=5, default='📁')
    type = models.CharField(max_length=10, choices=CATEGORY_TYPE)
    color = models.CharField(max_length=7, default='#FFA500')
    default_budget = models.FloatField(default=0)
    class Meta:
        unique_together = ('user', 'name', 'type')

    def __str__(self):
        return f"{self.name} ({self.type})"

class Transaction(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    type = models.CharField(
        max_length=10,
        choices=[('income', 'Income'), ('expense', 'Expense')]
    )
    note = models.CharField(max_length=255, blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.type} - Rs {self.amount}"


class Budget(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        limit_choices_to={'type': 'expense'}
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )

    month = models.IntegerField()
    year = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.category.name} - Rs {self.amount} ({self.month}/{self.year})"
