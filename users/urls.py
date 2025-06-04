from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('telegram_auth/', views.TelegramAuthView, name="telegram_auth"),
    path('update_profile/', views.update_profile, name="update_profile"),
    path('logout/', views.logout_view, name="logout"),
]