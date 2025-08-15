import pytest
from django.http import Http404
from django.template.context_processors import request
from django.test import Client, RequestFactory
from django.urls import reverse
from MainApp.views import index_page
from MainApp.models import Snippet, Tag, Comment
from MainApp.views import snippet_delete
from django.contrib.auth.models import User
#  pytest -v MainApp\test_views.py

@pytest.mark.django_db
class TestIndexPage:
    def test_main_page_client(self):
        client = Client()
        response = client.get(reverse('home'))

        assert response.status_code == 200
        assert 'Добро пожаловать' in response.content.decode()
        assert response.context.get('pagename') == 'PythonBin'

    def test_main_page_factory(self):
        factory = RequestFactory()
        request = factory.get(reverse('home'))
        response = index_page(request)

        assert response.status_code == 200
        assert 'Добро пожаловать' in response.content.decode()


 # pytest -v MainApp\test_views.py::TestSnippetDelete

@pytest.mark.django_db
class TestSnippetDelete:
    def setup_method(self):
        self.factory = RequestFactory()

        # Очищаем базу данных от предыдущих тестов
        # User.objects.all().delete()
        # Snippet.objects.all().delete()

        # # Создаем пользователей с уникальными именами
        # self.user = User.objects.create_user(
        #         username='testuser_delete',
        #         email='test@example.com',
        #         password='testpass'
        #     )
        # self.other_user = User.objects.create_user(
        #         username='otheruser_delete',
        #         email='other@example.com',
        #         password='otherpass'
        #     )

        # # Создаем тестовый сниппет
        # self.snippet = Snippet.objects.create(
        #     name='Test Snippet',
        #     lang='python',
        #     code='print("Hello")',
        #     user=self.user
        # )

    @pytest.mark.skip(reason="Тест не закончен")
    def test_delete_snippet_incorrect_id(self):
        Snippet.objects.create(
            name = "Test Snippet",
            lang= "python",
            code = "print('Hello World!')",
            public=True,
        )
        request = self.factory.get(reverse('snippet-delete', kwargs={'id': 9}))#snippet.pk
        with pytest.raises(Http404):
            response = snippet_delete(request, 9)

        assert response.status_code == 404
        assert Snippet.objects.count() == 1

    @pytest.mark.skip(reason="Тест не закончен")
    def test_delete_snippet(self):
        Snippet.objects.create(
            name = "Test Snippet",
            lang= "python",
            code = "print('Hello World!')",
            public=True,
        )
        request = self.factory.get(reverse('snippet-delete', kwargs={'id': 1}))  # snippet.pk

        response = snippet_delete(request, 9)
        assert response.status_code == 302
        assert Snippet.objects.count() == 0

    # def test_get_owner_confirmation_page(self):
    #     """Владелец должен получить страницу подтверждения удаления"""
    #     request = self.factory.get(reverse('snippet-delete', args=[self.snippet.id]))
    #     request.user = self.user
    #     response = snippet_delete(request, self.snippet.id)
    #
    #     assert response.status_code == 200
    #     assert 'Удаление сниппета' in response.content.decode()
    #     assert self.snippet.name in response.content.decode()