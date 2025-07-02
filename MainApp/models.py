from django.db import models
from django.contrib.auth.models import User


LANG_CHOICES = [('', '--- Выберите язык ---'),
            ("Python", "Python"),
            ("cpp", "C++"),
            ("java", "Java"),
            ("JavaScript", "JavaScript"),
            ('html', 'HTML'),
                ('C', 'C'),
]
LANG_ICON = {
    "Python":"fa-brands fa-python",
    "cpp":"fa-solid fa-c",
    "C":"fa-solid fa-c",
    "java":"fa-brands fa-java",
    "JavaScript":"fa-brands fa-js",
    "html":"fa-brands fa-html5",
}
PUBLIC_CHOICES = [(0, 'Частный'),
            (1, 'Публичный'),
]
# class Lang(models.Model):
#     pass

class Snippet(models.Model):
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=10, choices=LANG_CHOICES)
    code = models.TextField(max_length=5000)
    description = models.TextField(
        max_length=1000,
        blank=True,      # разрешает оставить поле пустым в форме
        null=True        # разрешает NULL в базе данных
    )
    creation_date = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    views_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    public = models.BooleanField(default=True, choices=PUBLIC_CHOICES)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE,
                      blank=True, null=True)
