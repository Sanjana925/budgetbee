from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.home, name='home'),
    path('chart/', views.chart, name='chart'),
    path('accounts/', views.accounts, name='accounts'),
    path('category/', views.category, name='category'),
    path('settings/', views.settings, name='settings'),
]
