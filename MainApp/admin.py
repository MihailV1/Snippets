from django.contrib import admin
from django.db.models.aggregates import Count

# from django.db.models import Count

from .models import Snippet, Comment, Tag, Notification, LikeDislike, UserProfile


class SnippetAdmin(admin.ModelAdmin):
   list_display = ('name', 'lang', 'public', 'num_comments',)
   list_filter = ('lang', 'public')
   search_fields = ('name',)
   # Определение полей, которые будут отображаться в форме редактирования
   fields = ('name', 'lang', 'code', 'public', 'user','tags')

   # Метод для получения queryset с аннотированным полем
   def get_queryset(self, request):
       queryset = super().get_queryset(request)
       # Аннотируем каждую запись количеством комментариев
       queryset = queryset.annotate(
           num_comments=Count('comments', distinct=True)
       )
       return queryset

   # Добавление пользовательского поля
   def num_comments(self, obj):
       return obj.num_comments

   # Определение заголовка для пользовательского поля
   num_comments.short_description = 'Кол-во комментариев'

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def __str__(self):
        return f"Tag:{self.name}"

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'is_read', 'created_at', 'snippet')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__username')

    # Чтобы в админке удобно видеть статус
    list_editable = ('is_read',)

    # Только для чтения временные поля
    readonly_fields = ('created_at',)

# Register your models here.
admin.site.register(Snippet, SnippetAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Comment)
admin.site.register(Notification, NotificationAdmin)


# Изменение заголовка админ-панели
admin.site.site_header = "Snippets Admin"

# Изменение подзаголовка админ-панели
admin.site.site_title = "Snippets Admin Portal"

# Изменение заголовка индексной страницы админ-панели
admin.site.index_title = "Welcome to Snippets Admin Portal"

admin.site.register(UserProfile)