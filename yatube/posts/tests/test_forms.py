import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post
from posts.models import Comment


User = get_user_model()


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-descrp',
        )
        cls.post = Post.objects.create(
            text='test-text',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        text = 'Testtext'
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': text,
            'group': self.group.pk,
            'author': self.user.username,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(
            Post.objects.order_by('id').last().text,
            form_data['text']
        )
        self.assertEqual(
            Post.objects.order_by('id').last().author.username,
            form_data['author']
        )
        self.assertEqual(
            Post.objects.order_by('id').last().group.pk,
            form_data['group']
        )

    def test_edit_post(self):
        edited_post = 'Исправленный текст'
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}
            ),
            data={'text': edited_post},
            follow=True
        )
        test_post = Post.objects.get(id=f'{self.post.pk}')
        self.assertEqual(test_post.text, edited_post)
        self.assertEqual(test_post.author_id, self.user.pk)
        self.assertEqual(test_post.group_id, None)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.pk}'})
        )

    def test_creat_post_anonymous(self):
        """Создание поста анонимным пользователем"""
        posts_count = Post.objects.count()
        response = self.client.post(
            reverse('posts:post_create'),
            follow=True)
        self.assertNotEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_post_edit_anonymous(self):
        """Редактирование поста анонимным пользователем"""
        edited_post = 'Исправленный текст анонимом'
        response = self.client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.pk}'}
            ),
            data={'text': edited_post},
            follow=True
        )
        self.assertNotEqual(self.post.text, edited_post)
        self.assertRedirects(
            response, (
                f'/auth/login/?next=/posts/{self.post.pk}/edit/')
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-descrp',
        )
        cls.post = Post.objects.create(
            text='test-text',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='test-comment',
        )
        cls.form = CommentForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_comment(self):
        comments_count = Comment.objects.count()
        text = 'Testcomment'
        form_data = {
            'text': text,
        }
        post = self.post.id
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': f'{post}'}
            ),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': f'{post}'})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=text,
            ).exists()
        )
