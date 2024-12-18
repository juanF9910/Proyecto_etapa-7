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
from rest_framework import viewsets
from .pagination import BlogPostPagination, LikePagination

class BlogPostListView(APIView):
    
    permission_classes = [read_and_edit]

    def get_queryset(self, request):
        """
        Construye y devuelve el conjunto de datos basado en las reglas de permisos del usuario.
        """
        user = request.user


        # Query inicial: Posts públicos
        filters = Q(post_permissions='public')

        if user.is_authenticated:
            # Añadir posts autenticados y posts del autor
            filters |= Q(post_permissions='authenticated') | Q(author=user)

            # Añadir posts asociados a los grupos del usuario
            if user.groups.exists():
                filters |= Q(post_permissions='team', author__groups__in=user.groups.all())

        # Construir el queryset final
        queryset = BlogPost.objects.filter(filters).distinct().order_by('created_at')

        return queryset
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        
        if not queryset.exists():
            return Response({"detail": "No hay posts disponibles."}, status=status.HTTP_404_NOT_FOUND)
        # Initialize the paginator
        paginator = BlogPostPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = BlogPostSerializer(result_page, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)
    
class BlogPostDetailView(APIView):
    permission_classes = [read_and_edit]

   
    def get_object(self, pk):
        try:
            return BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            # Return a custom 404 response with a message
            return Response({"detail": "El post no se encuentra."}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)  # Valida permisos
        serializer = BlogPostSerializer(post)
        return Response(serializer.data)

    def patch(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)  # Verifica permisos para editar
        serializer = BlogPostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)  # Verifica permisos, si no tiene permisos lanza una excepción PermissionDenied 
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class LikeListView(APIView):
    permission_classes = [read_and_edit]  # Actualiza con tu clase de permiso personalizada

    def get_queryset(self, request):
        """
        Construye y devuelve el conjunto de datos basado en las reglas de permisos del usuario.
        """
        queryset = Like.objects.all()

        if request.user.is_authenticated:
            user_groups = request.user.groups.all()
            queryset = queryset.filter(
                Q(post__post_permissions='public') |
                Q(post__post_permissions='authenticated') |
                Q(post__author=request.user) |
                Q(post__post_permissions='team', post__author__groups__in=user_groups)
            ).distinct()
        else:
            queryset = queryset.filter(post__post_permissions='public')

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)
        
        # Inicializamos la paginación
        paginator = LikePagination()
        result_page = paginator.paginate_queryset(queryset, request)

        # Serializamos los datos paginados
        serializer = LikeSerializer(result_page, many=True)

        # Retornamos la respuesta paginada
        return paginator.get_paginated_response(serializer.data)

    
class LikeDetailView(APIView):

    permission_classes = [read_and_edit]

    def get_object(self, pk):
        try:
            return BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            raise Http404("El post no se encuentra.")
        
    def get(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)  # Valida permisos del post
        likes = Like.objects.filter(post=post)
        for like in likes:
            self.check_object_permissions(request, like)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)
        existing_like = Like.objects.filter(post=post, user=request.user).first()
        #self.check_object_permissions(request, existing_like)  # Valida permisos del like
        if existing_like:
            existing_like.delete()
            return Response({"detail": "Like eliminado."}, status=status.HTTP_200_OK)
        
        like = Like.objects.create(post=post, user=request.user)
        #self.check_object_permissions(request, like)  # Valida permisos del like
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class CommentListView(APIView):
    permission_classes = [read_and_edit]  # Permitir acceso público para lectura

    def get_queryset(self, request):
        """
        Construye y devuelve el conjunto de datos basado en las reglas de permisos del usuario.
        """
        user = request.user

        # Query inicial: Comentarios de posts públicos
        filters = Q(post__post_permissions='public')

        if user.is_authenticated:
            # Añadir comentarios de posts autenticados, del autor o asociados al mismo equipo
            filters |= Q(post__post_permissions='authenticated') | Q(post__author=user)

            # Añadir comentarios de posts asociados a los grupos del usuario
            if user.groups.exists():
                filters |= Q(post__post_permissions='team', post__author__groups__in=user.groups.all())

        # Construir el queryset final
        queryset = Comment.objects.filter(filters).distinct()

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)

        # Inicializamos la paginación
        paginator = BlogPostPagination()
        result_page = paginator.paginate_queryset(queryset, request)

        # Serializamos los datos paginados
        serializer = CommentSerializer(result_page, many=True)

        # Retornamos la respuesta paginada
        return paginator.get_paginated_response(serializer.data)



class CommentDetailView(APIView):

    permission_classes = [read_and_edit]

    def get_object(self, pk):
        try:
            return BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            raise Http404("El post no se encuentra.")

    def get(self, request, pk):
        post = self.get_object(pk)
        self.check_object_permissions(request, post)  # This should raise an exception for unauthorized users
        comments = Comment.objects.filter(post=post)
        if not comments:
            return Response({"detail": "No hay comentarios para este post."}, status=status.HTTP_404_NOT_FOUND)
        else:
            for comment in comments:
                self.check_object_permissions(request, comment)  # Check permissions for each comment
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    
    def post(self, request, pk):
        """
        Crea un comentario asociado al post con el ID dado (pk).
        """
        post= self.get_object(pk)
        self.check_object_permissions(request, post)  # Valida permisos del post
        content = request.data.get("content")
        if not content:
            return Response({"detail": "El contenido del comentario es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(post=post, user=request.user, content=content)
        #self.check_object_permissions(request, comment)  # Valida permisos del comentario antes de serializar
        serializer = CommentSerializer(comment) #si el comentario cumple con los permisos, se serializa
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class BlogPostCreateView(APIView):

        permission_classes = [read_and_edit]  # Permitir solo usuarios autenticados
            
        def get(self, request):

            if not request.user.is_authenticated:
                return Response({"detail": "Debes estar autenticado para crear un post."}, status=status.HTTP_401_UNAUTHORIZED)
                                
            return Response({"detail": "Este endpoint solo acepta solicitudes POST, cree su post con formato JSON"}, status=status.HTTP_200_OK)
        
        def post(self, request):

            if not request.user.is_authenticated:
                return Response({"detail": "Debes estar autenticado para crear un post."}, status=status.HTTP_401_UNAUTHORIZED)

            # Crear el post y asignar el autor automáticamente
            serializer = BlogPostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user)  # El autor se asigna automáticamente
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDeleteView(APIView):

    permission_classes = [read_and_edit]

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404("El comentario no se encuentra.")

    def get(self,request,pk):
        comment= self.get_object(pk)
        self.check_object_permissions(request, comment)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        comment = self.get_object(pk)
        self.check_object_permissions(request, comment)
        comment.delete()
        print(f"Deleted comment: {comment.id}")  # Debugging
        return Response(status=status.HTTP_204_NO_CONTENT)


