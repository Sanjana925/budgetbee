# finance/forms.py
from django import forms
from .models import Account, Category, Transaction

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
        fields = ['name', 'icon', 'type', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Emoji Icon'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'color': forms.TextInput(attrs={'type':'color','class':'form-control','value':'#FFA500'}), 
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'type', 'account', 'category', 'note', 'date']
        widgets = {
            'amount': forms.NumberInput(attrs={'class':'form-control', 'step':'0.01', 'placeholder':'Amount'}),
            'type': forms.Select(attrs={'class':'form-select'}),
            'account': forms.Select(attrs={'class':'form-select'}),
            'category': forms.Select(attrs={'class':'form-select'}),
            'note': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Note'}),
            'date': forms.DateInput(attrs={'class':'form-control', 'type':'date'}),
        }
