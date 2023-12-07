from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Title',
            slug='slug',
            author=cls.author
        )
        cls.slug = (cls.note.slug,)

    def test_main_page_availability(self):
        """Home page availability."""
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_done_add_notes_pages_availability_for_login_user(self):
        """Notes pages availability for registered user."""
        urls = ('notes:list', 'notes:success', 'notes:add')
        for url in urls:
            with self.subTest(name=url):
                response = self.author_client.get(reverse(url))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_notes_delete_edit_availability(self):
        """Note edit/delete availability for author and reader."""
        users_statuses = (
            (self.author_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND)
        )
        for client, status in users_statuses:
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(name=name):
                    url = reverse(name, args=self.slug)
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Redirect for anonymous user."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None), ('notes:success', None),
            ('notes:add', None), ('notes:detail', self.slug),
            ('notes:edit', self.slug), ('notes:delete', self.slug),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_login_logout_sighup_pages_availability(self):
        """Login/Logout/Sighup pages availability."""
        test_data = (
            (self.author_client, 'users:login'),
            (self.client, 'users:login'),
            (self.author_client, 'users:logout'),
            (self.client, 'users:logout'),
            (self.author_client, 'users:signup'),
            (self.client, 'users:signup'),
        )
        for client, name in test_data:
            with self.subTest():
                url = reverse(name)
                response = client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
