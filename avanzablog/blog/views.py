from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from .models import BlogPost
from .serializers import BlogPostSerializer
from django.db.models import Q
from django.http import Http404

from .serializers import LikeSerializer, CommentSerializer
from .models import Like, Comment
from rest_framework import viewsets
from .pagination import BlogPostPagination, LikePagination


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BlogPost
from .serializers import BlogPostSerializer
from .permissions import BlogPostPermission
from .pagination import BlogPostPagination

class BlogPostListView(APIView):

    permission_classes = [BlogPostPermission]

    def get_queryset(self, request):
        """
        Build and return the queryset based on the user's permission rules.
        """
        user = request.user
        posts = BlogPost.objects.all()  # Start with all posts
        readable_posts = []

        for post in posts:
            # Use the BlogPostPermission to check if the user has 'read' access
            permission = BlogPostPermission()
            if permission.check_permission(request, post.is_public) or permission.has_object_permission(request, self, post):
                readable_posts.append(post)

        # Convert the list of readable posts to a queryset and order by created_at
        queryset = BlogPost.objects.filter(id__in=[post.id for post in readable_posts]).distinct().order_by('created_at')
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)

        if not queryset.exists():
            return Response({"detail": "No hay posts disponibles."}, status=status.HTTP_404_NOT_FOUND)

        # Paginate the queryset
        paginator = BlogPostPagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = BlogPostSerializer(result_page, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)


class BlogPostDetailView(APIView):
    permission_classes = [BlogPostPermission]

    def get_object(self, pk):
        """
        Retrieve the BlogPost object or raise 404 if it does not exist.
        """
        try:
            post= BlogPost.objects.get(pk=pk)
            return post
        except BlogPost.DoesNotExist:
            print("No se encuentra el post")
            raise Http404("El post no se encuentra.")

    def get(self, request, pk):
        post = self.get_object(pk)
        
        try:
            # Check permissions for the specific object (raises an exception if not allowed)
            self.check_object_permissions(request, post)
        except PermissionDenied:
            return Response({"detail": "No tienes permiso para ver este post."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BlogPostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        post = self.get_object(pk)
        print(post)
        print(f"Received data: {request.data}")  
        
        try:
            # Check permissions for editing
            self.check_object_permissions(request, post)
        except PermissionDenied:
            return Response({"detail": "No tienes permiso para editar este post."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BlogPostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        post = self.get_object(pk)
        
        try:
            # Check permissions for deletion
            self.check_object_permissions(request, post)
        except PermissionDenied:
            return Response({"detail": "No tienes permiso para eliminar este post."}, status=status.HTTP_403_FORBIDDEN)
        
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class LikeListView(APIView):
    permission_classes = [BlogPostPermission]

    def get_queryset(self, request):
        """
        Build and return the queryset for likes, ensuring permissions on associated blog posts.
        """
        likes = Like.objects.select_related('post')  # Optimize query by prefetching related posts
        readable_likes = []

        for like in likes:
            post = like.post
            permission = BlogPostPermission()
            
            # Check if the user has 'read' access to the related blog post
            if permission.has_object_permission(request, self, post):
                readable_likes.append(like)

        # Convert the list of readable likes to a queryset and order by created_at
        queryset = Like.objects.filter(id__in=[like.id for like in readable_likes]).distinct().order_by('created_at')
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)

        if not queryset.exists():
            return Response({"detail": "No hay likes disponibles."}, status=status.HTTP_404_NOT_FOUND)

        # Paginate the queryset
        paginator = LikePagination()
        result_page = paginator.paginate_queryset(queryset, request)
        serializer = LikeSerializer(result_page, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)
    


class LikeDetailView(APIView):
    permission_classes = [BlogPostPermission]

    def get_post(self, pk):
        """
        Retrieve the BlogPost object or raise 404 if not found.
        """
        try:
            return BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            raise Http404("El post no se encuentra.")

    def get(self, request, pk):
        """
        Retrieve all likes for a specific blog post if the user has permission to view the post.
        """
        post = self.get_post(pk)
        self.check_object_permissions(request, post)  # Validate permissions on the post, if the post has no permissions, it will return 403
        
        likes = Like.objects.filter(post=post)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        """
        Add or remove a like for the specified blog post if the user has permission.
        """
        post = self.get_post(pk)
        self.check_object_permissions(request, post)  # Validate permissions on the post
        
        # Check if the user has already liked the post
        existing_like = Like.objects.filter(post=post, user=request.user).first()
        
        if existing_like:
            existing_like.delete()  # Remove the like if it already exists
            return Response({"detail": "Like eliminado."}, status=status.HTTP_200_OK)
        
        # Create a new like if it doesn't exist
        like = Like.objects.create(post=post, user=request.user)
        serializer = LikeSerializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class CommentListView(APIView):
    permission_classes = [BlogPostPermission]

    def get_queryset(self, request):
        """
        Build and return the queryset based on the user's permission rules for related blog posts.
        """
        user = request.user
        comments = Comment.objects.all()  # Start with all comments
        readable_comments = []

        for comment in comments:
            # Use BlogPostPermission to check if the user has access to the related post
            permission = BlogPostPermission()
            post = comment.post
            if permission.has_object_permission(request, self, post):
                readable_comments.append(comment)

        # Convert the list of readable comments to a queryset and order by created_at
        queryset = Comment.objects.filter(id__in=[comment.id for comment in readable_comments]).distinct().order_by('created_at')
        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset(request)

        if not queryset.exists():
            return Response({"detail": "No hay comentarios disponibles."}, status=status.HTTP_404_NOT_FOUND)

        # Paginate the queryset
        paginator = BlogPostPagination()
        result_page = paginator.paginate_queryset(queryset, request)

        # Serialize the paginated data
        serializer = CommentSerializer(result_page, many=True)

        # Return the paginated response
        return paginator.get_paginated_response(serializer.data)



class CommentDetailView(APIView):
    permission_classes = [BlogPostPermission]

    def get_post(self, pk):
        """
        Retrieve the BlogPost object or raise 404 if not found.
        """
        try:
            return BlogPost.objects.get(pk=pk)
        except BlogPost.DoesNotExist:
            raise Http404("El post no se encuentra.")

    def get(self, request, pk):
        """
        Retrieve all comments for a specific blog post if the user has permission to view the post.
        """
        post = self.get_post(pk)
        self.check_object_permissions(request, post)  # Validate permissions on the post
        
        comments = Comment.objects.filter(post=post)
        if not comments.exists():
            return Response({"detail": "No hay comentarios para este post."}, status=status.HTTP_200_OK)
        
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        """
        Crea un comentario asociado al post con el ID dado (pk).
        """
        post= self.get_post(pk)
        self.check_object_permissions(request, post)  # Valida permisos del post
        content = request.data.get("content")
        if not content:
            return Response({"detail": "El contenido del comentario es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(post=post, user=request.user, content=content)
        #self.check_object_permissions(request, comment)  # Valida permisos del comentario antes de serializar
        serializer = CommentSerializer(comment) #si el comentario cumple con los permisos, se serializa
        return Response(serializer.data, status=status.HTTP_201_CREATED)






class BlogPostCreateView(APIView):
    permission_classes = [BlogPostPermission]  # Restrict access based on custom permissions

    def get(self, request):
        """
        Return a message indicating that this endpoint only accepts POST requests.
        """
        if not request.user.is_authenticated:
            return Response({"detail": "Debes estar autenticado para crear un post."}, status=status.HTTP_401_UNAUTHORIZED)

        return Response({"detail": "Este endpoint solo acepta solicitudes POST. Cree su post con formato JSON."}, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Debes estar autenticado para crear un post."}, status=status.HTTP_401_UNAUTHORIZED)

        self.check_permissions(request)  # Verifica permisos

        print("Datos recibidos en el backend:", request.data)  # 👀 Verifica los datos en la consola

        serializer = BlogPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        print("Errores del serializer:", serializer.errors)  # 👀 Verifica los errores en la consola
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CommentDeleteView(APIView):
    permission_classes = [BlogPostPermission]

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            raise Http404("El comentario no se encuentra.")

    def get(self, request, pk):
        comment = self.get_object(pk)
        self.check_object_permissions(request, comment.post)  # Use built-in permission check for the related post

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        self.check_object_permissions(request, comment.post)

        comment.delete()
        return Response({"detail": f"Comentario eliminado correctamente (ID: {pk})."}, status=status.HTTP_204_NO_CONTENT)
