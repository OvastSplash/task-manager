from django.db import models

# Create your models here.
class Token(models.Model):
    token = models.CharField(max_length=255, unique=True, null=False, verbose_name="Токен")
    
    def __str__(self):
        return self.token
