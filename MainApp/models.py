from django.db import models
from django.contrib.auth.models import User


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

    def __repr__(self):
        return f"S: {self.name}|{self.lang} views:{self.views_count} public:{self.public} user:{self.user}"

class Comment(models.Model):
   text = models.TextField()
   creation_date = models.DateTimeField(auto_now_add=True)
   author = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)
   snippet = models.ForeignKey(to=Snippet, on_delete=models.CASCADE, related_name='comments')

   def __repr__(self):
       return f"C: {self.text[:10]} author:{self.author} sn: {self.snippet.name}"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name