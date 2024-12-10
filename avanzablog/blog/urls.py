from django.urls import path
from .views import (BlogPostListView, BlogPostDetailView, 
                    LikeListView, LikeDetailView, 
                    CommentListView, CommentDetailView, 
                    BlogPostCreateView, CommentDeleteView )

urlpatterns = [
    path('posts/', BlogPostListView.as_view(), name='post-list'),
    path('posts/<int:pk>/', BlogPostDetailView.as_view(), name='post-detail'),
    path('posts/create/', BlogPostCreateView.as_view(), name='post-create'),

    path('likes/', LikeListView.as_view(), name='like-list'),
    path('likes/<int:pk>/', LikeDetailView.as_view(), name='like-detail'),  # Cambiado de 'post-detail' a 'like-detail'

    path('comments/', CommentListView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('comments/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
]
