from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news')),
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, news_object):
    if news_object:
        url = reverse(name, args=(news_object.id,))
    else:
        url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_comment_pages_for_author(name, author_client, comment):
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_comment_pages_for_anonymous_user(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_user_cant_change_delete_another_user_comment(
    name, another_user_client, comment
):
    url = reverse(name, args=(comment.id,))
    response = another_user_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
