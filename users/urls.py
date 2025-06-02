from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('telegram_auth/', views.telegram_auth, name="telegram_auth")
]