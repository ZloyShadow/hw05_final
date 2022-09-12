from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        labels = {'group': 'Группа', 'text': 'Сообщение',
                  'image': 'Изображение'}
        help_texts = {'group': 'Выберите группу', 'text': 'Введите ссообщение',
                      'image': 'Выберите изображние'}
        fields = ["group", "text", "image"]
