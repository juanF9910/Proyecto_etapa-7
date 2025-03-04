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
        if obj.author == request.user:
            return True

        # Team permissions (Check if user belongs to the same team as the author)
        if request.user.is_authenticated and getattr(request.user, 'team', None) == getattr(obj.author, 'team', None):
            return self.check_permission(request, obj.team)

        # Authenticated permissions
        if request.user.is_authenticated:
            return self.check_permission(request, obj.authenticated)

        # Public permissions (applies to all users)
        return self.check_permission(request, getattr(obj, 'is_public', 'none'))

    def check_permission(self, request, access_level):
        """
        Helper method to determine if the request method is allowed based on access level.
        """
        if access_level == 'none':
            return False
        if access_level == 'read only':
            return request.method in permissions.SAFE_METHODS  # Only GET, HEAD, and OPTIONS are allowed
        if access_level == 'read and edit':
            return True  # All methods are allowed
        return False
