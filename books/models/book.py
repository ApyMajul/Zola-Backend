"""
Books Model
"""
import os.path

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from books.mixins import ReaderMixin

from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase

def upload_path_handler_cover(instance, filename):
    """
    Cover upload default path
    """
    fn, ext = os.path.splitext(filename)
    return "cover/{id}{ext}".format(id=instance.pk, ext=ext)


class TaggedBook(TaggedItemBase):
    """
    Intermediary model as a subclass of taggit.models.TaggedItemBase with a
    foreign key to Book model.
    """
    content_object = models.ForeignKey('Book', on_delete=models.CASCADE)


class Book(models.Model):
    """
    Book model
    """

    GENRE = [
        ('sf', 'Science Fiction'),
        ('theatre', 'Theatre'),
        ('poesie', 'Poésie'),
        ('nouvelle', 'Nouvelle'),
        ('bd', 'Bande Dessinée'),
        ('manga', 'Manga'),
    ]

    title =  models.CharField(
        verbose_name=_('Title'),
        max_length=150,
        null=False,
        blank=False)

    writer = models.ManyToManyField(
        'books.writer',
        blank=False,
        verbose_name=_('Writers'))

    tags = TaggableManager(
        through=TaggedBook,
        verbose_name=_('tags'),
        blank=True,
    )

    description = models.TextField(
        verbose_name=_('Description'),
        max_length=5000,
        null=True,
        blank=True)

    genre = models.CharField(
        verbose_name=_('Genre'),
        choices=GENRE,
        max_length=150,
        null=True,
        blank=True,
    )

    publisher =  models.CharField(
        verbose_name=_('Editor'),
        max_length=150,
        null=True,
        blank=True)

    cover = models.ImageField(
        verbose_name=_('Cover'),
        upload_to=upload_path_handler_cover,
        null=True,
        blank=True,
    )

    publication_date = models.CharField(
        verbose_name=_('Year of parution'),
        max_length=4,
        null=True,
        blank=True,
    )

    pages = models.CharField(
        verbose_name=_('Number of pages'),
        max_length=5,
        null=True,
        blank=True,
    )

    ISBN = models.CharField(
        verbose_name=_('ISBN code'),
        # min_length=10,
        max_length=13,
        null=True,
        blank=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owner',
        null=True,
        verbose_name=_('Owner'))

    creation_date=models.DateTimeField(
        _('Creation date'),
        auto_now_add=True,
    )

    reader = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='books.Reader',
    )

    def __str__(self):
        return self.title

    @property
    def get_tags(self):
        return self.tags.all()

    class Meta:
        ordering = ('title', 'publication_date',)


class Writer(models.Model):
    name = models.CharField(
        verbose_name=_('Author'),
        max_length=150,
        unique=True,
        null=False,
        blank=False,
    )

    link = models.URLField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

class Reader(models.Model):

    TYPE = [
        ('wish', 'Whish List'),
        ('read', 'Read List'),
        ('like', 'Like List'),
    ]

    class Meta:
        unique_together = [['user', 'book']]

    def __str__(self):
        return self.status

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=('User'),
        on_delete=models.CASCADE
    )

    book = models.ForeignKey(
        'books.Book',
        related_name='readers_books',
        verbose_name=('Book'),
        on_delete=models.CASCADE
    )

    status = models.CharField(
        verbose_name=_('Status'),
        choices=TYPE,
        max_length=150,
        null=False,
        blank=False,
        default='wish',
    )
