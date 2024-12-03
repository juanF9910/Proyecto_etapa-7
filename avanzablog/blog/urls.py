from django.urls import path
from rest_framework.routers import DefaultRouter
from .viewsets import BlogPostViewSet, LikeViewSet, CommentViewSet

router = DefaultRouter()
router.register("post", BlogPostViewSet)
router.register("like", LikeViewSet)
router.register("comment", CommentViewSet)

urlpatterns = router.urls