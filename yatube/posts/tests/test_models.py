from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Post, Group

User = get_user_model()


class TaskModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='UserName',
                                            email='user@yandex.ru',
                                            password='password',),
            text='Тестовая запись для создания нового поста'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_object_name_is_title_fild(self):
        post = TaskModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_group_object_name(self):
        group = TaskModelTest.group

        expected_group_str = group.title

        self.assertEqual(expected_group_str, str(group))
