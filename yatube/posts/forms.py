from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        help_texts = {
            'text': 'Введите текст',
            'group': 'Выберите группу из списка',
            'image': 'Вставьте изображение'
        }
        labels = {
            'text': 'Текст публикации',
            'group': 'Группа публикации',
            'image': 'Изображение'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Введите текст комментария'
        }
        labels = {
            'text': 'Комментарий'
        }
