from rest_framework import filters
import django_filters
from .models import Post, Like, Comment

# Filtrar por post_id y user_id
class LikeFilter(django_filters.FilterSet):
    post_id = django_filters.NumberFilter(field_name="post__id", lookup_expr='exact')
    user_id = django_filters.NumberFilter(field_name="user__id", lookup_expr='exact')

    class Meta:
        model = Like
        fields = ['post_id', 'user_id']

class CommentFilter(django_filters.FilterSet):
    post_id = django_filters.NumberFilter(field_name="post__id", lookup_expr='exact')
    user_id = django_filters.NumberFilter(field_name="user__id", lookup_expr='exact')

    class Meta:
        model = Comment
        fields = ['post_id', 'user_id']