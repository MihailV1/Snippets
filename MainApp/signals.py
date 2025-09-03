from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from MainApp.models import Snippet, Comment, Notification, UserProfile
from django.dispatch import Signal
from django.db.models import F

# Декоратор @receiver() связывает функцию send_registration_message
# с сигналом post_save. Мы указываем, что нас интересуют только сигналы
# от модели User, и только когда created=True (т.е. пользователь был создан, а не обновлён).
@receiver(post_save, sender=User)
def send_registration_message(sender, instance, created, **kwargs):
    """
    Обработчик сигнала, который выводит сообщение о регистрации пользователя в терминал.
    Срабатывает при создании нового пользователя.
    """
    if created:  # Проверяем, что объект был только что создан
        print(f"--- Сигнал post_save получен ---")
        print(f"Пользователь '{instance.username}' успешно зарегистрирован!")
        print(f"Отправитель: {sender.__name__}")
        print(f"ID пользователя: {instance.id}")
        print(f"is_active пользователя: {instance.is_active}")
        print(f"--- Конец сигнала ---")


snippet_view = Signal()

@receiver(snippet_view)
def snippet_views_count(sender, snippet, **kwargs):
    snippet.views_count = F('views_count') + 1
    snippet.save(update_fields=['views_count'])
    snippet.refresh_from_db()


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.snippet.user and instance.author != instance.snippet.user:
        Notification.objects.create(
            recipient=instance.snippet.user,   # кому уведомление
            snippet=instance.snippet,
            notification_type='comment',      # тип уведомления
            title=f"Новый комментарий к «{instance.snippet.name}»",
            message=f"{instance.author.username} написал: {instance.text}" # [:50]
        )

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
   if created:
       UserProfile.objects.create(user=instance)