"""
Provides graphql mutations for the accounts app.
"""
import json
import urllib
import base64

from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.shortcuts import reverse
from django.core.files.base import ContentFile

import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation, DjangoFormMutation
from graphql import GraphQLError

from graphql_jwt.mixins import VerifyMixin
from graphql_jwt.utils import get_payload
from graphql_jwt.relay import JSONWebTokenMutation
from graphql_jwt.refresh_token.signals import refresh_token_rotated
from graphql_jwt.decorators import login_required

from constants.fields import USERNAME_BLACKLIST
from accounts.models import User
from accounts.graphql.types import PrivateUserType
from lib.fields import PossiblyAbsentOrBlankCharField, TagsField

# Make sure that a refresh token is revoken when used:
@receiver(refresh_token_rotated)
def revoke_refresh_token(sender, refresh_token, **kwargs):
    """
    Automatically revoke a refresh token after it has been used
    See the django-graphql-jwt docs
    """
    refresh_token.revoke()


# ########## FORMS ########## #


class RegisterUserForm(forms.ModelForm):
    """
    Form used by the register user mutation
    """
    class Meta:
        model = User
        fields = ('email',)

    password = forms.CharField(required=True)

    def save(self, commit: bool = True) -> User:
        """
        Validates the captcha and saves the newly registered user to the
        database.
        """
        user = User.objects.create_user(
            email=self.instance.email,
            username=self.generate_username_from_email(),
            password=self.cleaned_data['password'],
        )
        return user

    def clean_password(self) -> str:
        """
        Validates the password. Ensures that it is conformrs to the password policy.
        """
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError(_(
                "The password must be at least 8 characters long."
            ))

        first_isalpha = password[0].isalpha()
        if all(c.isalpha() == first_isalpha for c in password):
            raise forms.ValidationError(_(
                "The password must contain at least"
                "one letter and at least one digit or punctuation character."
            ))

        return password

    # def clean_username(self) -> str:
    #     """
    #     Validates the username. Ensures that:

    #     - it is valid (length and characters)
    #     - it is not blacklisted
    #     - it is not already in use
    #     """
    #     username = self.cleaned_data.get('username')

    #     if User.objects.filter(username=username).exists() or username.lower() in USERNAME_BLACKLIST:
    #         raise forms.ValidationError(_("This username is already taken."))

    #     return username

    def generate_username_from_email(self) -> str:
        """
        Generate the username using the provided email. Ensures that:

        - it is valid (length and characters)
        - it is not blacklisted
        - it is not already in use
        """
        username = self.instance.email.split("@")[0]

        i = 0
        while User.objects.filter(username=username).exists() or username.lower() in USERNAME_BLACKLIST:
            i += 1
            #make sure username + number isnt over 20 characters
            username = username[:20-len(str(i))] + str(i)

        while len(username)<3:
            username = username + "_"

        return username

class ProfileSettingsForm(forms.Form):
    """
    For used by profile settings mutation.
    """
    short_description = PossiblyAbsentOrBlankCharField(
        max_length=User._meta.get_field('short_description').max_length
    )

    tags = TagsField()

    location = PossiblyAbsentOrBlankCharField(
        max_length=User._meta.get_field('location').max_length
    )

    location_id = PossiblyAbsentOrBlankCharField(
        max_length=User._meta.get_field('location_id').max_length,
    )

    avatar = forms.CharField(
        required=False,
    )

    email = PossiblyAbsentOrBlankCharField(
        max_length=User._meta.get_field('email').max_length
    )

    first_name = PossiblyAbsentOrBlankCharField(
        max_length=User._meta.get_field('first_name').max_length
    )

    last_name = PossiblyAbsentOrBlankCharField(
        max_length=User._meta.get_field('last_name').max_length,
    )

    def clean_avatar(self) -> str:
        """
        Add some custom validation to our avatar field
        """
        avatar = self.cleaned_data.get('avatar', None)
        if avatar is not None:
            avatar_size = (len(avatar) * 3) / 4 - avatar.count('=', -2)
            if avatar_size > settings.MAX_FILE_SIZES["avatar"]:
                raise forms.ValidationError(_("Image file too large"))
        return avatar


    def save(self, info, commit: bool = True) -> User:
        """
        Saves the changes made to the database (if any)
        """
        user = info.context.user
        touched = False

        if self.cleaned_data.get('tags') is not None:
            tags = self.cleaned_data.get('tags')
            user.tags.set(*tags)

        for field in ('first_name', 'last_name', 'short_description', 'location', 'location_id', 'email'):
            # Here, we must use cleaned_data.get() method instead of cleaned_data[], because
            # ... cleaned_data[] will raise a KeyError, while cleaned_data.get() will return None.
            # see: http://bit.ly/2Zfxcrr
            if (self.cleaned_data.get(field) is not None and self.cleaned_data.get(field) != getattr(user, field)):
                # If the field value is an empty string, we consider it as a valid update motif.
                # ... But if the value is None, it means that the field was absent in the request,
                # ... therefore we don't update it.
                setattr(user, field, self.cleaned_data[field])
                touched = True
        for field in ('avatar'):
            if len(self.cleaned_data[field]) > 0 and (self.cleaned_data[field] != getattr(user, field)):
                # we check the length because django "normalizes" the value of
                # absent non-required char/choice fields to empty strings
                setattr(user, field, self.cleaned_data[field])
                touched = True
                if field == 'avatar':
                    fileformat, imgstr = self.cleaned_data[field].split(';base64,')
                    ext = fileformat.split('/')[-1]
                    avatar = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
                    setattr(user, field, avatar)
        if touched:
            user.save()
        return info.context.user


class SetPasswordForm(forms.Form):
    """
    Form used by the set password mutation. Can be used to set a password for
    the first time or changing an existing password
    """
    old_password = forms.CharField(required=False)
    new_password = forms.CharField(required=True)

    def save(self, info, commit: bool = True) -> User:
        """
        Verifies that the user either has provided their valid current password
        or doesn't yet have a password before saving the new password.
        """
        user = info.context.user
        valid_password_for_user = user.has_usable_password() and user.check_password(self.cleaned_data["old_password"])
        if valid_password_for_user or not user.has_usable_password():
            user.set_password(self.cleaned_data["new_password"])
        else:
            raise GraphQLError(_("Incorrect previous password"))
        user.save()
        return user


# ########## MUTATIONS ########## #


class ObtainJSONWebToken(JSONWebTokenMutation):
    """
    Login mutation provided bu django-grapql-jwt. Subclassed to have it return
    the logged-in user
    """
    user = graphene.Field(PrivateUserType)

    @classmethod
    def resolve(cls, root, info, **kwargs):
        """
        overloaded to redutrn the logged-in user on login
        """
        return cls(user=info.context.user)

class Verify(VerifyMixin, graphene.ClientIDMutation):
    """
    Verify the token mutation provided by django-graphql-jwt, subclassed to return
    the token's owner
    """
    user = graphene.Field(PrivateUserType)

    class Input:
        token = graphene.String(required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, token, **kwargs):
        """
        Overloaded to determine the owener form the payload and return it.
        """
        payload = get_payload(token, info.context)
        user = User.objects.get(email=payload["email"])
        return cls(payload=payload, user=user)

class RegisterUserMutation(DjangoModelFormMutation):
    """
    Mutation for user registration
    """
    class Meta:
        form_class = RegisterUserForm

    user = graphene.Field(PrivateUserType)

class ProfileSettingsMutation(DjangoFormMutation):
    """
    Mutation allowing the current user to set their profile options.
    """
    class Meta:
        form_class = ProfileSettingsForm

    user = graphene.Field(PrivateUserType)

    @classmethod
    @login_required
    def perform_mutate(cls, form: ProfileSettingsForm, info):
        """
        Overloaded to make the mutation require a logged-in user and pass said
        user to the underlying form's save() method.
        """
        obj = form.save(info)
        kwargs = {"user": obj}
        return cls(errors=[], **kwargs)

class SetPasswordMutation(DjangoFormMutation):
    """
    Mutation allowing the current user to set/change their password
    """
    class Meta:
        form_class = SetPasswordForm

    user = graphene.Field(PrivateUserType)

    @classmethod
    @login_required
    def perform_mutate(cls, form: SetPasswordForm, info):
        """
        Overloaded to make the mutation require a logged-in user and pass said
        user to underlying form's save() method;
        """
        obj = form.save(info)
        kwargs = {"user":obj}
        return cls(errors=[], **kwargs)
