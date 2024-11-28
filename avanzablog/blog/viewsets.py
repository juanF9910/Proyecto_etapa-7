from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status

from .models import BlogPost, Like, Comment
from .serializers import BlogPostSerializer, LikeSerializer, CommentSerializer

from .permissions import BlogPostPermission
from users.permissions import UserPermissions

class BlogPostViewSet(ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [BlogPostPermission , UserPermissions]



#esta clase permite acceder a las acciones
#post, get, put, delete, etc de los modelos a traves de la api
class LikeViewSet(ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    #permission_classes = [IsAuthenticatedOrReadOnly]

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    #permission_classes = [IsAuthenticatedOrReadOnly]

