from django.contrib.auth.models import User
from MainApp.factories import UserFactory, SnippetFactory, TagFactory
import pytest

from MainApp.models import Tag, Snippet


# pytest -v MainApp/test_factory.py
# python manage.py shell_plus --ipython

@pytest.mark.django_db
def test_task1():
    user = UserFactory(username='Alice')

    # assert User.objects.get(id) == 1
    assert User.objects.get(id=user.id).username == 'Alice'


@pytest.mark.django_db
def test_create_tags():
    # Создаем теги
    tags = TagFactory.create_batch(5)

    assert Tag.objects.all().count() == 5


@pytest.mark.django_db
def test_create_snippet():
    # Создаем сниппет
    SnippetFactory(name='Java Quick Sort', lang='java')

    assert Snippet.objects.get(name='Java Quick Sort').lang == 'java'

@pytest.mark.django_db
def test_create_snippet_privat():
    user = UserFactory()
    SnippetFactory.create_batch(3, user=user, public=False)

    snippets = Snippet.objects.all()

    for snippet in snippets:
        assert snippet.user == user
        assert snippet.public is False
    assert snippets.count() == 3