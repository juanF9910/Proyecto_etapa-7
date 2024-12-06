from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from .models import BlogPost, Like, Comment
from .serializers import BlogPostSerializer, LikeSerializer, CommentSerializer
from .permissions import read_and_edit
from .pagination import BlogPostPagination, LikePagination
from django.db.models import Q
from django.http import Http404

class BlogPostViewSet(ModelViewSet):
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [read_and_edit]
    pagination_class = BlogPostPagination

    def get_queryset(self):
        user = self.request.user

        # Usuarios no autenticados solo pueden ver posts públicos
        queryset = BlogPost.objects.filter(post_permissions='public')

        if user.is_authenticated:
            # Filtrar por permisos 'authenticated', 'author', y 'team'
            queryset |= BlogPost.objects.filter(
                Q(post_permissions='authenticated') | 
                Q(author=user)
            )

            if user.groups.exists():
                queryset |= BlogPost.objects.filter(post_permissions='team', author__groups__in=user.groups.all()
)

        return queryset.distinct()

    #función para el caso en el que se quiera obtener un objeto
    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.filter(pk=self.kwargs["pk"]).first()
        if obj is None:
            raise Http404("El post no se encuentra o no tienes permiso para verlo.")
        return obj

    def create(self, serializer):
        #if not self.request.user.is_authenticated:
        #    raise NotAuthenticated("Debes estar autenticado para crear un post.")
        #serializer.save(author=self.request.user)
        raise PermissionDenied("No puedes crear posts de esta forma.")

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author != request.user and not request.user.is_superuser:
            # Verificar si el usuario pertenece al mismo equipo que el autor
            user_group = request.user.groups.first()
            if user_group:
                if not post.author.groups.filter(id=user_group.id).exists():
                    return response(status=status.HTTP_403_FORBIDDEN)
            else:
                return response(status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)


    @action(detail=False, methods=['POST'], serializer_class=BlogPostSerializer)
    def create_custom(self, request):
        # Verificar si el usuario está autenticado
        if not request.user.is_authenticated:
            raise NotAuthenticated("Debes estar autenticado para crear un post.")

        # Serializar y crear el post
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)  # Asociamos el post al usuario
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST', 'GET'], serializer_class=LikeSerializer)
    def like(self, request, pk):
        post = self.get_object()
        if request.method == 'GET':
            likes = Like.objects.filter(post=post)
            serializer = LikeSerializer(likes, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            existing_like = Like.objects.filter(post=post, user=request.user).first()
            if existing_like:
                existing_like.delete()
                return Response({"detail": "Diste un dislike"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = LikeSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=request.user, post=post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"detail": "Método no permitido."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=True, methods=['POST', 'GET'], serializer_class=CommentSerializer)
    def comment(self, request, pk=None):
        post = self.get_object()
        if request.method == 'GET':
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            if not request.user.is_authenticated:
                raise NotAuthenticated("Debes estar autenticado para comentar.")
            data = request.data.copy()
            data['post'] = post.id
            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=request.user, post=post)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Método no permitido."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    

    

from django_filters.rest_framework import DjangoFilterBackend

class LikeViewSet(ModelViewSet):
    queryset = Like.objects.all().order_by('-created_at')
    serializer_class = LikeSerializer
    permission_classes = [read_and_edit]
    pagination_class = LikePagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'user']

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Debes estar autenticado para dar un like.")
        serializer.save(user=self.request.user)

    #filtramos los likes que puede ver el usuario
    #de acuerdo a los per
    def get_queryset(self):
        user = self.request.user
        queryset = Like.objects.all()

        if not user.is_authenticated:
            queryset = queryset.filter(post__post_permissions='public')
        else:
            queryset = queryset.filter(
                Q(post__post_permissions='public') | 
                Q(post__post_permissions='authenticated') | 
                Q(post__author=user)
            )
            if user.groups.exists():
                queryset |= Like.objects.filter(post__post_permissions='team', post__author__groups__in=user.groups.all())

        return queryset.distinct()



class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [read_and_edit]
    pagination_class = BlogPostPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['post', 'user']


    
    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Debes estar autenticado para comentar.")
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        if comment.user != request.user and not request.user.is_superuser:
            raise PermissionDenied("Solo el autor o un superusuario pueden eliminar este comentario.")
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        queryset = Comment.objects.all()

        if not user.is_authenticated:
            queryset = queryset.filter(post__post_permissions='public')
        else:
            queryset = queryset.filter(
                Q(post__post_permissions='public') | 
                Q(post__post_permissions='authenticated') | 
                Q(post__author=user)
            )
            if user.groups.exists():
                queryset |= Comment.objects.filter(post__post_permissions='team', post__author__groups__in=user.groups.all())

        return queryset.distinct()