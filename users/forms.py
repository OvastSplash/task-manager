from django import forms
from .models import CustomUser

class CustromUserCreationForm(forms.ModelForm):
    login = forms.CharField(label='Логин', max_length=50)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    checkPassword = forms.CharField(label='Подтвердите пароль', widget=forms.PasswordInput)
    email = forms.EmailField(label='Email', required=False)
    telegram = forms.URLField(label='Ссылка на телеграм (не обязательно)', required=False)

    class Meta:
        model = CustomUser
        fields = ('login', 'email', 'telegram_id')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        checkPassword = cleaned_data.get("checkPassword")
        
        if not password:
            self.add_error("password", "Введите пароль")
        
        if not checkPassword:
            self.add_error("checkPassword", "Подтвердите пароль")

        if password != checkPassword:
            self.add_error("checkPassword", "Пароли не совпадают")
        
        return cleaned_data

    def clean_login(self):
        login = self.cleaned_data.get("login")

        if not login:
            raise forms.ValidationError("Введите логин")
        elif CustomUser.objects.filter(login=login).exists():
            raise forms.ValidationError("Данный пользователь уже зарегестрирован")
        
        return login
    
    def clean_email(self):
        email = self.cleaned_data.get("email")

        if not email:
            raise forms.ValidationError("Введите почту")
        elif CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Данная почта уже зарегестрирована")
        
        return email
    
    def clean_telegram(self):
        telegram_url = self.cleaned_data.get("telegram")
        if "https://t.me/" in telegram_url:
            telegram = telegram_url.split("https://t.me/")[1]
            
            if CustomUser.objects.filter(telegram_id=telegram).exists():
                raise forms.ValidationError("Данный пользователь уже зарегестрирован")
            
        else:
            raise forms.ValidationError("Введите корректную ссылку на телеграм")

        return telegram

class LoginForm(forms.Form):
    login = forms.CharField(label="Логин или email", max_length=50)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        login_or_email = cleaned_data.get("login")

        user = CustomUser.objects.filter(login=login_or_email)

        if not user.exists():
            user = CustomUser.objects.filter(email=login_or_email)

        if not user.exists():
            raise forms.ValidationError("Пользователь с таким именем или почтой не был найден")
        
        return cleaned_data      
    
class UpdateProfileForm(forms.ModelForm):
    new_password = forms.CharField(label="Новый пароль", widget=forms.PasswordInput, required=False)
    check_password = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput, required=False)
    email = forms.EmailField(label="Email", required=False)
    telegram = forms.URLField(label="Ссылка на телеграм", required=False)
    
    class Meta:
        model = CustomUser
        fields = []  # Пустой список, так как мы обрабатываем поля вручную
        
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        check_password = cleaned_data.get("check_password")
        
        # Проверяем пароли только если введен новый пароль
        if new_password:
            if not check_password:
                self.add_error("check_password", "Подтвердите пароль")
            elif new_password != check_password:
                self.add_error("check_password", "Пароли не совпадают")
        
        return cleaned_data
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise forms.ValidationError("Данная почта уже зарегестрирована")
        return email
    
    def clean_telegram(self):
        telegram_url = self.cleaned_data.get("telegram")
        if telegram_url:
            if "https://t.me/" in telegram_url:
                telegram = telegram_url.split("https://t.me/")[1]
                if CustomUser.objects.exclude(pk=self.instance.pk).filter(telegram_id=telegram).exists():
                    raise forms.ValidationError("Данный пользователь уже зарегестрирован")
                return telegram
            else:
                raise forms.ValidationError("Введите корректную ссылку на телеграм")
        return None