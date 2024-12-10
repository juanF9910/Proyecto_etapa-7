from rest_framework import serializers
from .models import BlogPost, Like, Comment





class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Campo adicional
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'username', 'content', 'created_at']  # 'post' se dejará de incluir
        read_only_fields = ['user', 'post']  # 'post' ya no es requerido en la solicitud




class BlogPostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='author.username', read_only=True)  # Campo adicional para el autor
    likes_count = serializers.SerializerMethodField()  # Campo calculado para contar likes
    comments_count = serializers.SerializerMethodField()  # Campo calculado para contar comentarios
    excerpt = serializers.SerializerMethodField()  # Campo calculado para el extracto del contenido
    equipo = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True, source='comment_set')  # Anidamos comentarios

    class Meta:
        model = BlogPost
        fields = [
            'id', 'author', 'username', 'equipo', 'title', 'content', 
            'excerpt', 'post_permissions', 'created_at',
            'likes_count', 'comments_count', 'comments'
        ]
        read_only_fields = ['author']  # Excluimos 'author' del campo de entrada, ya que se asigna automáticamente

    def get_likes_count(self, obj):
        """Retorna la cantidad de likes asociados a un post."""
        return Like.objects.filter(post=obj).count()

    def get_comments_count(self, obj):
        """Retorna la cantidad de comentarios asociados a un post."""
        return Comment.objects.filter(post=obj).count()

    def get_excerpt(self, obj):
        """Retorna los primeros 200 caracteres del contenido."""
        return obj.content[:200] if obj.content else ""
    
    def get_equipo(self, obj): 
        grupo = obj.author.groups.first()
        return grupo.name if grupo else None


class LikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Campo adicional
    #post = BlogPostSerializer(read_only=True)  # Serializador anidado para incluir detalles del post

    class Meta:
        model = Like
        fields = ['id','post', 'username', 'created_at']  # Incluye el campo 'post' serializado
        read_only_fields = ['post', 'user']