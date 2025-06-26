from django.db import models

LANG_CHOICES = [('', '--- Выберите язык ---'),
            ("python", "Python"),
            ("cpp", "C++"),
            ("java", "Java"),
            ("javascript", "JavaScript"),
            ('html', 'HTML'),
]
# class Lang(models.Model):
#     pass

class Snippet(models.Model):
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=10, choices=LANG_CHOICES)
    code = models.TextField(max_length=5000)
    creation_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
