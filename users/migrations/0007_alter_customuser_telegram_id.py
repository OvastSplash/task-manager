# Generated by Django 5.2.1 on 2025-06-02 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_customuser_telegram_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='telegram_id',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
