"""
Django URL configuration

"""
import os

from django.views.static import serve
from django.conf import settings
from django.contrib import admin
from django.urls import (path, re_path)
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from accounts.views import (
    UserConfirmEmailView,
)
from .schema import schema

urlpatterns = [
    path('admin/', admin.site.urls),

    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),

    path('confirm-email', UserConfirmEmailView.as_view(), name='confirm-email'),

    re_path('^medias/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.MEDIA_ROOT)}),
]
