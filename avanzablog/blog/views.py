from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from .models import BlogPost
from .serializers import BlogPostSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import read_and_edit

class BlogPostCreateView(APIView):
    permission_classes = [read_and_edit]  # Asegúrate de que el usuario esté autenticado

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise NotAuthenticated("Debes estar autenticado para crear un post.")
        
        # Usamos el serializer para validar y guardar el post
        serializer = BlogPostSerializer(data=request.data)
        
        if serializer.is_valid():
            # Establecemos el autor como el usuario autenticado
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)