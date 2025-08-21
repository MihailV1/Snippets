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
    "python":"fa-brands fa-python",
    "cpp":"fa-solid fa-c",
    "C":"fa-solid fa-c",
    "java":"fa-brands fa-java",
    "javascript":"fa-brands fa-js",
    "html":"fa-brands fa-html5",
}
PUBLIC_CHOICES = [(0, 'Частный'),
            (1, 'Публичный'),
]
# class Lang(models.Model):
#     pass


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('comment', 'Новый комментарий'),
        ('like', 'Новый лайк'),
        ('follow', 'Новый подписчик'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    snippet = models.ForeignKey(   # 🔹 добавляем связь
        'Snippet',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True, blank=True,      # сделаем необязательным (для лайков/подписок)
    )
    # snippet = models.ForeignKey(Snippet, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

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
        blank=True,      # разрешает оставить поле пустым в форме
        null=True        # разрешает NULL в базе данных
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True, null=True)
    views_count = models.IntegerField(default=0)
    public = models.BooleanField(default=True)#, choices=PUBLIC_CHOICES)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                      blank=True, null=True)
    tags = models.ManyToManyField(to='Tag', blank=True, related_name='snippets')
    likes = GenericRelation(LikeDislike)

    def __repr__(self):
        return f"S: {self.name}|{self.lang} views:{self.views_count} public:{self.public} user:{self.user}"

    def likes_count(self):
        self.likes.filter(vote=LikeDislike.LIKE).count()

    def deslikes_count(self):
        self.likes.filter(vote=LikeDislike.DISLIKE).count()

class Comment(models.Model):
   text = models.TextField()
   creation_date = models.DateTimeField(auto_now_add=True)
   author = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
   snippet = models.ForeignKey(to=Snippet, on_delete=models.CASCADE, related_name='comments')
   likes = GenericRelation(LikeDislike)

   def __repr__(self):
       return f"C: {self.text[:10]} author:{self.author} sn: {self.snippet.name}"

   def likes_count(self):
       self.likes.filter(vote=LikeDislike.LIKE).count()
   def dislikes_count(self):
       self.likes.filter(vote=LikeDislike.DISLIKE).count()


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name


# class LikeDislike(models.Model):
#    LIKE = 1
#    DISLIKE = -1
#    VOTES = (
#        (LIKE, 'Like'),
#        (DISLIKE, 'Dislike'),
#    )
#    vote = models.SmallIntegerField(choices=VOTES)
#    user = models.ForeignKey(User, on_delete=models.CASCADE)
#
#    comment = models.ForeignKey(
#        Comment, on_delete=models.CASCADE, related_name='likes_dislikes'
#    )
#
#    class Meta:
#        # Уникальность связки: пользователь -> комментарий
#        unique_together = ('user', 'comment')

