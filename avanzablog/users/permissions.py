from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name='admin').exists()
    

class IsBloger(BasePermission):

    def has_permission(self, request, view):
        return request.user.groups.filter(name='bloger').exists()