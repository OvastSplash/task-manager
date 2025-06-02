from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('tasks/', include('tasks.urls')),
    path('api/v1/task/', include('APItasks.urls'))
]
