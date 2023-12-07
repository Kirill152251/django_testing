import pytest
from django.conf import settings as st
from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.usefixtures('create_news')
def test_news_count(client):
    """Home page availability."""
    response = client.get(reverse('news:home'))
    assert 'object_list' in response.context
    assert len(response.context['object_list']) == st.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('create_news')
def test_news_order(client):
    """News order on home page - from newest to oldest."""
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    assert 'object_list' in response.context
    dates = [news.date for news in object_list]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


@pytest.mark.usefixtures('create_comments')
def test_comment_order(client, news_url):
    """Comments chronological order."""
    response = client.get(news_url)
    assert 'news' in response.context
    comments = response.context['news'].comment_set.all()
    comments_dates = [comment.created for comment in comments]
    sorted_comment = sorted(comments_dates)
    assert comments_dates == sorted_comment


@pytest.mark.django_db
@pytest.mark.parametrize(
    'users_client, expected_result',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('another_user_client'), True),
    ),
)
def test_comment_form_availability(users_client, expected_result, news_url):
    """Comment form availability for anonymous and authorised user."""
    response = users_client.get(news_url)
    result = 'form' in response.context
    if result:
        assert isinstance(response.context['form'], CommentForm)
    assert result == expected_result
