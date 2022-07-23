from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..forms import PostForm
from ..models import Group, Post, Follow
from yatube import settings

User = get_user_model()


class CorrectTemplateTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.get(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа123',
            slug='test-slug',
            description='Тестовое описание123',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая пост 1',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)
        cache.clear()

    def check_func(self, response, bol=False):
        """Вспомогательная функция для проверки корректного контекста"""
        if bol:
            post = response.context.get('post')
        else:
            post = response.context['page_obj'][0]
        self.assertEqual(post.text, self.post.text)
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.pub_date, self.post.pub_date)
        self.assertEqual(post.image, self.post.image)
        self.assertContains(response, '<img')

    def test_index_pages_show_correct_context(self):
        """Проверка контекста в index"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.check_func(response)

    def test_group_list_pages_show_correct_context(self):
        """Проверка контекста в group_list"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,))
        )
        self.check_func(response)
        group_context = response.context['group']
        self.assertEqual(group_context, self.group)

    def test_profile_pages_show_correct_context(self):
        """Проверка контекста в profile"""
        response = self.authorized_client.get(reverse(
            'posts:profile', args=(self.user.username,))
        )
        self.check_func(response)
        group_context = response.context['author']
        self.assertEqual(group_context, self.author)

    def test_post_detail_pages_show_correct_context(self):
        """Проверка контекста в post_detail"""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', args=(self.post.id,))
        )
        self.check_func(response, True)

    def test_post_for_follow(self):
        """Новая запись в index follow """
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.check_func(response)

    def test_create_edit_both_context(self):
        """Проверка контекста в create и edit"""
        context_urls = (
            ('posts:post_create', None),
            ('posts:post_edit', (self.post.id,))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for address, args in context_urls:
            with self.subTest(address=address):
                response = self.authorized_author.get(
                    reverse(address, args=args)
                )
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context.get('form'), PostForm)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get('form').fields.get(
                            value
                        )
                        self.assertIsInstance(form_field, expected)

    def test_post_correct_group(self):
        """Проверка что пост попадает в корректную группу."""
        post_count = Post.objects.count()
        post1 = Post.objects.create(
            author=self.author,
            text='Тестовая пост 1',
            group=self.group
        )
        group2 = Group.objects.create(
            title='Тестовая группа NEW',
            slug='test-slug-new',
            description='Тестовое описание NEW',
        )
        response1 = self.authorized_client.get(reverse(
            'posts:group_list', args=(group2.slug,))
        )
        response2 = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,))
        )
        self.assertEqual(len(response1.context['page_obj']), settings.ZERO)
        self.assertEqual(post1.group, self.group)
        self.assertEqual(len(response2.context['page_obj']), post_count + 1)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.get(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа123',
            slug='test-slug',
            description='Тестовое описание123',
        )
        cls.posts = [
            Post(
                text=f'Тестовый пост {number_post}',
                author=cls.user,
                group=cls.group,
            )
            for number_post in range(settings.SORT13)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_pagin_new(self):
        """Проверка пагинации"""
        pagin_urls = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user.username,))
        )
        pages_units = (
            ('?page=1', settings.SORT10),
            ('?page=2', settings.SORT13 - settings.SORT10)
        )

        for address, args in pagin_urls:
            with self.subTest(address=address):
                for page, units in pages_units:
                    with self.subTest(page=page):
                        response = self.authorized_author.get(
                            reverse(address, args=args) + page
                        )
        self.assertEqual(len(response.context['page_obj']), units)


class CommentFollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.follower = User.objects.create_user(username='follower')
        cls.following = User.objects.create_user(username='following')
        cls.post = Post.objects.create(
            author=cls.following,
            text='Тестируем подписки',
        )

    def setUp(self):
        self.authorized_follower_client = Client()
        self.authorized_follower_client.force_login(self.follower)
        self.authorized_following_client = Client()
        self.authorized_following_client.force_login(self.following)

    def test_follow(self):
        """Тестирование подписки"""
        follow_count = Follow.objects.count()
        self.authorized_follower_client.get(
            reverse(
                'posts:profile_follow',
                args=(self.following,)
            )
        )
        follow_count2 = Follow.objects.count()
        self.assertEqual(follow_count + 1, follow_count2)

    def test_unfollow(self):
        """Тестирование отписки"""
        Follow.objects.create(user=self.follower, author=self.following)
        follow_count = Follow.objects.count()
        self.authorized_follower_client.get(
            reverse(
                'posts:profile_unfollow',
                args=(self.following,)
            )
        )
        follow_count2 = Follow.objects.count()
        self.assertEqual(follow_count - 1, follow_count2)

    def test_follow_self(self):
        """Тестирование подписки на самого себя"""
        follow_count = Follow.objects.count()
        self.authorized_follower_client.get(
            reverse(
                'posts:profile_follow',
                args=(self.follower,)
            )
        )
        follow_count2 = Follow.objects.count()
        self.assertEqual(follow_count, follow_count2)

    def test_no_post_for_unfollow(self):
        """Нового поста нет у того, кто не подписан"""
        response = self.authorized_follower_client.get(
            reverse('posts:follow_index')
        )
        content = response.context['page_obj']
        self.assertNotIn(self.post, content)
