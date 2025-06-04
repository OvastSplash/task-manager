from django.shortcuts import render, redirect
from django.contrib import messages
from . forms import CustromUserCreationForm, LoginForm, UpdateProfileForm
from . models import CustomUser
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse, JsonResponse
from rest_framework import status
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
            telegram = form.cleaned_data['telegram']

            CustomUser.objects.create_user(login=login, password=password, email=email, telegram_id=telegram)
            return redirect("/")

    return render(request, 'users/register.html', {'form': form})

def TelegramAuthView(request):
    if request.method == 'GET':
        telegram_id = request.headers.get('TELEGRAM-ID')
        
        if telegram_id:
            try:
                user = CustomUser.objects.get(telegram_id=telegram_id)
                return JsonResponse({"login": user.login}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)
                
        
    return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

@login_required
def update_profile(request):
    if request.method == 'POST':
        form = UpdateProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            email = form.cleaned_data.get('email')
            telegram = form.cleaned_data.get('telegram')
            
            # Сначала сохраняем основные поля формы
            user = form.save(commit=False)
            
            # Затем обновляем дополнительные поля через менеджер
            CustomUser.objects.update_user(
                user=user,
                password=new_password if new_password else None,
                email=email,
                telegram=telegram
            )
            messages.success(request, "Профиль успешно обновлен")
            return redirect("tasks")
        else:
            messages.error(request, "Ошибка в введенных данных")
    else:
        initial_data = {
            'email': request.user.email,
            'telegram': f"https://t.me/{request.user.telegram_id}" if request.user.telegram_id else ""
        }
        form = UpdateProfileForm(instance=request.user, initial=initial_data)

    return render(request, 'users/update_profile.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')
