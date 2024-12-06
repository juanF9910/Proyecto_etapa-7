from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from .models import BlogPost
from .serializers import BlogPostSerializer
from django.db.models import Q
from django.http import Http404
from .permissions import read_and_edit
from .serializers import LikeSerializer, CommentSerializer
from .models import Like, Comment

class BlogPostListView(APIView):

    permission_classes = [read_and_edit]

    def get(self, request):
        user = request.user
        queryset = BlogPost.objects.filter(post_permissions='public')

        if user.is_authenticated:
            queryset |= BlogPost.objects.filter(
                Q(post_permissions='authenticated') | 
                Q(author=user)
            )

            if user.groups.exists():
                queryset |= BlogPost.objects.filter(post_permissions='team', author__groups__in=user.groups.all())

        serializer = BlogPostSerializer(queryset.distinct(), many=True)
        return Response(serializer.data)

class BlogPostDetailView(APIView):
    permission_classes = [read_and_edit]

    def get_object(self, pk):
        try:
            return BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            raise Http404("El post no se encuentra o no tienes permiso para verlo.")

    def get(self, request, pk):
        post = self.get_object(pk)
        serializer = BlogPostSerializer(post)
        return Response(serializer.data)

    def delete(self, request, pk):
        post = self.get_object(pk)
        if post.author != request.user and not request.user.is_superuser:
            raise PermissionDenied("No tienes permiso para eliminar este post.")
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk):
        post = self.get_object(pk)
        if post.author != request.user and not request.user.is_superuser:
            raise PermissionDenied("No tienes permiso para editar este post.")
        serializer = BlogPostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from rest_framework import viewsets

class BlogPostCreateView(APIView):
    permission_classes = [read_and_edit]  # Permitir solo usuarios autenticados

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Debes estar autenticado para crear un post."}, status=status.HTTP_401_UNAUTHORIZED)

        # Crear el post y asignar el autor automáticamente
        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # El autor se asigna automáticamente
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeListView(APIView):
    permission_classes = [read_and_edit]  # Permitir acceso público para lectura

    def get(self, request):
        # Obtenemos todos los likes
        queryset = Like.objects.all()

        # Filtramos según la autenticación del usuario
        if request.user.is_authenticated:
            user_groups = request.user.groups.all()
            queryset = queryset.filter(
                Q(post__post_permissions='public') |
                Q(post__post_permissions='authenticated') |
                Q(post__author=request.user) |
                Q(post__post_permissions='team', post__author__groups__in=user_groups)
            ).distinct()
        else:
            # Si no está autenticado, solo mostramos likes de posts públicos
            queryset = queryset.filter(post__post_permissions='public')

        # Serializamos y retornamos la respuesta
        serializer = LikeSerializer(queryset, many=True)
        return Response(serializer.data)

    
class LikeDetailView(APIView):
    permission_classes = [read_and_edit]

    def get(self, request, pk):
        # Buscar todos los likes del post con el id pk
        likes = Like.objects.filter(post__id=pk)

        # Si no hay likes para este post
        if not likes.exists():
            return Response({"detail": "No likes found for this post."}, status=status.HTTP_404_NOT_FOUND)

        # Serializar los likes encontrados
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)

    
class CommentListView(APIView):
    permission_classes = [read_and_edit]  # Permitir acceso público para lectura

    def get(self, request):
        # Obtenemos todos los comentarios
        queryset = Comment.objects.all()

        # Filtramos según la autenticación del usuario
        if request.user.is_authenticated:
            user_groups = request.user.groups.all()
            queryset = queryset.filter(
                Q(post__post_permissions='public') |
                Q(post__post_permissions='authenticated') |
                Q(post__author=request.user) |
                Q(post__post_permissions='team', post__author__groups__in=user_groups)
            ).distinct()
        else:
            # Si no está autenticado, solo mostramos comentarios de posts públicos
            queryset = queryset.filter(post__post_permissions='public')

        # Serializamos y retornamos la respuesta
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)


class CommentDetailView(APIView):

    def get(self, request, pk):
        # Buscar todos los comentarios del post con el id pk
        comments = Comment.objects.filter(post__id=pk)

        # Si no hay comentarios para este post
        if not comments.exists():
            return Response({"detail": "No comments found for this post."}, status=status.HTTP_404_NOT_FOUND)

        # Serializar los comentarios encontrados
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class CommentCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Debes estar autenticado para comentar.")
        data = request.data.copy()
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LikeCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Debes estar autenticado para dar un like.")
        data = request.data.copy()
        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)