# Generated by Django 5.2.3 on 2025-06-26 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0007_alter_snippet_lang'),
    ]

    operations = [
        migrations.AlterField(
            model_name='snippet',
            name='lang',
            field=models.CharField(choices=[('', '--- Выберите язык ---'), ('Python', 'Python'), ('cpp', 'C++'), ('java', 'Java'), ('JavaScript', 'JavaScript'), ('html', 'HTML'), ('C', 'C')], max_length=10),
        ),
    ]
