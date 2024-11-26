from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import BlogPost, Like, Comment
from .serializers import BlogPostSerializer, LikeSerializer, CommentSerializer


class BlogPostViewSet(ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='like', serializer_class=LikeSerializer)    
    def like(self, request, pk=None):
        post = self.get_object()

        # Copiamos los datos del request y asignamos el ID del post
        data = request.data.copy()
        data['post'] = post.id
        data['user'] = request.user.id  # Asignamos el usuario autenticado

        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='comment', serializer_class=CommentSerializer)
    def comment(self, request, pk=None):
        post = self.get_object() #desde el objeto post voy agregar un comentario, 
        #es decir modificar la base de datos de comentarios

        # Copiamos los datos del request y asignamos el ID del post
        data = request.data.copy()
        data['post'] = post.id
        data['user'] = request.user.id  # Asignamos el usuario autenticado

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()#se guarda el comentario en la base de datos
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeViewSet(ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

