from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="Код группы"
    )
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        blank=True,
        null=True,
        verbose_name="Группа"
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ('-pub_date',)

        def __str__(self):
            return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
        verbose_name="Пост"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
        verbose_name="Автор комментария"
    )
    text = models.TextField(verbose_name="Текст комментария")
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время публикации"
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name="Подписчик"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name="Автор"
    )
