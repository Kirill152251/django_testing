import pytest
from django.conf import settings as st
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.usefixtures('create_news')
def test_news_count(client):
    response = client.get(reverse('news:home'))
    assert len(response.context['object_list']) == st.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.usefixtures('create_news')
def test_news_order(client):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    dates = [news.date for news in object_list]
    sorted_dates = sorted(dates, reverse=True)
    assert dates == sorted_dates


@pytest.mark.usefixtures('create_comments')
def test_comment_order(client, news_url):
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
    response = users_client.get(news_url)
    result = 'form' in response.context
    assert result == expected_result
