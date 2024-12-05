from django.urls import path
from rest_framework.routers import DefaultRouter
from .viewsets import BlogPostViewSet, LikeViewSet, CommentViewSet

router = DefaultRouter()
router.register("post", BlogPostViewSet)
router.register("like", LikeViewSet)
router.register("comment", CommentViewSet)

urlpatterns = [
    # Elimina el comentario específico usando 'pk' como parámetro en lugar de 'comment_id'
    path('post/<int:post_id>/comment/<int:pk>/', CommentViewSet.as_view({'delete': 'destroy'}), name='comment-detail'),
]

# Rutas generadas por el router
urlpatterns += router.urls
