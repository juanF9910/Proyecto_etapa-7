from rest_framework import serializers
from .models import BlogPost, Like, Comment


from rest_framework import serializers
from .models import BlogPost, Like, Comment


class BlogPostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='author.username', read_only=True)  # Author's username
    likes_count = serializers.SerializerMethodField()  # Count of likes
    comments_count = serializers.SerializerMethodField()  # Count of comments
    excerpt = serializers.SerializerMethodField()  # Content excerpt (first 200 characters)
    equipo = serializers.SerializerMethodField()  # Group of the author
    # comments = CommentSerializer(many=True, read_only=True, source='comment_set')  # Nested comments

    class Meta:
        model = BlogPost
        fields = [
            'id', 'author', 'username', 'title', 'content', 'excerpt', 
            'is_public', 'authenticated', 'team', 'owner',  # Permission fields
            'created_at', 'updated_at', 'likes_count', 'comments_count', 'equipo'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'likes_count', 'comments_count']

    def get_likes_count(self, obj):
        """Returns the number of likes associated with the post."""
        return Like.objects.filter(post=obj).count()

    def get_comments_count(self, obj):
        """Returns the number of comments associated with the post."""
        return Comment.objects.filter(post=obj).count()

    def get_excerpt(self, obj):
        """Returns the first 200 characters of the content."""
        return obj.content[:200] if obj.content else ""

    def get_equipo(self, obj):
        """Returns the name of the author's first group."""
        grupo = obj.author.groups.first()
        return grupo.name if grupo else None



class LikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Campo adicional
    #post = BlogPostSerializer(read_only=True)  # Serializador anidado para incluir detalles del post

    class Meta:
        model = Like
        fields = ['id','post', 'username', 'created_at']  # Incluye el campo 'post' serializado
        read_only_fields = ['post', 'user']


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Campo adicional

    class Meta:
        model = Comment
        fields = ['id', 'post', 'username', 'content', 'created_at']
        read_only_fields = ['post', 'user', 'created_at']

    