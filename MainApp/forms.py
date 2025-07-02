from django import forms
from MainApp.models import LANG_CHOICES, PUBLIC_CHOICES
from django.contrib.auth.models import User
from MainApp.models import Snippet


class SnippetForm(forms.Form):
    name = forms.CharField(
        label="Название сниппета", #
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Краткое название'}),
    )

    lang = forms.ChoiceField(
        label="Язык программирования",
        choices=LANG_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    code = forms.CharField(
        label="Исходный код",
        max_length=5000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Введите ваш код здесь'})
    )
    description = forms.CharField(
        label="Пояснение",
        max_length=1000,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Введите пояснение'})
    )
    public = forms.ChoiceField(
        label="Видимость Сниппита", #
        choices=PUBLIC_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 5:
            raise forms.ValidationError("name must be 5 or more letters!")
        return name
    # Пример валидации на уровне формы (опционально)
    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        description = cleaned_data.get('description')

        if code and len(code) < 10 and not description:
            # Если код очень короткий, а описание отсутствует, добавить ошибку
            self.add_error(None, "Для очень короткого кода требуется описание.")  # Общая ошибка формы
        return cleaned_data



# class SnippetForm(forms.ModelForm):
#     class Meta:
#         model = Snippet
#         fields = ['name', 'lang', 'code']
#         # widgets = {
#         #     'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Краткое название'}),
#         #     'lang': forms.Select(attrs={'class': 'form-control'}),
#         #     'code': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Введите ваш код здесь'}),
#         # }
#         labels = {
#             'name': 'Название сниппета',
#             'lang': 'Язык программирования',
#             'code': 'Исходный код',
#         }

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email'}),
        }

    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'password'}
    ))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'confirm password'}
    ))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 == password2:
            return password2
        raise forms.ValidationError("Пароли пустые или не совпадают")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user