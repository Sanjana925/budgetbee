# finance/forms.py
from django import forms
from .models import Account, Category

class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'balance', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account Name'}),
            'balance': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Initial Amount'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emoji Icon'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon', 'type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emoji Icon'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
        }
