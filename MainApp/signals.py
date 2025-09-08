from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from MainApp.models import Snippet, Comment, Notification, UserProfile, Subscription
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


# @receiver(post_save, sender=Snippet)
# def edit_snippet_notification(sender, instance, created, **kwargs):
#     if not created:
#         subs = Subscription.objects.filter(snippet=instance)
#         subs_list = list(subs)
#         print(f"subs_list _________-------------______________------------->>>>>>\n{subs_list}")
#         # for sub in subs:
#         #     user = sub.user
#         #     Notification.objects.create(
#         #         recipient=user,
#         #         notification_type='snippet_update',
#         #         title=f'Изменен сниппет "{instance.name}"',
#         #         message=f'Автор отредактировал сниппет "{instance.name}"'
#         #     )


@receiver(pre_save, sender=Snippet)
def snippet_store_old_values(sender, instance, **kwargs):
    """
    Перед сохранением — получаем старые значения из базы и сохраняем их в instance._old_values
    """
    if not instance.pk:
        return  # Новый сниппет — старых данных нет

    try:
        old_instance = Snippet.objects.get(pk=instance.pk)
        instance._old_values = {
            'name': old_instance.name,
            'code': old_instance.code,
            'description': old_instance.description,
            'tags': set(old_instance.tags.all()),
        }
    except Snippet.DoesNotExist:
        instance._old_values = None

@receiver(post_save, sender=Snippet)
def edit_snippet_notification(sender, instance, created, **kwargs):
    """
    Создаёт уведомления только если реально изменились важные поля,
    кроме views_count.
    """
    if created:
        # Новый сниппет — уведомления о создании не отправляем
        return

    if not hasattr(instance, '_old_values') or not instance._old_values:
        return  # Нет старых данных — нечего сравнивать

    old_values = instance._old_values
    changed_fields = []

    # Проверяем изменения по ключевым полям
    if old_values['code'] != instance.code:
        changed_fields.append("код")
    if old_values['name'] != instance.name:
        changed_fields.append("название")
    if old_values['description'] != instance.description:
        changed_fields.append("описание")

    # Проверка тегов
    current_tags = set(instance.tags.all())
    if old_values['tags'] != current_tags:
        changed_fields.append("теги")

    # Если нет изменений — выходим
    if not changed_fields:
        return

    # Формируем сообщение
    fields_str = ", ".join(changed_fields)
    message = f"Автор обновил {fields_str} сниппета «{instance.name}»"

    # Находим всех подписчиков
    subs = Subscription.objects.filter(snippet=instance).select_related('user')

    if not subs.exists():
        return

    # Создаём уведомления пакетно
    notifications = [
        Notification(
            recipient=sub.user,
            snippet=instance,
            notification_type='snippet_update',
            title=f"Изменен сниппет «{instance.name}»",
            message=message
        )
        for sub in subs
    ]

    Notification.objects.bulk_create(notifications)  # Оптимизированная вставка