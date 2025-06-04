from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, login, password, **extra_fields):
        if not login:
            raise ValueError('Введите логин')
        
        if not password:
            raise ValueError('Введите пароль')
        
        elif self.model.objects.filter(login=login).exists():
            raise ValueError('Пользователь с таким имененм уже существует')

        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, login, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True')        

        return self.create_user(login, password, **extra_fields)
    
    def update_user(self, user, password=None, email=None, telegram=None, **extra_fields):
        """Обновляет данные пользователя"""
        if password:
            user.set_password(password)
        
        # Обновляем email даже если он пустой (None)
        user.email = email
        
        # Обновляем telegram_id даже если он пустой (None)
        user.telegram_id = telegram
        
        # Обновляем дополнительные поля
        for field, value in extra_fields.items():
            setattr(user, field, value)
            
        user.save(using=self.db)
        return user
        

class CustomUser(AbstractBaseUser):
    login = models.CharField(max_length=50, unique=True)
    email = models.EmailField(null=True, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    telegram_id = models.CharField(max_length=50, null=True)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.login
    
    def has_perm(self, perm, obj=None):
        return self.is_superuser
    
    def has_module_perms(self, app_label):
        return self.is_superuser