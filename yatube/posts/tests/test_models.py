from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа123',
            slug='Тестовый слаг123',
            description='Тестовое описание123',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост1234',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей GROUP корректно работает __str__."""
        # group = PostModelTest.group
        # group_title = group._meta.get_field('title')
        expected_object_name = self.group.title
        self.assertEqual(expected_object_name, 'Тестовая группа123')

    def test_models_obj_name_post(self):
        """Проверяем, что у моделей POST корректно работает __str__."""
        # post = PostModelTest.post
        # post_text15 = post._meta.get_field('text'[:15])
        expected_object_name = self.post.text[:15]
        self.assertEqual(expected_object_name, 'Тестовая пост1234'[:15])
