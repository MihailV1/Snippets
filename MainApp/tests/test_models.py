from django.db import transaction
from django.contrib.auth.models import User
import pytest

from MainApp.models import Snippet, Tag, Comment
from django.test import TestCase

#  pytest -v   pytest -m pytest

@pytest.mark.django_db
class TestSnippetModel:
    def test_create_snippet(self):
        """тест для создания нового сниппета"""
        snippet = Snippet.objects.create(
            name = "Test Snippet",
            lang= "python",
            code = "print('Hello World!')",
        )
        assert snippet.name == "Test Snippet"
        assert snippet.lang == "python"
        assert snippet.code == "print('Hello World!')"
        assert snippet.public is True
        assert snippet.user is None


@pytest.mark.django_db
class TestTagModel:
    """Тесты для модели Tag"""

    def test_tag_creation(self):
        """Тест создания тега"""
        tag = Tag.objects.create(name="Python")
        assert tag.name == "Python"

    def test_duplicate_tag_names_not_allowed(self):
        """Тест, что теги с одинаковыми именами недопустимы"""
        from django.db import IntegrityError

        # Создаем первый тег
        tag1 = Tag.objects.create(name="Python")

        # Пытаемся создать второй тег с тем же именем
        # Должно возникнуть исключение IntegrityError
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Tag.objects.create(name="Python")

        # Проверяем, что в базе данных остался только один тег с именем "Python"
        assert Tag.objects.filter(name="Python").count() == 1
        assert Tag.objects.get(name="Python") == tag1

@pytest.mark.django_db
class TestCommentModel:
    """Тесты для модели Comment"""

    def test_comment_creation(self):
        """Тест создания комментария"""
        # Создаем пользователя
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        # Создаем сниппет
        snippet = Snippet.objects.create(
            name="Test Snippet",
            lang="python",
            code="print('Hello World!')"
        )

        # Создаем комментарий
        comment = Comment.objects.create(
            text="Это тестовый комментарий",
            author=user,
            snippet=snippet
        )

        # Проверяем поля
        assert comment.text == "Это тестовый комментарий"
        assert comment.author == user
        assert comment.snippet == snippet
        assert comment.creation_date is not None
