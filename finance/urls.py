from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    # Home / Dashboard
    path('', views.home, name='home'),

    # Transactions
    path('transaction/', views.add_transaction, name='add_transaction'),            # Add transaction modal + POST
    path('transaction/edit/<int:transaction_id>/', views.edit_transaction, name='edit_transaction'),  # Edit transaction modal + POST
    path('transaction/delete/<int:transaction_id>/', views.delete_transaction, name='delete_transaction'),  # Delete via AJAX

    # Accounts
    path('accounts/', views.accounts, name='accounts'),
    path('accounts/add/', views.add_account, name='add_account'),
    path('accounts/edit/<int:account_id>/', views.edit_account, name='edit_account'),
    path('accounts/delete/<int:account_id>/', views.delete_account, name='delete_account'),

    # Categories
    path('categories/', views.category, name='category'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),

    # Chart & Settings
    path('chart/', views.chart, name='chart'),
    path('settings/', views.settings, name='settings'),
]
