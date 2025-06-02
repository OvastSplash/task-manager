from django.shortcuts import render, redirect
from django.contrib import messages
from . forms import CustromUserCreationForm, LoginForm
from . models import CustomUser
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required


# Create your views here.

def login(request):
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            login_or_email = form.cleaned_data['login']
            password = form.cleaned_data['password']

            user = authenticate(request, login=login_or_email, password=password)

            if user is not None:
                auth_login(request, user)
                return redirect("tasks")

            else:
                messages.error(request, "Неверный логин или пароль")

    return render(request, 'users/login.html', {'form': form})


def register(request):
    form = CustromUserCreationForm()

    if request.method == 'POST':
        form = CustromUserCreationForm(request.POST)

        if form.is_valid():
            login = form.cleaned_data['login']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            CustomUser.objects.create_user(login=login, password=password, email=email)
            return redirect("/")

    return render(request, 'users/register.html', {'form': form})


@login_required
def telegram_auth(request):
    if request.method == 'POST':
        telegram_id = request.POST.get('telegram_id')
        user = request.user
        if not CustomUser.objects.filter(telegram_id=telegram_id).exists():
            user.telegram_id = telegram_id
            user.save()
            return redirect("tasks")
        else:
            messages.error(request, "Пользователь с таким telegram id уже существует")
    
    return redirect("tasks")
