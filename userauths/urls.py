# userauths/urls.py
from django.urls import path
from . import views

app_name = "userauths"  # <-- namespace for userauths app

urlpatterns = [
    path('signup/', views.register_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
