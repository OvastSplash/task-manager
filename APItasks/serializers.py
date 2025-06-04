from rest_framework import serializers, status
from tasks.models import Task, TaskCategory
from rest_framework.response import Response

class TaskSerializer(serializers.ModelSerializer):
    number = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Task
        fields = ['number', 'title', 'is_done']
        
    def create(self, validated_data):
        user = self.context.get('user')
        category = self.context.get('category')
        return Task.objects.create_task(user, category, **validated_data)
    
        
        
class TaskCategorySerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    class Meta:
        model = TaskCategory
        fields = ['number', 'title', 'tasks']
        
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = ['number', 'title']
        
    def create(self, validated_data):
        user = self.context.get('user')
        title = validated_data.get('title')
        
        if TaskCategory.objects.filter(user=user, title=title, is_visible=True).exists():
            raise serializers.ValidationError("Категория с таким названием уже существует")
        
        return TaskCategory.objects.create_category(user, title)

class StatisticSerializer(serializers.Serializer):
    categories_count = serializers.IntegerField()
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    need_tasks = serializers.IntegerField()