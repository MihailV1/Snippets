from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from MainApp.models import *

LANG_CHOICES = [
    ("python", "Python"),
    ("cpp", "C++"),
    ("java", "Java"),
    ("javascript", "JavaScript")
]

LANG_ICON = {
    "python": "fa-brands fa-python",
    "cpp": "fa-solid fa-c",
    "C": "fa-solid fa-c",
    "java": "fa-brands fa-java",
    "javascript": "fa-brands fa-js",
    "html": "fa-brands fa-html5",
}
PUBLIC_CHOICES = [(0, 'Частный'),
                  (1, 'Публичный'),
                  ]



# User._meta.get_field('email')._unique = True

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('comment', 'Новый комментарий'),
        ('like', 'Новый лайк'),
        ('follow', 'Новый подписчик'),
        ('snippet_update', 'Обновление сниппета'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    snippet = models.ForeignKey(  # 🔹 добавляем связь
        'Snippet',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True, blank=True,  # сделаем необязательным (для лайков/подписок)
    )
    # snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
        ]

    def __str__(self):
        return f"Уведомление для {self.recipient.username}: {self.title}"


class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1
    VOTES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    vote = models.SmallIntegerField(choices=VOTES)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = ['user', 'content_type', 'object_id']



class Snippet(models.Model):
    class Meta:
        ordering = ('name',)

    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=10, choices=LANG_CHOICES)
    code = models.TextField(max_length=5000)
    description = models.TextField(
        max_length=1000,
        blank=True,  # разрешает оставить поле пустым в форме
        null=True  # разрешает NULL в базе данных
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, null=True)
    views_count = models.IntegerField(default=0)
    public = models.BooleanField(default=True)  # , choices=PUBLIC_CHOICES)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                             blank=True, null=True)
    tags = models.ManyToManyField(to='Tag', blank=True, related_name='snippets')
    likes = GenericRelation(LikeDislike)

    def __repr__(self):
        return f"S: {self.name}|{self.lang} views:{self.views_count} public:{self.public} user:{self.user}"

    @property # можно писать comment.likes_count без скобок
    def likes_count(self):
        return self.likes.filter(vote=LikeDislike.LIKE).count()

    @property
    def dislikes_count(self):
        return self.likes.filter(vote=LikeDislike.DISLIKE).count()

    class Meta:
        ordering = ['name','lang']
        indexes = [
            # models.Index(fields=['public','user']),
            models.Index(fields=['name','lang']),
            models.Index(fields=['user','name', 'lang']),
        ]


class Comment(models.Model):
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
    snippet = models.ForeignKey(to=Snippet, on_delete=models.CASCADE, related_name='comments')
    likes = GenericRelation(LikeDislike)

    def __repr__(self):
        return f"C: {self.text[:10]} author:{self.author} sn: {self.snippet.name}"

    @property
    def likes_count(self):
        """Количество лайков у комментария"""
        return self.likes.filter(vote=LikeDislike.LIKE).count()

    @property
    def dislikes_count(self):
        """Количество дизлайков у комментария"""
        return self.likes.filter(vote=LikeDislike.DISLIKE).count()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

    def __str__(self):
        return f"Профиль для {self.user.username}"

class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    snippet = models.ForeignKey(
        Snippet,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'snippet')
        ordering = ['-created_at']  # сортировка по дате подписки

    def __str__(self):
        return f"{self.user.username} подписан на {self.snippet.name}"