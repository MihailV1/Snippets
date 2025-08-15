from typing import List
import pytest
from MainApp.models import Snippet, Comment, Tag
from MainApp.factories import UserFactory, SnippetFactory, CommentFactory, TagFactory
import pytest


# ---> conftest.py
# @pytest.fixture
# def tag_factory():
#     def _create_tags(names:list[str]):
#         tags = []
#         for name in names:
#             tags.append(TagFactory(name=name))
#         return tags
#     return _create_tags

@pytest.mark.django_db
def test_factory_tags(tag_factory):
    tags = tag_factory(names=["js", "basic", "oop", "sdg"])

    assert Tag.objects.count() == 4
    for tag, name in zip(tags, ["js", "basic", "oop", "sdg"]):
        assert tag.name == name
    assert tags[0].name == "js"
    assert tags[1].name == "basic"


# @pytest.fixture
# def comment_factory():
#     def _create_comments(snippet, num):
#         # comments = []
#         # for n in range(num):
#         #     comment = CommentFactory(
#         #         text=f'Тестовый комментарий #{n + 1}',
#         #         snippet=snippet
#         #     )
#         #     comments.append(comment)
#         # return comments
#         return CommentFactory.create_batch(num, snippet=snippet)
#     return _create_comments

@pytest.mark.django_db
def test_factory_comments(comment_factory):
    # Добавит 6 произвольных комментариев к snippet
    snippet = SnippetFactory()
    comment_factory(snippet=snippet, num = 6)
    comments = Comment.objects.all()
    for comment in comments:
        assert comment.snippet == snippet
    assert Comment.objects.count() == 6

# Задание-3
# Создайте фабрику, которая позволяет создавать группу Сниппетов для определенного пользователя с определенным языком(lang).