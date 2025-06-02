from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.main, name="tasks"),
    path('toggle_complete/<int:task_id>/', views.toggle_complete, name='toggle_complete'),
    path('delete_task/<int:task_id>/', views.delete_task, name="delete"),
    path('delete_category/<int:category_id>/', views.delete_category, name="delete_category"),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]