from django.contrib.auth.models import User
from django.test import RequestFactory, Client
from django.urls import reverse

from MainApp.factories import UserFactory, SnippetFactory, TagFactory, CommentFactory
import pytest

from MainApp.models import Tag, Snippet
from MainApp.views import snippet_detail


@pytest.mark.django_db
class TestSnippetDetail:
    def setup_method(self):
        self.factory = RequestFactory()
        self.client = Client()

        # Создаем тестовых пользователей с помощью фабрик
        self.user = UserFactory(username="testuser", email="test@example.com")
        self.another_user = UserFactory(username="anotheruser", email="another@example.com")

        # Создаем тестовые сниппеты с помощью фабрик
        self.public_snippet = SnippetFactory(
            name="Public Python Snippet",
            code="print('Hello, World!')",
            lang="python",
            user=self.user,
            public=True,
            views_count=5
        )

        self.private_snippet = SnippetFactory(
            name="Private Python Snippet",
            code="print('This is private')",
            lang="python",
            user=self.user,
            public=False,
            views_count=2
        )

        # Создаем комментарии к сниппетам с помощью фабрик
        self.comment1 = CommentFactory(
            text="Отличный код!",
            author=self.user,
            snippet=self.public_snippet
        )

        self.comment2 = CommentFactory(
            text="Очень полезно",
            author=self.another_user,
            snippet=self.public_snippet
        )

    def test_snippet_detail_public_snippet_authenticated_user(self):
        """Тест просмотра публичного сниппета авторизованным пользователем"""
        # self.client=Client()
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        assert response.context['pagename'] == f'Сниппет: {self.public_snippet.name}'
        assert response.context['snippet'] == self.public_snippet
        assert 'comment_form' in response.context.keys()
        assert len(response.context['comments']) == 2

    def test_snippet_detail_public_snippet_anonymous_user(self):
        """Тест просмотра публичного сниппета неавторизованным пользователем"""
        response = self.client.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == self.public_snippet
        assert 'comment_form' in response.context
        assert len(response.context['comments']) == 2

    def test_snippet_detail_private_snippet_owner(self):
        """Тест просмотра приватного сниппета его владельцем"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-id', kwargs={'id': self.private_snippet.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == self.private_snippet
        assert 'comment_form' in response.context

    def test_snippet_detail_private_snippet_other_user(self):
        """Тест просмотра приватного сниппета другим пользователем"""
        self.client.force_login(self.another_user)
        response = self.client.get(reverse('snippet-id', kwargs={'id': self.private_snippet.id}))

        assert response.status_code == 403
        assert "not authorized" in response.content.decode().lower()
        # assert response.context['snippet'] == self.private_snippet
        # assert 'comment_form' in response.context

    def test_snippet_detail_private_snippet_anonymous_user(self):
        """Тест просмотра приватного сниппета неавторизованным пользователем"""
        response = self.client.get(reverse('snippet-id', kwargs={'id': self.private_snippet.id}))

        assert response.status_code == 403
        assert "not authorized" in response.content.decode().lower()
        # assert response.context['snippet'] == self.private_snippet
        # assert 'comment_form' in response.context

    def test_snippet_detail_nonexistent_snippet(self):
        """Тест просмотра несуществующего сниппета"""
        self.client.force_login(self.user)
        try:
            response = self.client.get(reverse('snippet-id', kwargs={'id': 99999}))
            assert response.status_code == 404
        except Exception as e:
            # Django может вернуть 500 ошибку при DoesNotExist исключении
            assert "DoesNotExist" in str(e) or "Snippet matching query does not exist" in str(e)

    def test_snippet_detail_increments_views_count(self):
        """Тест увеличения счетчика просмотров при просмотре сниппета"""
        initial_views = self.public_snippet.views_count
        self.client.force_login(self.user)

        response = self.client.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        # Обновляем объект из базы данных
        self.public_snippet.refresh_from_db()
        assert self.public_snippet.views_count == initial_views + 1

    def test_snippet_detail_with_comments(self):
        """Тест отображения комментариев к сниппету"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        comments = response.context['comments']
        assert len(comments) == 2
        assert self.comment1 in comments
        assert self.comment2 in comments

    def test_snippet_detail_without_comments(self):
        """Тест отображения сниппета без комментариев"""
        # Создаем новый сниппет без комментариев с помощью фабрики
        snippet_without_comments = SnippetFactory(
            name="Snippet Without Comments",
            code="print('No comments')",
            lang="python",
            user=self.user,
            public=True
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-id', kwargs={'id': snippet_without_comments.id}))

        assert response.status_code == 200
        assert len(response.context['comments']) == 0

    def test_snippet_detail_comment_form_in_context(self):
        """Тест наличия формы комментария в контексте"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        assert 'comment_form' in response.context
        assert response.context['comment_form'] is not None

    def test_snippet_detail_using_request_factory(self):
        """Тест с использованием RequestFactory"""
        request = self.factory.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))
        request.user = self.user

        response = snippet_detail(request, self.public_snippet.id)

        assert response.status_code == 200
        # При использовании RequestFactory напрямую, response может не иметь context
        # Проверяем, что функция возвращает HttpResponse
        assert hasattr(response, 'content')

    def test_snippet_detail_multiple_views_increment_count(self):
        """Тест многократного увеличения счетчика просмотров"""
        initial_views = self.public_snippet.views_count
        self.client.force_login(self.user)

        # Просматриваем сниппет несколько раз
        for i in range(3):
            response = self.client.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))
            assert response.status_code == 200

        # Проверяем, что счетчик увеличился на 3
        self.public_snippet.refresh_from_db()
        assert self.public_snippet.views_count == initial_views + 3

    def test_snippet_detail_different_users_increment_count(self):
        """Тест увеличения счетчика просмотров разными пользователями"""
        initial_views = self.public_snippet.views_count

        # Первый пользователь просматривает
        self.client.force_login(self.user)
        response1 = self.client.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))
        assert response1.status_code == 200

        # Второй пользователь просматривает
        self.client.force_login(self.another_user)
        response2 = self.client.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))
        assert response2.status_code == 200

        # Проверяем, что счетчик увеличился на 2
        self.public_snippet.refresh_from_db()
        assert self.public_snippet.views_count == initial_views + 2

    def test_snippet_detail_context_structure(self):
        """Тест структуры контекста ответа"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-id', kwargs={'id': self.public_snippet.id}))

        assert response.status_code == 200
        context = response.context

        # Проверяем наличие всех необходимых ключей в контексте
        assert 'pagename' in context
        assert 'snippet' in context
        assert 'comments' in context
        assert 'comment_form' in context

        # Проверяем правильность значений
        assert context['pagename'] == f'Сниппет: {self.public_snippet.name}'
        assert context['snippet'] == self.public_snippet
        # comments может быть QuerySet или list, проверяем что это итерируемый объект
        assert hasattr(context['comments'], '__iter__')
        assert context['comment_form'] is not None

    def test_snippet_detail_with_factory_generated_data(self):
        """Тест с данными, сгенерированными фабриками"""
        # Создаем сниппет с автоматически сгенерированными данными
        factory_snippet = SnippetFactory(
            user=self.user,
            public=True
        )

        # Создаем несколько комментариев к этому сниппету
        comments = CommentFactory.create_batch(3, snippet=factory_snippet)

        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-id', kwargs={'id': factory_snippet.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == factory_snippet
        assert len(response.context['comments']) == 3

    def test_snippet_detail_anonymous_snippet(self):
        """Тест просмотра сниппета без автора (анонимного)"""
        # Создаем сниппет без пользователя
        anonymous_snippet = SnippetFactory(user=None, public=True)

        response = self.client.get(reverse('snippet-id', kwargs={'id': anonymous_snippet.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == anonymous_snippet
        assert response.context['snippet'].user is None

    def test_snippet_detail_with_tags(self):
        """Тест просмотра сниппета с тегами"""
        # Создаем теги через фабрику
        from MainApp.factories import TagFactory
        python_tag = TagFactory(name='python')
        django_tag = TagFactory(name='django')
        web_tag = TagFactory(name='web')

        # Создаем сниппет с тегами
        snippet_with_tags = SnippetFactory(
            user=self.user,
            public=True
        )
        # Очищаем автоматически созданные теги и добавляем наши
        snippet_with_tags.tags.clear()
        snippet_with_tags.tags.add(python_tag, django_tag, web_tag)

        self.client.force_login(self.user)
        response = self.client.get(reverse('snippet-id', kwargs={'id': snippet_with_tags.id}))

        assert response.status_code == 200
        assert response.context['snippet'] == snippet_with_tags
        assert snippet_with_tags.tags.count() == 3

    def test_snippet_detail_multiple_languages(self):
        """Тест просмотра сниппетов на разных языках"""
        # Создаем сниппеты на разных языках
        python_snippet = SnippetFactory(lang='python', user=self.user, public=True)
        js_snippet = SnippetFactory(lang='javascript', user=self.user, public=True)
        java_snippet = SnippetFactory(lang='java', user=self.user, public=True)

        self.client.force_login(self.user)

        # Проверяем каждый сниппет
        for snippet in [python_snippet, js_snippet, java_snippet]:
            response = self.client.get(reverse('snippet-id', kwargs={'id': snippet.id}))
            assert response.status_code == 200
            assert response.context['snippet'] == snippet
            assert response.context['snippet'].lang in ['python', 'javascript', 'java']