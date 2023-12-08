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
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.create_note_url = reverse('notes:add')

    def test_user_can_create_note(self):
        """User can create note."""
        Note.objects.all().delete()
        response = self.user_client.post(self.create_note_url, self.NOTE_DATA)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.NOTE_DATA['title'])
        self.assertEqual(new_note.text, self.NOTE_DATA['text'])
        self.assertEqual(new_note.slug, self.NOTE_DATA['slug'])
        self.assertEqual(new_note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        """Anonymous user can't create note."""
        expected_note_count = Note.objects.count()
        response = self.client.post(self.create_note_url, self.NOTE_DATA)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.create_note_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), expected_note_count)

    def test_not_unique_slug(self):
        """User can't create note with existing slug."""
        Note.objects.all().delete()
        Note.objects.create(
            title='test',
            text='test text',
            author=self.user,
            slug=self.NOTE_DATA['slug']
        )
        response = self.user_client.post(self.create_note_url, self.NOTE_DATA)
        self.assertFormError(
            response, 'form', 'slug',
            errors=(self.NOTE_DATA['slug'] + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Auto forming empty slug from title."""
        Note.objects.all().delete()
        without_slug = self.NOTE_DATA.copy()
        without_slug.pop('slug')

        response = self.user_client.post(self.create_note_url, without_slug)

        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.slug, slugify(self.NOTE_DATA['title']))


class TestNoteDeleteEdit(TestCase):

    NOTE = {
        'title': 'author note',
        'text': 'small text',
        'slug': 'slug'
    }
    URL_ARG = (NOTE['slug'],)
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
        cls.note = Note.objects.create(
            title=cls.NOTE['title'],
            slug=cls.NOTE['slug'],
            author=cls.author,
            text=cls.NOTE['text']
        )
        cls.another_user = User.objects.create(username='user')
        cls.another_user_client = Client()
        cls.another_user_client.force_login(cls.another_user)
        cls.delete_url = reverse('notes:delete', args=cls.URL_ARG)
        cls.edit_url = reverse('notes:edit', args=cls.URL_ARG)

    def test_author_can_delete_his_note(self):
        """Author can delete his note."""
        expected_count = Note.objects.count() - 1
        self.author_client.delete(self.delete_url)
        self.assertEqual(Note.objects.count(), expected_count)
        self.assertNotIn(self.note, Note.objects.all())

    def test_user_cant_delete_someone_elses_post(self):
        """User cant delete someone else's post."""
        expected_count = Note.objects.count()
        self.another_user_client.delete(self.delete_url)
        self.assertEqual(Note.objects.count(), expected_count)

    def test_author_can_edit_his_note(self):
        """User can edit his note."""
        self.author_client.post(self.edit_url, data=self.FORM)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.FORM['text'])
        self.assertEqual(self.note.title, self.FORM['title'])
        self.assertEqual(self.note.slug, self.FORM['slug'])

    def test_user_cant_edit_someone_elses_note(self):
        """User can't edit someone else's note."""
        self.another_user_client.post(self.edit_url, data=self.FORM)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE['text'])
        self.assertEqual(self.note.title, self.NOTE['title'])
        self.assertEqual(self.note.slug, self.NOTE['slug'])
