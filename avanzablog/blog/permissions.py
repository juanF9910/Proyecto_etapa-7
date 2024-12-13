
from rest_framework import permissions

class read_and_edit(permissions.BasePermission):


    def has_object_permission(self, request, view, obj):
        # Permitir acceso total a superusuarios
        if request.user.is_superuser:
            return True

        # Permisos de los posts
        if hasattr(obj, 'post_permissions'):
            # Permisos de lectura (SAFE_METHODS)
            if request.method in permissions.SAFE_METHODS:
                if obj.post_permissions == 'public':
                    return True
                elif obj.post_permissions == 'authenticated':
                    return request.user.is_authenticated
                elif obj.post_permissions == 'author':
                    return obj.author == request.user
                elif obj.post_permissions == 'team':
                    user_group = request.user.groups.first()
                    if user_group:
                        return obj.author.groups.filter(id=user_group.id).exists()
                    return False
            elif request.method == 'POST' and request.user.is_authenticated:
                return True
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                if obj.author == request.user:
                    return True
                user_group = request.user.groups.first()
                if user_group:
                    return obj.author.groups.filter(id=user_group.id).exists()
                return False

        # Permisos de los likes
        elif hasattr(obj, 'post'): # Verificar si el objeto tiene un campo 'post'

                
            # Verificar si el usuario es el autor del post
            if request.method == 'POST':
                if obj.post.post_permissions == 'public':
                    return True
                elif obj.post.post_permissions == 'authenticated':
                    return request.user.is_authenticated
                elif obj.post.post_permissions == 'author':
                    return request.user == obj.post.author  # Permite a los autores interactuar con sus propios posts
                elif obj.post.post_permissions == 'team':
                    user_group = request.user.groups.first()
                    if user_group:
                        return obj.post.author.groups.filter(id=user_group.id).exists()
                    return False

            elif request.method in permissions.SAFE_METHODS:
                if obj.post.post_permissions == 'public':
                    return True
                elif obj.post.post_permissions == 'authenticated':
                    return request.user.is_authenticated
                elif obj.post.post_permissions == 'author':
                    return obj.post.author == request.user
                elif obj.post.post_permissions == 'team':
                    user_group = request.user.groups.first()
                    if user_group:
                        return obj.post.author.groups.filter(id=user_group.id).exists()
                    return False

            # Permitir si el usuario es el autor del comentario/like o es superusuario
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                if obj.user == request.user:
                    return True
                elif request.user.is_superuser:
                    return True
                user_group = request.user.groups.first()
                if obj.post.post_permissions == 'team':
                    return obj.post.author.groups.filter(id=user_group.id).exists()


        return False
