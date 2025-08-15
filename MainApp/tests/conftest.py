from MainApp.models import Snippet, Comment, Tag
from MainApp.factories import UserFactory, SnippetFactory, CommentFactory, TagFactory
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


# Фикстура для настройки и очистки драйвера браузера
@pytest.fixture(scope="session")
def browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

# TEST COVE
# pip install pytest-cov
# p


@pytest.fixture
def tag_factory():
    def _create_tags(names:list[str]):
        tags = []
        for name in names:
            tags.append(TagFactory(name=name))
        return tags
    return _create_tags

@pytest.fixture
def comment_factory():
    def _create_comments(snippet, num):
        # comments = []
        # for n in range(num):
        #     comment = CommentFactory(
        #         text=f'Тестовый комментарий #{n + 1}',
        #         snippet=snippet
        #     )
        #     comments.append(comment)
        # return comments
        return CommentFactory.create_batch(num, snippet=snippet)
    return _create_comments