from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('send/', views.send_email, name='send'),
    path('reset_pass/', views.reset_password_view, name='reset-password'),
]