from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action 
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from .serializers import UserSerializer
from django.contrib.auth.models import User
from rest_framework import viewsets


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    #la clase ReadOnlyModelViewSet permite acceder a las acciones
    #get y list de los modelos a traves de la api
    #pero no permite modificar la base de datos de usu
   
    queryset = User.objects.all()
    serializer_class = UserSerializer