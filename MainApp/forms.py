from django import forms
from MainApp.models import LANG_CHOICES

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