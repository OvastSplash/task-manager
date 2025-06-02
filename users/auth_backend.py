from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailOrLoginBackend(ModelBackend):
    def authenticate(self, request, login = None, password = None, **kwargs):
        if login is None or password is None:
            return None

        login_field = UserModel.USERNAME_FIELD

        try:
            user = UserModel.objects.get(**{login_field: login})

        except UserModel.DoesNotExist:
            try:
                user = UserModel.objects.get(email=login)

            except UserModel.DoesNotExist:
                return None
            
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None