# Generated by Django 5.2.3 on 2025-06-26 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0004_alter_snippet_creation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='snippet',
            name='views_count',
            field=models.IntegerField(default=0),
        ),
    ]
