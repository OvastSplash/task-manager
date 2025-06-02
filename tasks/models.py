from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class TaskCategory(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='categories')
    title = models.CharField(max_length=50, verbose_name="Название категории")
    is_visible = models.BooleanField(default=True, verbose_name="Показывать пользователю")

    def __str__(self):
        return self.title

class Task(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(TaskCategory, verbose_name='Категория', on_delete=models.CASCADE, related_name='tasks', null=True)
    title = models.CharField(max_length=30, verbose_name="Заголовок")
    is_done = models.BooleanField(default=False, verbose_name="Выполнено")
    is_visible = models.BooleanField(default=True, verbose_name="Показывать пользователю")

    def __str__(self):
        return self.title
    
