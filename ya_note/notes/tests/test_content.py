from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(title='title',
                                       slug='slug',
                                       author=cls.author)

    def test_notes_list_for_different_users(self):
        """User can't see another user note."""
        url = reverse('notes:list')
        users = (
            (self.user_client, False), (self.author_client, True)
        )
        for client, note_in_list in users:
            with self.subTest():
                response = client.get(url)
                self.assertIn('object_list', response.context)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, note_in_list)

    def test_pages_contains_form(self):
        """Note edit/add pages receive NoteForm."""
        names = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        )
        for name, args in names:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
