from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .forms import CreateTaskForm, CreateCategoryForm
from .models import Task, TaskCategory

# Create your views here.
@login_required
def main(request):
    form = TaskCategory.objects.filter(user=request.user, is_visible=True)

    if request.method == 'POST':
        if "create_category" in request.POST:
            form = CreateCategoryForm(request.POST)

            if form.is_valid():
                user = request.user
                
                category = form.save(commit=False)
                category.user = request.user
                category.number = TaskCategory.objects.filter(user=user, is_visible=True).count() + 1
                category.save()
        
        elif "create_task" in request.POST:
            task_form = CreateTaskForm(request.POST, prefix="task")
            category_form = CreateCategoryForm(request.POST, prefix='category')

            if task_form.is_valid():
                task = task_form.save(commit=False)
                task.user = request.user
                
                category_id = request.POST.get('category')
                task.category = TaskCategory.objects.filter(id=category_id, user=request.user).first()
                task.number = Task.objects.filter(category=task.category, is_visible=True).count() + 1
                task.save()

    else:
        cat_form = CreateCategoryForm(prefix="cat")
        if not form.count():
            task_form = CreateTaskForm(prefix="task")
        else:
            task_form = None
            

    tasks = Task.objects.filter(user=request.user, is_visible=True)
    completedTasks = Task.objects.filter(user=request.user, is_visible=True, is_done=True)
    totalTasks = tasks.count()

    categories = TaskCategory.objects.filter(user=request.user, is_visible=True)
    totalCategories = categories.count()

    context = {
        'form': form,
        'tasks': tasks,
        'completedTasks': completedTasks,
        'totalTasks': totalTasks,
        'categories': categories,
        'totalCategories': totalCategories,
    }

    return render(request, 'tasks/tasks.html', context)


# Отмечает задачу как выполненную
@login_required
def toggle_complete(request, task_id):
    if request.method == "POST":
        Task.objects.task_complete(task_id)
        
    return redirect('tasks')

# Удаляет задачу
@login_required
def delete_task(request, task_id):
    if request.method == 'POST':
        Task.objects.hide_task(task_id)

    return redirect('tasks')

# Удаляет категорию
@login_required
def delete_category(request, category_id):
    if request.method == 'POST':
        TaskCategory.objects.hide_category(category_id)
                
    return redirect('tasks')