from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='author')


@pytest.fixture
def another_user(django_user_model):
    return django_user_model.objects.create(username='another user')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def another_user_client(another_user):
    client = Client()
    client.force_login(another_user)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='title',
        text='news text',
    )


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture
def news_url(news):
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='comment text'
    )


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def create_news():
    news_list = [
        News(title=f'News {index}',
             text='text',
             date=datetime.today() - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def create_comments(another_user, news):
    for index in range(7):
        comment = Comment.objects.create(
            news=news, author=another_user, text=f'text{index}'
        )
        comment.creates = timezone.now() + timedelta(days=index)
        comment.save()


@pytest.fixture
def edit_comment_form():
    return {
        'text': 'new comment text'
    }
