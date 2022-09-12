# posts/urls.py
from django.urls import path
from posts.views import (group_posts, index, post_create,
                         post_edit, post_view, profile, page_not_found)

app_name = 'posts'
urlpatterns = [
    path('group/<slug:slug>/', group_posts, name='group_list'),
    path('profile/<str:username>/', profile, name='profile'),
    path('posts/<int:post_id>/', post_view, name='post_detail'),
    path('create/', post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', post_edit, name='post_edit'),
    path("404/", page_not_found, name="404"),
    path('', index, name='index'),
]
