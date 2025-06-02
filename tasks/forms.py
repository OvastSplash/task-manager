from django import forms
from .models import Task, TaskCategory

class CreateTaskForm(forms.ModelForm):
    title = forms.CharField(label="Создайте новую задачу", max_length=30)

    class Meta:
        model = Task
        fields = ['title']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")

        if title is None:
            raise forms.ValidationError("Введите задачу")
        
        return cleaned_data

class CreateCategoryForm(forms.ModelForm):
    title = forms.CharField(label="Название категории", max_length=50)

    class Meta:
        model = TaskCategory
        fields = ['title']

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")

        if title is None:
            raise forms.ValidationError("Введите название категории")
        
        return cleaned_data