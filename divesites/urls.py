from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'divesites', views.DivesiteViewSet)
router.register(r'dives', views.DiveViewSet)

urlpatterns = [
        url(r'^', include(router.urls)),
        ]
