from rest_framework import permissions

class read_and_edit(permissions.BasePermission):
    
    #permisos de la vista de lista  
    def has_permission(self, request, view):
        

        #solo pueden crear post los usuarios autenticados
        if request.method=='POST':
            return request.user.is_authenticated
        else:
            return True

    # permisos de la vista de detalle
    def has_object_permission(self, request, view, obj):
        
        #verificamos si el usuario es superusuario
        if request.user.is_superuser:
            return True
        #verificamos si el usuario es blogger
        else:
            # permisos de lectura
            if request.method in permissions.SAFE_METHODS:
                
                if obj.post_permissions == 'public':
                    return True
                elif obj.post_permissions == 'authenticated':
                    return request.user.is_authenticated
                elif obj.post_permissions == 'author':
                    return obj.author == request.user
                elif obj.post_permissions == 'team':
                    # Comprobar si el usuario tiene un grupo
                    user_group = request.user.groups.first()
                    if user_group:
                        return obj.author.groups.filter(id=user_group.id).exists()
                    else:
                        return False
                else:
                    return False
            
            # permisos de edición
            else:
                if obj.post_permissions == 'author':
                    return obj.author == request.user
                elif obj.post_permissions == 'team':
                    # Comprobar si el usuario tiene un grupo
                    user_group = request.user.groups.first()
                    if user_group:
                        return obj.author.groups.filter(id=user_group.id).exists()
                    else:
                        return False
                else:
                    return False
