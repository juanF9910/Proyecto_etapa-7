from django.urls import path
from rest_framework.routers import DefaultRouter
from .viewsets import BlogPostViewSet, LikeViewSet, CommentViewSet

router = DefaultRouter()
router.register("post", BlogPostViewSet)
router.register("like", LikeViewSet)
router.register("comment", CommentViewSet)

urlpatterns =[

    path('api/custom-post/', BlogPostViewSet.as_view({'post': 'create_custom'}), name='create_custom_post'),
    #path('custom_post/create/', BlogPostViewSet.as_view({'post': 'create_custom'}), name='create_custom_post'),
    path('post/<int:post_id>/comment/<int:pk>/', CommentViewSet.as_view({'delete': 'destroy', 'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}), name='comment-detail'),
]

# Rutas generadas por el router
urlpatterns += router.urls