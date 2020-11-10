"""
Provides GraphQL queries for the comment app.
"""

import graphene
import django_filters
from graphql_jwt.decorators import login_required
from django.db.models.query import QuerySet
from graphene_django.filter import DjangoFilterConnectionField

from comments.models import Comment
from .types import CommentType


# class CommentConnection(graphene.relay.Connection):
#     """A custom connection for queries on comment"""

#     class Meta:
#         node = CommentType

#     @staticmethod
#     def resolve_books(inst, info, **args) -> QuerySet:


class Query(graphene.ObjectType):
    Comments = DjangoFilterConnectionField(CommentType)
