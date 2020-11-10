"""
Views for the accounts app.

Although we have an SPA, we need those views to handle OAuth redirects and
callbacks.
"""
# pytlint will want to make class based views' methods statics, bad idea:
# pylint: disable=no-self-use
import json
from urllib.parse import urlencode
from uuid import UUID

from django.views.generic import View
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.conf import settings
from django.shortcuts import redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _

from graphql_jwt.shortcuts import get_token
# from graphql_jwt.refresh_token.shortcuts import create_refresh_token

from .models import User

class UserConfirmEmailView(View):
    """
    View used for e-mail confirmation links
    """
    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Handles GET requests.

        The e-mail activation key should be provided in the activation_key
        parameter.
        """
        activation_key = request.GET.get("activation_key", '')
        redirect_url = f"{settings.FRONTEND_BASE_URL}/{FRONTEND_EMAIL_CONFIRM_ROUTE}"
        error = None
        if len(activation_key):
            try:
                k = UUID(activation_key)
                user = User.objects.get(activation_key=k)
                if not user.confirm_email():
                    error = _("This activation key has expired")
            except (ValueError, User.DoesNotExist):
                # ValueError will be raised if the UUID is invalud
                error = _("This activation key is invalid")
        else:
            error = _("No activation key was provided")
        if error:
            redirect_url += f"?backendError={error}"
        return redirect(redirect_url)
