from rest_framework import serializers
from .models import BlogPost, Like, Comment

class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        #el campo fields permite seleccionar los campos que se van a serializar
        fields = ['id','author','title', 'content', 'post_permissions', 'created_at', 'updated_at']
        #el campo read_only_fields permite seleccionar los campos que no se pueden modificar
        read_only_fields = ['author']

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['post', 'user'] #el usuario no puede modificar el like
        #se asigna automaticamente el usuario que realiza el like

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['post','user'] #el usuario no puede modificar el comentario