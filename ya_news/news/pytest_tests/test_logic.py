from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import (
    assertFormError,
    assertRedirects
)

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    edit_comment_form, client,
    news_url
):
    """Anonymous user can't leave a comment."""
    client.post(news_url, data=edit_comment_form)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(
    edit_comment_form,
    another_user,
    another_user_client,
    news_url,
    news
):
    """Authorised user can leave a comment."""
    another_user_client.post(news_url, data=edit_comment_form)
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == edit_comment_form['text']
    assert comment.news == news
    assert comment.author == another_user


@pytest.mark.django_db
@pytest.mark.parametrize(
    'word', (BAD_WORDS)
)
def test_user_cant_use_bad_words(news_url, another_user_client, word):
    """User can't leave a comment with forbidden word."""
    bad_word_form = {'text': f'text with {word}'}
    response = another_user_client.post(news_url, data=bad_word_form)
    assertFormError(response, form='form', field='text', errors=WARNING)
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, comment_id, news_url):
    """User can delete his comment."""
    url = reverse('news:delete', args=comment_id)
    response = author_client.delete(url)
    assertRedirects(response, news_url + '#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(
    another_user_client,
    comment_id
):
    """User can't delete someone else's comment."""
    url = reverse('news:delete', args=comment_id)
    response = another_user_client.delete(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(
    author_client,
    edit_comment_form,
    comment,
    news_url
):
    """User can edit his comment."""
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, data=edit_comment_form)
    assertRedirects(response, news_url + '#comments')
    comment.refresh_from_db()
    assert comment.text == edit_comment_form['text']


def test_user_cant_edit_comment_of_another_user(
    another_user_client,
    edit_comment_form,
    comment
):
    """User can't edit someone else's comment."""
    url = reverse('news:edit', args=(comment.id,))
    old_text = comment.text
    response = another_user_client.post(url, data=edit_comment_form)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
