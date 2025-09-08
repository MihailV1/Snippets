# from django.core.management.base import BaseCommand, CommandError
# from django.db.models import Count
#
# # from django.contrib.auth.models import User
# from MainApp.models import User
#
#
# class Command(BaseCommand):
#     # Атрибут 'help' — это краткое описание вашей команды.
#     # Оно отображается, когда пользователь вводит 'python manage.py help my_custom_command'
#     # или 'python manage.py my_custom_command --help'.
#     help = 'Пример кастомной команды: выводит список всех пользователей.'
#
#     # Метод add_arguments позволяет добавлять аргументы и опции для вашей команды.
#     # Это необязательно, если ваша команда не требует входных данных.
#     def add_arguments(self, parser):
#         parser.add_argument(
#             '--verbose',  # Имя опции
#             action='store_true',  # Тип действия: просто флаг, который устанавливается в True при наличии
#             help='Вывести более подробную информацию о пользователях.',
#         )
#         parser.add_argument(
#             '--limit',
#             type=int,  # Указываем, что аргумент должен быть целым числом
#             help='Ограничить количество выводимых пользователей.',
#         )
#
#     def handle(self, *args, **options):
#         verbose = options['verbose']
#         limit = options['limit']
#         users = User.objects.all()
#
#         for user in users[:limit]:
#             if verbose:
#                 self.stdout.write(f'{user.id} User --> {user.username} e-mail --> {user.email}')
#             else:
#                 self.stdout.write(f'{user.id} User --> {user.username}')
#
# duplicates = User.objects.values('email').annotate(count_emails=Count('email')).filter(count_emails__gt=1)
# user_d = User.objects.filter(email='test3@mail.com').order_by('date_joined')[1:]

