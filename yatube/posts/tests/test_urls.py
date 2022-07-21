from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class FirstAccess(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='auth2')
        # cls.author = User.objects.get(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа123',
            slug='testslug',
            description='Тестовое описание123',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая пост 1',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        self.urls_template = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.author,)),
            ('posts:post_detail', (self.post.id,)),
            ('posts:post_create', None),
            ('posts:post_edit', (self.post.id,))
        )
        cache.clear()

    def test_guest_access(self):
        """Доступность для гостя."""
        for address, args in self.urls_template:
            with self.subTest(address=address):
                reverse_list = ['posts:post_create', 'posts:post_edit']
                if address in reverse_list:
                    response = self.client.get(
                        reverse(address, args=args), follow=True
                    )
                    rev_login = reverse('users:login')
                    rev_name = reverse(address, args=args)
                    self.assertRedirects(
                        response, f'{rev_login}?next={rev_name}'
                    )
                else:
                    response = self.client.get(reverse(address, args=args))
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user_access(self):
        """Доступность для пользователя."""
        for address, args in self.urls_template:
            with self.subTest(address=address):
                response = self.authorized_client.get(
                    reverse(address, args=args)
                )
                if address != 'posts:post_edit':
                    self.assertEqual(response.status_code, HTTPStatus.OK)
                else:
                    rev_detail = reverse(
                        'posts:post_detail', args=(self.post.id,)
                    )
                    self.assertRedirects(response, rev_detail)

    def test_author_access(self):
        """Доступность для автора."""
        for address, args in self.urls_template:
            with self.subTest(address=address):
                response = self.authorized_author.get(
                    reverse(address, args=args)
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_guest_fakepage(self):
        """Ответ 404 на несуществующую страницу"""
        response = self.client.get('/fakepage/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_correct_templates(self):
        """Проверка корректности шаблонов"""
        templates_urls = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list', (self.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (self.author,), 'posts/profile.html'),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:post_edit', (self.post.id,), 'posts/create_post.html')
        )
        for address, args, template in templates_urls:
            with self.subTest(address=address):
                response = self.authorized_author.get(
                    reverse(address, args=args)
                )
                self.assertTemplateUsed(response, template)

    def test_reverse_urls_correct(self):
        """Корректность реверса"""
        reverse_urls = (
            ('posts:index', None, '/'),
            ('posts:group_list', (self.group.slug,), (f'/group/'
                                                      f'{self.group.slug}/')),
            ('posts:profile', (self.author,), f'/profile/{self.author}/'),
            ('posts:post_detail', (self.post.id,), f'/posts/{self.post.id}/'),
            ('posts:post_create', None, '/create/'),
            ('posts:post_edit', (self.post.id,), f'/posts/'
                                                 f'{self.post.id}/edit/')
        )
        for address, args, links in reverse_urls:
            with self.subTest(address=address):
                self.assertEqual(reverse(address, args=args), links)
