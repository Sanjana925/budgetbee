# finance/urls.py
from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.home, name='home'),
    path('chart/', views.chart, name='chart'),
     # Accounts page
    path('accounts/', views.accounts, name='accounts'),

    # AJAX CRUD endpoints
    path('accounts/add/', views.add_account, name='add_account'),
    path('accounts/edit/<int:account_id>/', views.edit_account, name='edit_account'),
    path('accounts/delete/<int:account_id>/', views.delete_account, name='delete_account'),

       path('category/', views.category, name='category'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('category/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('settings/', views.settings, name='settings'),
    path('transaction-modal/', views.add_transaction, name='transaction_modal'),
    path('transaction/add/', views.add_transaction, name='add-transaction'),
]
