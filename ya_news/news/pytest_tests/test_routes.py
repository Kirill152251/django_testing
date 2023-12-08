from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None),
    ),
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Public pages availability for anonymous user."""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name, user_client, response_code',
    (
        ('news:delete', pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        ('news:edit', pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (
            'news:delete',
            pytest.lazy_fixture('another_user_client'),
            HTTPStatus.NOT_FOUND
        ),
        (
            'news:edit',
            pytest.lazy_fixture('another_user_client'),
            HTTPStatus.NOT_FOUND
        ),
    ),
)
def test_comment_delete_edit(
    name,
    user_client,
    response_code,
    comment_id
):
    """Comment delete/edit availability for author and reader."""
    url = reverse(name, args=comment_id)
    response = user_client.get(url)
    assert response.status_code == response_code


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_comment_pages_for_anonymous_user(client, name, comment_id):
    """Comment delete/edit availability for anonymous user."""
    login_url = reverse('users:login')
    url = reverse(name, args=comment_id)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
