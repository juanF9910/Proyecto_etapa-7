from rest_framework import serializers
from .models import BlogPost, Like, Comment

class BlogPostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='author.username', read_only=True)  # Cambiar 'user' a 'author'

    class Meta:
        model = BlogPost
        fields = ['id', 'author', 'username', 'title', 'content', 'post_permissions', 'created_at', 'updated_at']
        read_only_fields = ['author']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['post', 'user'] #el usuario no puede modificar el like
        #se asigna automaticamente el usuario que realiza el like

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Campo adicional

    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'username', 'content', 'created_at']  # Incluye el campo 'username'
        read_only_fields = ['post', 'user']
