from rest_framework import serializers
from .models import BlogPost, Like, Comment

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        #read_only_fields = ['user'] #el usuario no puede modificar el like
        #se asigna automaticamente el usuario que realiza el like

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        #read_only_fields = ['user'] #el usuario no puede modificar el comentario