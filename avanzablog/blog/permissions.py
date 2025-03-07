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

        # Team permissions (Check if user belongs to any of the author's groups)
        if request.user.is_authenticated and hasattr(obj, 'team'):
            user_groups = set(request.user.groups.all())
            author_groups = set(obj.author.groups.all())

            if user_groups & author_groups:  # Check if there's any group in common
                return self.check_permission(request, obj.team)

        # Authenticated permissions
        if request.user.is_authenticated:
            return self.check_permission(request, obj.authenticated)

        # Public permissions (applies to all users)
        if hasattr(obj, 'is_public'):
            return self.check_permission(request, obj.is_public)

        # Default: No permission
        return False


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
