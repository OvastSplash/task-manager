from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Prefetch

# Create your models here.
User = get_user_model()

class TaskCategoryManager(models.Manager):
    # Создает категорию
    def create_category(self, user, title):
        all_categories = self.filter(user=user, is_visible=True)
        catogeries_count = all_categories.count()
        
        category = self.create(
            user=user, 
            title=title, 
            number=catogeries_count + 1
        )
        return category
    
    # Обновляет категорию
    def update_category(self, category_id, title, number, is_visible):
        category = self.get(id=category_id)
        category.title = title
        category.number = number

        if not is_visible:
            self.hide_category(category_id)
        elif not self.is_visible and is_visible:
            self.show_category(category_id)
        
        category.is_visible = is_visible
        category.save()
        
        return category
    
    # Скрывает категорию
    def hide_category(self, category_id):
        category = self.get(id=category_id)
        category.is_visible = False
        category.save()
        
        user = category.user
        categories = self.filter(user=user, is_visible=True).order_by('number')
        
        for i, cat in enumerate(categories, start=1):
            cat.number = i
            cat.save()

        tasks = Task.objects.filter(category=category).prefetch_related(Prefetch('category', queryset=TaskCategory.objects.filter(is_visible=True)))
        for task in tasks:
            Task.objects.hide_task(task.id)

        return category
    
    # Показывает категорию
    def show_category(self, category_id):
        category = self.get(id=category_id)
        category.is_visible = True
        category.save()
        
        user = category.user
        categories = self.filter(user=user, is_visible=True).order_by('number')
        
        for i, cat in enumerate(categories, start=1):
            cat.number = i
            cat.save()
        return category
    

        
class TaskCategory(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='categories')
    title = models.CharField(max_length=50, verbose_name="Название категории")
    is_visible = models.BooleanField(default=True, verbose_name="Показывать пользователю")
    number = models.IntegerField(verbose_name="Номер категории", default=0)

    objects = TaskCategoryManager()
    
    def __str__(self):
        return self.title
    
    

class TaskManager(models.Manager):
    def create_task(self, user, category, title, is_done=False):
        all_tasks = self.filter(user=user, category=category, is_visible=True)
        tasks_count = all_tasks.count()
        
        task = self.create(
            user=user,
            category=category,
            title=title,
            number=tasks_count + 1
        )
        return task
    
    # Обновляет задачу
    def update_task(self, task_id, title, number, is_visible, is_done):
        task = self.get(id=task_id)
        task.title = title
        task.number = number
        task.is_done = is_done

        if not is_visible:
            self.hide_task(task_id)
        elif not task.is_visible and is_visible:
            self.show_task(task_id)
        
        task.is_visible = is_visible
        task.save()
        
        return task
    
    # Скрывает задачу
    def hide_task(self, task_id):
        task = self.get(id=task_id)
        task.is_visible = False
        task.save()
        
        user = task.user
        category = task.category
        tasks = self.filter(user=user, category=category, is_visible=True).order_by('number')
        
        for i, tsk in enumerate(tasks, start=1):
            tsk.number = i
            tsk.save()
            
        return task
    
    # Показывает задачу
    def show_task(self, task_id):
        task = self.get(id=task_id)
        task.is_visible = True
        task.save()
        
        user = task.user
        category = task.category
        tasks = self.filter(user=user, category=category, is_visible=True).order_by('number')
        
        for i, tsk in enumerate(tasks, start=1):
            tsk.number = i
            tsk.save()
        return task
    
    # Отмечает задачу как выполненную
    def task_complete(self, task_id):
        task = self.get(id=task_id)
        task.is_done = not task.is_done
        task.save()
        return task

class Task(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE, related_name='tasks')
    category = models.ForeignKey(TaskCategory, verbose_name='Категория', on_delete=models.CASCADE, related_name='tasks', null=True)
    title = models.CharField(max_length=30, verbose_name="Заголовок")
    number = models.IntegerField(verbose_name="Номер задачи", default=0)
    is_done = models.BooleanField(default=False, verbose_name="Выполнено")
    is_visible = models.BooleanField(default=True, verbose_name="Показывать пользователю")

    objects = TaskManager()

    def __str__(self):
        return self.title