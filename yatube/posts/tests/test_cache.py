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
        cache_response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        cache_response2 = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(cache_response.content, cache_response2.content)
        cache.clear()
        response_cleared = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(
            cache_response,
            response_cleared
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
