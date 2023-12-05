from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='user')
        cls.author = User.objects.create(username='author')
        cls.note = Note.objects.create(title='title',
                                       slug='slug',
                                       author=cls.author)

    def test_notes_list_for_different_users(self):
        url = reverse('notes:list')
        users = (
            (self.user, False), (self.author, True)
        )
        for user, note_in_list in users:
            self.client.force_login(user)
            with self.subTest():
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, note_in_list)

    def test_pages_contains_form(self):
        names = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None)
        )
        for name, args in names:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
