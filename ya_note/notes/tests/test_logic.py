from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()


class TestNoteCreation(TestCase):

    NOTE_DATA = {
        'title': 'new-title',
        'text': 'new-text',
        'slug': 'new-slug'
    }

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='username')
        cls.create_note_url = reverse('notes:add')

    def test_user_can_create_note(self):
        self.client.force_login(self.user)
        response = self.client.post(self.create_note_url, self.NOTE_DATA)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.NOTE_DATA['title'])
        self.assertEqual(new_note.text, self.NOTE_DATA['text'])
        self.assertEqual(new_note.slug, self.NOTE_DATA['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.create_note_url, self.NOTE_DATA)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.create_note_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_unique_slug(self):
        self.client.force_login(self.user)
        Note.objects.create(title='test',
                            text='test text',
                            author=self.user,
                            slug=self.NOTE_DATA['slug'])

        response = self.client.post(self.create_note_url, self.NOTE_DATA)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.NOTE_DATA['slug'] + WARNING))
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        self.client.force_login(self.user)
        without_slug = self.NOTE_DATA.copy()
        without_slug.pop('slug')

        response = self.client.post(self.create_note_url, without_slug)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, slugify(self.NOTE_DATA['title']))


class TestNoteDeleteEdit(TestCase):

    NOTE_TEXT = 'text'
    FORM = {
        'title': 'new title',
        'text': 'new text',
        'slug': 'new-slug'
    }

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.author_note = Note.objects.create(title='author note',
                                              slug='slug',
                                              author=cls.author,
                                              text=cls.NOTE_TEXT)
        cls.another_user = User.objects.create(username='user')
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)
        cls.another_user_note = Note.objects.create(title='another user note',
                                                    slug='slugg',
                                                    author=cls.another_user,
                                                    text='text')

    def test_delete_note(self):
        test_data = (
            (self.author_note, False),
            (self.another_user_note, True),
        )
        for note, result in test_data:
            with self.subTest(name=note.title):
                url = reverse('notes:delete', args=(note.slug,))
                self.author_client.delete(url)
                self.assertEqual(note in Note.objects.all(), result)

    def test_edit_note(self):
        test_data = (
            (self.author_note, True),
            (self.another_user_note, False),
        )
        for note, result in test_data:
            with self.subTest(name=note.title):
                url = reverse('notes:edit', args=(note.slug,))
                self.author_client.post(url, data=self.FORM)
                note.refresh_from_db()
                self.assertEqual(note.text == self.FORM['text'], result)
                self.assertEqual(note.title == self.FORM['title'], result)
                self.assertEqual(note.slug == self.FORM['slug'], result)
