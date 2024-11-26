from django.db import models

# Create your models here.
class User(models.Model): #abstractuser es un modelo de usuario que ya viene con django, usado para la autenticacion 
    role = models.CharField(max_length=20) #esto es para que el usuario pueda ser admin, autor o lector
    bio = models.TextField(blank=True, null=True) #blank=True para que no sea obligatorio, null=True para que pueda ser nulo, 
    #ponemos la bio para que los autores puedan poner una descripcion de ellos mismos


class Permission(models.Model):
    
    role = models.CharField(max_length=20, unique=True)
    can_create = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    can_manage_all = models.BooleanField(default=False)