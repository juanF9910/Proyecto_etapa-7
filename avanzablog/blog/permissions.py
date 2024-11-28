from rest_framework.permissions import BasePermission, SAFE_METHODS

class BlogPostPermission(BasePermission):
    """
    Custom permission to manage access to blog posts based on `post_permissions`
    with independent controls for reading and writing.
    """

def has_object_permission(self, request, view, obj):
    """
    Manage object-level permissions for individual blog post access.
    """
    is_read_only = request.method in SAFE_METHODS

    # Public posts: allow read-only access for all
    if obj.post_permissions == 'public':
        return is_read_only

    # Authenticated: allow read-only access if authenticated
    if obj.post_permissions == 'authenticated':
        return is_read_only and request.user.is_authenticated

    # Team: allow read/write for same team
    if obj.post_permissions == 'team':
        return (
            request.user == obj.author
            or (hasattr(request.user, 'team') and request.user.team == obj.author.team)
        )

    # Author: Only the author can read/write
    if obj.post_permissions == 'author':
        return obj.author == request.user

    # Deny all other requests
    return False

