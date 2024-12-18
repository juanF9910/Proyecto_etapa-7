from django.urls import path
from rest_framework.routers import DefaultRouter

from .viewsets import UserViewSet

router = DefaultRouter()
router.register("user", UserViewSet)
urlpatterns = router.urls
