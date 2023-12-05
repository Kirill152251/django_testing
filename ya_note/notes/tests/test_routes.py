from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user')
        cls.reader = User.objects.create(username='reader')
        cls.author = User.objects.create(username='author')
        cls.note = Note.objects.create(title='Title',
                                       slug='slug',
                                       author=cls.author)

    def test_main_page_availability(self):
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_done_add_notes_pages_availability_for_login_user(self):
        urls = ('notes:list', 'notes:success', 'notes:add')
        self.client.force_login(self.user)
        for url in urls:
            with self.subTest(name=url):
                response = self.client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_delete_edit_availability(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        slug = self.note.slug
        urls = (
            ('notes:list', None), ('notes:success', None),
            ('notes:add', None), ('notes:detail', (slug,)),
            ('notes:edit', (slug,)), ('notes:delete', (slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_login_logout_sighup_pages_availability(self):
        for name in ('users:login', 'users:logout', 'users:signup'):
            with self.subTest(name='name'):
                url = reverse(name)
                self.client.logout()
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

                self.client.force_login(self.user)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
