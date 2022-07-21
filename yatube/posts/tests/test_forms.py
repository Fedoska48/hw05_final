import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая пост1234',
            group=cls.group,
        )


    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        # uploaded = SimpleUploadedFile(
        #     name='small.gif',
        #     content=self.small_gif,
        #     content_type='image/gif'
        # )

    def test_create_form(self):
        """Тест формы создания поста."""
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'New comment',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    args=(self.author.username,)))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.author)


    def test_edit_form(self):
        self.group_2 = Group.objects.create(
            title='Тестовое название2',
            description='Тестовое описание2',
            slug='test-slug2',
        )
        post_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        edit_form_data = {
            'text': 'Исправленный пост',
            'group': self.group_2.id,
            'image': uploaded,
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=edit_form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    kwargs={'post_id': post.id}))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(post.text, edit_form_data['text'])
        self.assertEqual(post.group, self.group_2)
        self.assertEqual(post.author, self.author)
        response = self.authorized_author.post(
            reverse('posts:group_list', args=(self.group.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context['page_obj']), settings.ZERO)
        self.assertEqual(post.uploaded, self.uploaded)

    def test_anonymous_create_post(self):
        """Создание поста анонимом."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'New post ANON',
            'group': self.group.id,
        }
        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )
        self.assertNotEqual(post.text, form_data['text'])
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), post_count)


class CommentFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая пост1234',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_comment_form(self):
        """Тест формы создания комментария."""
        comm_count = Post.comments.objects.count()
        form_data = {
            'text': 'New comment',
        }
        response = self.authorized_author.post(
            reverse('posts:post_detail'),
            data=form_data,
            follow=True
        )
        post_comm = Post.comments.objects.first()
        self.assertRedirects(
            response,
            reverse('posts:post_detail',
                    args=(self.post.id,)))
        self.assertEqual(Post.comments.objects.count(), comm_count + 1)
        self.assertEqual(post_comm.text, form_data['text'])
