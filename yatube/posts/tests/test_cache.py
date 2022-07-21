from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тевст',
            group=cls.group,
            author=cls.author
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_cache_on_index_page_exists(self):
        """Кэширование данных на главной странице существует."""
        response = self.authorized_client.get(reverse('posts:index'))
        cache_response = response.content
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:index'))
        cache_response_clear = response.content
        self.assertEqual(
            cache_response,
            cache_response_clear
        )

    def test_cache_on_index_page_updates(self):
        """Данные на странице обновляются."""
        response = self.authorized_client.get(reverse('posts:index'))
        cache_response = response.content
        cache.clear()
        Post.objects.create(
            text='Тектс',
            group=self.group,
            author=self.author
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(
            cache_response,
            response.content
        )
