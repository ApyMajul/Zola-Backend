"""
Comments Model
"""
import os.path

from django.db import models
from django.db.models import Count
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey

class Comment(MPTTModel):
    """
    Comment Model
    """
    message = models.TextField(
        verbose_name=_('Message'),
        max_length=255,
        null=False,
        blank=False,
    )

    publication_date=models.DateTimeField(
        verbose_name=_('Publication date'),
        auto_now_add=True,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        verbose_name=_('Owner')
    )

    content=models.ForeignKey(
        'books.book',
        on_delete=models.PROTECT,
        null=False,
        verbose_name=_('Content')
    )

    parent = TreeForeignKey(
        'self',
        null=True,
        blank=True,
        related_name="sub_comment",
        on_delete=models.PROTECT,
    )

    # upvotes=models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     blank=False,
    #     verbose_name=_('Up Votes')
    # )

    # downvotes=models.ManyToManyField(
    #     settings.AUTH_USER_MODEL,
    #     blank=False,
    #     verbose_name=_('Down Votes')
    # )

    # objects = models.Manager()
    # tree = TreeManager()

    class Meta:
        ordering = ('publication_date',)

    # def get_score(self) -> str:
    #     """
    #     Return la différence entre nombre d'up et de down votes
    #     """
    #     return self.upvotes.count() - self.downvotes.count()

    def get_all_children(self, include_self=False):
        """
        Gets all of the comment thread.
        """
        children_list = self._recurse_for_children(self)
        if include_self:
            ix = 0
        else:
            ix = 1
        flat_list = self._flatten(children_list[ix:])
        return flat_list

    def _recurse_for_children(self, node):
        children= []
        children.append(node)
        for child in node.sub_comment.enabled():
            if child != self:
                children_list = self._recurse_for_children(child)
                children.append(children_list)
        return children

    def _flatten(self, L):
        if type(L) != type([]): return [L]
        if L == []: return L
        return self._flatten(L[0]) + self._flatten(L[1:])
