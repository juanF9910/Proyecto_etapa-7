from rest_framework import permissions

class BlogPostPermission(permissions.BasePermission):
    
    """
    Custom permission to handle BlogPost access based on the permission fields:
    public, authenticated, team, and owner.
    """

    def has_object_permission(self, request, view, obj):
        # Superuser has full access
        if request.user.is_superuser:
            return True

        # Owner permissions (highest priority, always has full access)
        elif obj.author == request.user:
            return True

        # Team permissions
        elif request.user.is_authenticated and hasattr(obj, 'team_members') and request.user in obj.team_members():
            return self.check_permission(request, obj.team)

        # Authenticated permissions
        elif request.user.is_authenticated:
            return self.check_permission(request, obj.authenticated)

        # Public permissions (applies to all users)
        else:
            return self.check_permission(request, obj.is_public)

    def check_permission(self, request, access_level):
        """
        Helper method to determine if the request method is allowed based on access level.
        """
        if access_level == 'none':
            return False
        elif access_level == 'read only':
            return request.method in permissions.SAFE_METHODS  # Only GET, HEAD, and OPTIONS are allowed
        elif access_level == 'read and edit':
            return True  # All methods are allowed
        return False
