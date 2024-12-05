from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from .models import BlogPost, Like, Comment
from .serializers import BlogPostSerializer, LikeSerializer, CommentSerializer
from .permissions import read_and_edit
from .pagination import  BlogPostPagination, LikePagination
from django.db.models import Q
from django.http import Http404

class BlogPostViewSet(ModelViewSet):

    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [read_and_edit]
    pagination_class = BlogPostPagination

    #este es el metodo que se encarga de filtrar los posts que se van a mostrar
    #en la vista de lista de posts de la api de blogpost y en la vista de detalle
    def get_queryset(self):
        user = self.request.user

        # Usuarios no autenticados solo pueden ver posts públicos
        if not user.is_authenticated:
            return BlogPost.objects.filter(post_permissions='public')

        # Usuarios autenticados: filtrar por permisos
        queryset = BlogPost.objects.filter(
            Q(post_permissions='public') | Q(post_permissions='authenticated') |  Q(author=user)  
        )

        # Filtrar por equipo si el usuario pertenece a algún grupo
        if user.groups.exists():
            group_queryset = BlogPost.objects.filter(post_permissions='team')
            queryset = queryset | group_queryset

        return queryset.distinct()

    #error en la vista de detalle de un post si el usuario no tiene permisos
    #o si el post no existe

    #cuando se vaya a obtener un post se determina si existe en la lista de posts filtrados
    def get_object(self):
            # Personaliza la lógica de obtención del objeto para la vista de detalle
            queryset = self.get_queryset()
            # Obtenemos el objeto solo si está en el queryset filtrado
            obj = queryset.filter(pk=self.kwargs["pk"]).first()
            if obj is None:
                raise Http404("El post no se encuentra o no tienes permiso para verlo.")
            return obj

    #cuando se vaya a crear un post se asigna el usuario autenticado
    def perform_create(self, serializer):
        
        """
            obrescribe la creación para asignar el usuario autenticado como autor.
        """
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Debes estar autenticado para crear un post.")
        serializer.save(author=self.request.user)


    #reescribir el metodo destroy para que solo el autor o un superusuario puedan eliminar un post 
    def destroy(self, request, *args, **kwargs):
            post = self.get_object()  # Obtener el post que se intenta eliminar
            #si el usuario no es el autor y tampoco es un superusuario
            if post.author != request.user and not request.user.is_superuser:
              raise PermissionDenied("Solo el autor o un superusuario pueden eliminar este post.")

             #Proceder con la eliminación si los permisos son correctos
            return super().destroy(request, *args, **kwargs)
    
    @action(detail=True, methods=['POST', 'GET'], serializer_class=LikeSerializer)
    def like(self, request, pk):
        post = self.get_object()  # Obtener el objeto post

        if request.method == 'GET':
            likes = Like.objects.filter(post=post)
            serializer = LikeSerializer(likes, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            # Verificar si el usuario ya ha dado like
            existing_like = Like.objects.filter(post=post, user=request.user).first()
            if existing_like:
                existing_like.delete()
                return Response({"detail": "Diste un dislike"}, status=status.HTTP_400_BAD_REQUEST)
            else:
            # Crear un nuevo like y asignar explícitamente el post

                serializer = LikeSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save(user=request.user, post=post)  # Asignar explícitamente post

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response({"detail": "Método no permitido."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



    @action(detail=True, methods=['POST', 'GET'], serializer_class=CommentSerializer)
    def comment(self, request, pk=None):
        post = self.get_object()  # Obtenemos el objeto post
        
        if request.method == 'GET':
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        
        if request.method == 'POST':
            # Ensure the user is authenticated
            if not request.user.is_authenticated:
                raise NotAuthenticated("Debes estar autenticado para comentar.")
            
            # Copy the data and assign the post ID
            data = request.data.copy()
            data['post'] = post.id  # Explicitly set the post ID for the comment
            
            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                serializer.save(user=request.user, post=post)  # Explicitly save with post
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Método no permitido."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


#esta clase permite acceder a las acciones
#post, get, put, delete, etc de los modelos a traves de la api

class LikeViewSet(ModelViewSet):
    queryset = Like.objects.all().order_by('-created_at')
    serializer_class = LikeSerializer
    permission_classes = [read_and_edit]
    pagination_class = LikePagination

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Debes estar autenticado para dar un like.")
        serializer.save(user=self.request.user)

    def get_queryset(self):
        user = self.request.user
        
        # Filtrar los 'likes' asociados a posts con los permisos adecuados
        queryset = Like.objects.all()
        
        # Usuarios no autenticados solo pueden ver likes en posts públicos
        if not user.is_authenticated:
            queryset = queryset.filter(post__post_permissions='public')

        # Usuarios autenticados: filtrar por permisos de posts
        else:
            queryset = queryset.filter(
                Q(post__post_permissions='public') | 
                Q(post__post_permissions='authenticated') | 
                Q(post__author=user)
            )

            # Filtrar por equipo si el usuario pertenece a algún grupo
            if user.groups.exists():
                queryset = queryset.filter(post__post_permissions='team')

        return queryset.distinct()

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [read_and_edit]
    pagination_class = BlogPostPagination

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise NotAuthenticated("Debes estar autenticado para comentar.")
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()

        # Verificar si el usuario es el autor del comentario o un superusuario
        if comment.user != request.user and not request.user.is_superuser:
            raise PermissionDenied("Solo el autor o un superusuario pueden eliminar este comentario.")

        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        # Filtrar los comentarios asociados a posts con los permisos adecuados
        queryset = Comment.objects.all()

        # Usuarios no autenticados solo pueden ver comentarios en posts públicos
        if not user.is_authenticated:
            queryset = queryset.filter(post__post_permissions='public')

        # Usuarios autenticados: filtrar por permisos de posts
        else:
            queryset = queryset.filter(
                Q(post__post_permissions='public') | 
                Q(post__post_permissions='authenticated') | 
                Q(post__author=user)
            )

            # Filtrar por equipo si el usuario pertenece a algún grupo
            if user.groups.exists():
                queryset = queryset.filter(post__post_permissions='team')

        return queryset.distinct()