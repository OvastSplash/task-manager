from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch
from tasks.models import Task, TaskCategory
from users.models import CustomUser
from .serializers import TaskCategorySerializer, CategorySerializer, TaskSerializer, StatisticSerializer
from rest_framework.exceptions import NotFound

class BaseAPIView(APIView):
    def dispatch(self, request, *args, **kwargs):
        telegram_id = request.headers.get('TELEGRAM-ID')
        print(f"TELEGRAM_ID: {telegram_id}")
        
        try:
            self.user = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            raise NotFound(detail="User not found")
        
        return super().dispatch(request, *args, **kwargs)

class GetStatistic(BaseAPIView):
    def get(self, request, *args, **kwargs):
        categories = TaskCategory.objects.filter(user=self.user, is_visible=True)  
        all_tasks = Task.objects.filter(user=self.user, is_visible=True)
        done_tasks = Task.objects.filter(user=self.user, is_done=True)
        need_tasks = all_tasks.filter(is_done=False).count()
        
        data = {
            'categories_count': categories.count(),
            'total_tasks': all_tasks.count(),
            'completed_tasks': done_tasks.count(),
            'need_tasks': need_tasks
        }
        
        serializer = StatisticSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AllTasksView(BaseAPIView):
    # Получение всех задач из всех категорий
    def get(self, request, *args, **kwargs):
        category_number = request.headers.get('CATEGORY-NUMBER')
        
        # Если передан номер категории, то возвращаем задачи из этой категории
        if category_number:
            categories = TaskCategory.objects.filter(
                user=self.user,
                is_visible=True,
                number=category_number
            ).prefetch_related(
                Prefetch('tasks', queryset=Task.objects.filter(is_visible=True))
            )
            serializer = TaskCategorySerializer(categories, many=True)
            return Response(serializer.data)
        
        # Если не передан номер категории, то возвращаем все задачи
        else:
            tasks = TaskCategory.objects.filter(
                user=self.user,
                is_visible=True
            ).prefetch_related(
                Prefetch('tasks', queryset=Task.objects.filter(is_visible=True))
            )
            serializer = TaskCategorySerializer(tasks, many=True)
            
        return Response(serializer.data)
    
class CreateTaskView(BaseAPIView):
    # Добавление задачи
    def post(self, request, category_number, *args, **kwargs):
        try:
            category = TaskCategory.objects.get(user=self.user, is_visible=True, number=category_number)
        except TaskCategory.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        title = request.data.get('title')
        
        if title:
            data = {
                'user': self.user,
                'category': category,
            }
            serializer = TaskSerializer(data=request.data, context=data)
            
            if serializer.is_valid():
                serializer.create(serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        raise NotFound(detail="Task title not found")
        
        
class ActionTaskView(BaseAPIView):
    def put(self, request, category_number, task_number, *args, **kwargs):
        try:
            task = Task.objects.select_related('category').get(
                user=self.user,
                is_visible=True,
                number=task_number,
                category__number=category_number
            )
        except Task.DoesNotExist:
            raise NotFound(detail="Task not found")
        
        title = request.data.get('title')
        if not title:
            title = task.title

        is_done = request.data.get('is_done')
        print(f"IS DONE --- {is_done}")

        if not is_done and is_done != False:
            is_done = task.is_done

        if title:
            data = {
                'title': title,
                'is_done': is_done
            }
            serializer = TaskSerializer(instance=task, data=data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        raise NotFound(detail="Task not found")
    
    def delete(self, request, category_number, task_number, *args, **kwargs):
        try:
            task = Task.objects.select_related('category').get(
                user=self.user,
                is_visible=True,
                number=task_number,
                category__number=category_number
            )
        except Task.DoesNotExist:
            print("TASK NOT FOUND")
            raise NotFound(detail="Task not found")
        
        Task.objects.hide_task(task.id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoriesView(BaseAPIView):
    # Получение всех категорий
    def get(self, request, *args, **kwargs):
        categories = TaskCategory.objects.filter(user=self.user, is_visible=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    # Добавление категории
    def post(self, request, *args, **kwargs):
        category_title = request.data.get('title')
        if category_title:
            serializer = CategorySerializer(data=request.data, context={'user': self.user})
            
            if serializer.is_valid():
                serializer.create(serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        raise NotFound(detail="Category title not found")
        
    
    
class CategoriesActionView(BaseAPIView):
    # Редактирование категории
    def put(self, request, number, *args, **kwargs):
        category_title = request.data.get('title')
        
        if number and category_title:
            try:
                category = TaskCategory.objects.get(
                    user=self.user,
                    is_visible=True,
                    number=number
                )
            except TaskCategory.DoesNotExist:
                raise NotFound(detail="Category not found")

            data = {
                'title': category_title
            }

            serializer = CategorySerializer(instance=category, data=data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        raise NotFound(detail="Category number or title not found")

    # Удаление категории
    def delete(self, request, number, *args, **kwargs):
        try:
            category = TaskCategory.objects.get(user=self.user, is_visible=True, number=number)
            category_id = category.id
            TaskCategory.objects.hide_category(category_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except TaskCategory.DoesNotExist:
            raise NotFound(detail="Category not found")

