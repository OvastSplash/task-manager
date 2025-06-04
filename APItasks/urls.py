from django.urls import path
from . import views


urlpatterns = [
    path("", views.AllTasksView.as_view(), name="API_tasks"),
    path("statistic/", views.GetStatistic.as_view(), name="API_statistic"),
    path("categories/", views.CategoriesView.as_view(), name="API_categories"),
    path("categories/action/<int:number>/", views.CategoriesActionView.as_view(), name="API_categories_action"),
    path("action/<int:category_number>/", views.CreateTaskView.as_view(), name="API_task_action"),
    path("action/<int:category_number>/<int:task_number>/", views.ActionTaskView.as_view(), name="API_update_task")
]