from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
   Sólo el propietario del objeto puede editarlo, editar significa
    actualizar y eliminar. put, patch, delete
    """

    #la función has_object_permission se ejecuta cada vez que 
    # se hace una petición, está asociada a un objeto 

    def has_object_permission(self, request, view, obj):

        #la lista de SAFE_METHODS contiene los métodos que no modifican
        #la base de datos, es decir, son seguros, estos son: get, head, options
        #get es para obtener un objeto, head es para obtener la cabecera de un objeto, 
        #la cabecera de un objeto es la información del objeto,
        #options es para obtener las opciones de un objeto

        if request.method in permissions.SAFE_METHODS:
            return True

        #verificamos si
        return obj.author == request.user