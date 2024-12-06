from rest_framework import permissions

class read_and_edit(permissions.BasePermission):
    
    def has_permission(self, request, view):
        # Solo los usuarios autenticados pueden crear posts, likes y comentarios
        if request.method == 'POST':
            return request.user.is_authenticated
        else:
            return True

    def has_object_permission(self, request, view, obj):
        # Permitir acceso total a superusuarios
        if request.user.is_superuser:
            return True
        
        # Permisos de los post
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
                    # Verificar si el usuario pertenece al mismo equipo
                    user_group = request.user.groups.first()
                    if user_group:
                        # Permitir acceso si el autor pertenece al mismo equipo que el usuario
                        return obj.author.groups.filter(id=user_group.id).exists()
                    return False

            # Permisos de edición o eliminación (PUT, PATCH, DELETE)
            elif request.method in ['PUT', 'PATCH', 'DELETE']:
                # Permitir si es el autor
                if obj.author == request.user:
                    return True
                
                # Permitir si el usuario pertenece al mismo equipo que el autor
                user_group = request.user.groups.first()
                if user_group:
                    # Permitir eliminación si el autor pertenece al mismo equipo que el usuario
                    return obj.author.groups.filter(id=user_group.id).exists()

                return False

        # Permisos de los likes y los comentarios
        if hasattr(obj, 'post'):
            if request.method in permissions.SAFE_METHODS:
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

            # Permitir si el usuario es el autor del comentario o es superusuario
            if request.method in ['PUT', 'PATCH', 'DELETE']:
                if obj.user == request.user:
                    return True
                
                user_group = request.user.groups.first()
                if user_group:
                    # Verificar si el autor del comentario pertenece al mismo grupo
                    return obj.post.author.groups.filter(id=user_group.id).exists()

                return False

        # Por defecto, denegar acceso si no es BlogPost ni Comment
        return False