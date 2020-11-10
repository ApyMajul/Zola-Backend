from __future__ import annotations
import uuid
from datetime import timedelta
from typing import Optional, Union
import os.path
import io
from PIL import Image as Img
from unidecode import unidecode
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.staticfiles.storage import staticfiles_storage

from constants.fields import USERNAME_BLACKLIST
from lib.exceptions import LeviathanRegistrationException
from lib.storage import OverwriteStorage


def upload_path_handler_avatar(instance, filename):
    """
    Avatar upload default path
    """
    fn, ext = os.path.splitext(filename)
    return "avatar/{id}{ext}".format(id=instance.pk, ext=ext)

class TaggedUser(TaggedItemBase):
    """
    Intermediary model as a subclass of taggit.models.TaggedItemBase with a
    foreign key to User model.
    """
    content_object = models.ForeignKey('User', on_delete=models.CASCADE)

class LeviathanUserManager(BaseUserManager):
    """
    Replaces the default user manager (User.objects), providing shortcuts for
    creating users with different presets
    """

    @staticmethod
    def _duplicate_default_avatar(username: str):
        image = Img.open(staticfiles_storage.path('images/avatar.png'))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.thumbnail((512, 512), Img.ANTIALIAS)
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=100)
        output.seek(0)
        default_avatar = InMemoryUploadedFile(
            output,
            'ImageField',
            "%s.jpg" % str(username),
            'image/jpeg',
            output.getbuffer().nbytes,
            None)
        if not default_avatar:
            raise LeviathanRegistrationException(f"Missing default avatar in static files folder.")
        return default_avatar

    def _create_user(
        self,
        email: str,
        username: str,
        password: str,
        is_staff: bool,
        is_superuser: bool,
        **extra_fields
    ):
        """
        Create and save an User with the given email, password, name and  phone number
        """
        now = timezone.now()
        email = self.normalize_email(email)
        avatar = self._duplicate_default_avatar(username)

        user = self.model(
            email=email.strip().lower(),
            username=username,
            is_staff=is_staff,
            is_active=True,
            is_superuser=is_superuser,
            last_login=now,
            date_joined=now,
            avatar=avatar,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, username: str, password: str, **extra_fields):
        """
        Create and save an User with the given email, password and name.
        """

        return self._create_user(
            email,
            username,
            password,
            is_staff=False,
            is_superuser=False,
            **extra_fields
        )

    # def create_facebook_user(...)

    def create_superuser(
        self,
        email: str,
        username: str,
        password: Optionnal[str] = None,
        **extra_fields
    ):
        """
        Create a super user
        """
        if not email:
            raise ValueError('User must have an email')
        if not password:
            raise ValueError('User must have a password')

        return self._create_user(
            email,
            username,
            password,
            is_staff=True,
            is_superuser=True,
            **extra_fields
        )

class User(AbstractBaseUser, PermissionsMixin):
    """
    Model that represents an user.

    To be active, the user must register and confirm his email.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )


    readers = models.ManyToManyField(
        'books.Book',
        through='books.Reader',
    )

    username = models.CharField(
        verbose_name=_('Username'),
        max_length=20,
        unique=True,
        null=False,
        default=None,
    )

    avatar = models.ImageField(
        verbose_name=_('avatar'),
        storage=OverwriteStorage(),
        upload_to=upload_path_handler_avatar,
        null=True,
        blank=True,
    )

    short_description = models.TextField(
        verbose_name=_('Short description'),
        max_length=300,
        blank=True,
    )

    tags = TaggableManager(
        through=TaggedUser,
        verbose_name=_('tags'),
        blank=True,
    )

    location_id = models.CharField(
        verbose_name=_('Location ID'),
        max_length=100,
        blank=True,
    )

    location = models.CharField(
        verbose_name=_('Location'),
        max_length=300,
        blank=True,
    )

    email = models.EmailField(
        _('Email adress'),
        unique=True,
    )

    first_name = models.CharField(
        _('First Name'),
        max_length=50,
        blank=True,
    )

    last_name = models.CharField(
        _('Last Name'),
        max_length=50,
        blank=True,
    )

    confirmed_email = models.BooleanField(
        _('Confirmed email'),
        default=False,
    )

    is_staff = models.BooleanField(
        _('Staff status'),
        default=False,
    )

    is_superuser = models.BooleanField(
        _('Superuser status'),
        default=False,
    )

    is_active = models.BooleanField(
        _('Active'),
        default=True,
    )

    date_joined = models.DateTimeField(
        _('Date joined'),
        auto_now_add=True
    )

    date_updated= models.DateTimeField(
        _('Date updated'),
        auto_now=True
    )

    activation_key = models.UUIDField(
        _('Activation key'),
        unique=True,
        default=uuid.uuid4,
    )

    facebook_id = models.BigIntegerField(
        _('Facebook ID'),
        unique=True,
        null=True,
        default=None,
    )

    USERNAME_FIELD = 'email'

    objects = LeviathanUserManager()

    def __str__(self):
        """
        Unicode representation fo an user model
        """

        return self.email

    def get_full_name(self) -> str:
        """
        Return the first_name plus the last_name with a space between
        """

        return "{0} {1}".format(self.first_name, self.last_name)

    def get_whort_name(self) -> str:
        """
        Return the first_name.
        """

        return self.first_name

    def activation_expired(self) -> bool:
        """
        Check if user's activation has expired.
        """

        return self.date_joined + timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS) < timezone.now()

    def confirm_email(self) -> bool:
        """
        Confirm email.
        """

        if not self.activation_expired() and not self.confirmed_email:
            self.confirmed_email = True
            self.save()
            return True
        return False

    @property
    def get_tags(self):
        """
        Get user's tags
        """
        return self.tags.all()

    def save(self, *args, **kwargs):
        """
        Save user model
        """
        try:
            if self.avatar and self.avatar != (str(self.pk) + '.jpg'):
                image = Img.open(io.BytesIO(self.avatar.read()))
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.thumbnail((self.avatar.width, self.avatar.height), Img.ANTIALIAS)
                output = io.BytesIO()
                image.save(output, format='JPEG', quality=100)
                output.seek(0)
                self.avatar = InMemoryUploadedFile(
                    output,
                    'ImageField',
                    "%s.jpg" % str(self.pk),
                    'image/jpeg',
                    output.getbuffer().nbytes,
                    None)

        except Exception as e:
            print('User avatar updates error:"', str(e))

        super(User, self).save(*args, **kwargs)
