from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post
from django.urls import reverse

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserName')
        cls.user_not_author = User.objects.create_user(
            username='test_user_not_author'
        )
        cls.user_author = User.objects.create_user(
            username='user_author')
        cls.another_user = User.objects.create_user(
            username='another_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='tst-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            group=cls.group,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.auth_client = Client()
        self.auth_client_not_author = Client()
        self.post_author = Client()

        self.auth_client.force_login(PostsURLTests.user)
        self.auth_client_not_author.force_login(PostsURLTests.user_not_author)

    def test_urls_exists_at_desired_location(self):
        group = PostsURLTests.group
        user = PostsURLTests.user
        post = PostsURLTests.post

        url_names = [
            '/',
            f'/group/{group.slug}/',
            f'/profile/{user.username}/',
            f'/posts/{post.pk}/',
        ]

        for address in url_names:
            with self.subTest(address=address):
                guest_response = self.guest_client.get(address, follow=True)
                auth_response = self.auth_client.get(address)

                self.assertEqual(guest_response.status_code, 200)
                self.assertEqual(auth_response.status_code, 200)

    def test_create_post_url_exists_at_desired_location(self):
        address = f'{"/create/"}'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)

        self.assertRedirects(
            guest_response,
            f'{"/auth/login/?next=/create/"}'
        )
        self.assertEqual(auth_response.status_code, 200)

    def test_404_error_return_for_unexisting_page(self):
        address = f'{"/fake/"}'

        guest_response = self.guest_client.get(address, follow=True)
        auth_response = self.auth_client.get(address)

        self.assertEqual(guest_response.status_code, 404)
        self.assertEqual(auth_response.status_code, 404)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            reverse(
                'posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.post_author.get(adress)
                self.assertTemplateUsed(response, template)
