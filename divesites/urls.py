from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'divesites', views.DivesiteViewSet)

urlpatterns = [
        url(r'^', include(router.urls)),
        ]
