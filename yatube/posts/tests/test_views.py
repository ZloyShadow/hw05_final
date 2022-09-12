import datetime as dt
from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_no_posts = User.objects.create_user(username='UserName1')
        cls.authorized_client_no_posts = Client()
        cls.authorized_client_no_posts.force_login(cls.user_no_posts)
        cls.group_no_posts = Group.objects.create(
            title='Пустая тестовая группа',
            slug='group-no-posts'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug'
        )
        cls.posts = Post.objects.bulk_create([
            Post(
                text=f'Тестовый пост {x}',
                author=cls.user,
                group=cls.group,
                pk=x)
            for x in range(13)
        ])

    def chek_context(self, response, user, group, num):
        for i in range(num):
            for j in range(num - 1, 0):
                actual_obj = response.context['page_obj'][i]
                self.assertEqual(actual_obj.text, f'Тестовый пост {j}')
                self.assertEqual(actual_obj.author, user)
                self.assertEqual(actual_obj.group, group)
                self.assertEqual(actual_obj.pub_date, dt.date.today())

    def test_pages_uses_correct_templates(self):
        templates_pages = {
            'posts/index.html': reverse('posts:index'),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={'username': self.user.username}),
            'posts/group_list.html': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            'posts/post_detail.html': reverse(
                'posts:post_detail', kwargs={'post_id': self.posts[1].pk}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_index_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            'posts:index') + '?page=2')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), 3)

    def test_group_paginator_first_page(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_paginator_second_page(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}) + '?page=2')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), 3)

    def test_profile_paginator_first_page(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), 10)

    def test_profile_paginator_second_page(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}) + '?page=2')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self. assertEqual(len(response.context['page_obj']), 3)

    def test_index_show_correct_context(self):
        """Корректные посты на главной странице"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.chek_context(response, self.user, self.group, 13)

    def test_group_show_correct_context(self):
        """Корректные посты на странице группы"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.chek_context(response, self.user, self.group, 13)

    def test_profile_show_correct_context(self):
        """Корректные посты на странице пользователя"""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.chek_context(response, self.user, self.group, 13)

    def test_group_page_show_correct_group(self):
        """Корректная группа передается в шаблон"""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        actual_group = response.context['group']
        self.assertEqual(self.group, actual_group)

    def test_profile_page_show_correct_user(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        actual_user = response.context['author']
        self.assertEqual(self.user, actual_user)

    def test_create_form_is_correct(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_form_is_correct(self):
        """Поля формы на странице редактирования поста корректного типа"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.posts[0].pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_form_suggests_correct_post(self):
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.posts[0].pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        actual_post = response.context['post']
        self.assertEqual(actual_post, self.posts[0])

    def test_post_detail_shows_correct_post(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.posts[0].pk}))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        actual_post = response.context['post']
        self.assertEqual(actual_post, self.posts[0])

    def test_new_post_not_in_incorrect_group(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group_no_posts.slug}
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertNotIn(self.posts[0], response.context.get('page_obj'))
