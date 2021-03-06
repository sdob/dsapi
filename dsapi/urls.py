"""dsapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

from rest_framework.authtoken import views as authtoken_views
#from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import SimpleRouter, NestedSimpleRouter
import comments.views
import divesites.views
import images.views
import profiles.views
import sitestatistics.views
from authviews.views import FacebookLogin, GoogleLogin

router = SimpleRouter()
router.register(r'comments/compressors', comments.views.CompressorCommentViewSet)
router.register(r'comments/divesites', comments.views.DivesiteCommentViewSet)
router.register(r'comments/slipways', comments.views.SlipwayCommentViewSet)

router.register(r'compressors', divesites.views.CompressorViewSet, base_name='compressor')
router.register(r'divesites', divesites.views.DivesiteViewSet, base_name='divesite')
router.register(r'dives', divesites.views.DiveViewSet)
router.register(r'slipways', divesites.views.SlipwayViewSet, base_name='slipway')
router.register(r'users', profiles.views.ProfileViewSet, base_name='profile')

compressors_router = NestedSimpleRouter(router, r'compressors', lookup='compressor')
compressors_router.register(r'images', images.views.ImageViewSet, base_name='compressor-image')

divesites_router = NestedSimpleRouter(router, r'divesites', lookup='divesite')
divesites_router.register(r'images', images.views.ImageViewSet, base_name='divesite-image')

slipways_router = NestedSimpleRouter(router, r'slipways', lookup='slipway')
slipways_router.register(r'images', images.views.ImageViewSet, base_name='slipway-image')

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^', include(compressors_router.urls)),
    url(r'^', include(divesites_router.urls)),
    url(r'^', include(slipways_router.urls)),
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    url(r'^auth/google/$', GoogleLogin.as_view(), name='google_login'),
    url(r'^accounts/', include('allauth.socialaccount.urls')),
    url(r'^statistics/$', sitestatistics.views.site_statistics),
]
