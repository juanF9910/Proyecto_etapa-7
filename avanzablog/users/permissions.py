from rest_framework.permissions import BasePermission

class UserPermissions(BasePermission):
    """
    Permiso basado en el tipo de usuario (Admin, Autores, Equipos).
    """

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True  # Admins pueden realizar cualquier acción
        if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'): # Solo los usuarios autenticados pueden escribir en la API 
            return request.user.is_authenticated and request.user.is_staff
        return True  # Usuarios autenticados pueden leer

    def has_object_permission(self, request, view, obj):
        """
        Control de acceso específico de objeto.
        """
        if request.user.is_superuser:
            return True
        if obj.post_permissions == 'author':
            return obj.author == request.user
        if obj.post_permissions == 'team':
            return request.user.team == obj.author.team if hasattr(request.user, 'team') else False
        return request.method in ('GET', 'HEAD', 'OPTIONS')