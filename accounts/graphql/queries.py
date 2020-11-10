"""
Provides GraphQL queries for the accounts app.
"""
import operator
from functools import reduce

import graphene
from graphql_jwt.decorators import login_required
from graphql import GraphQLError
from django.db.models import Q
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from accounts.models import User
from .types import UserType, UserOrderBy, TagsType


class UserConnection(graphene.relay.Connection):
    """A custom Connection for queries on User."""

    class Meta:
        node = UserType

    @staticmethod
    def get_users_input_fields() -> dict:
        """
        this creates an input field using the UserOrderBy custom enum
        """
        return {
            'order_by': graphene.Argument(UserOrderBy),
            'username': graphene.String(),
            'tags': graphene.List(graphene.String),
        }

    @staticmethod
    def resolve_users(inst, info, **args) -> QuerySet:
        """
        Resolves the users query
        """
        qs = User.objects.all()

        username = args.get('username', None)
        tags = args.get('tags', None)
        order_by = args.get('order_by', None)

        if tags and username:
            raise GraphQLError(_("'tags' and 'username' inputs cannot be used together."))

        if tags:
            qs = qs.filter(reduce(operator.or_, (Q(tags__name__contains=x) for x in tags))).distinct()

        if username:
            return qs.filter(username=username)

        if order_by:
            # Graphene has already translated the over-the-wire enum value (e.g. 'createdAt_DESC')
            # to our internal value ('-created_at') needed by Django.
            qs = qs.order_by(order_by)

        return qs


class Query(graphene.ObjectType):
    """
    Fields for accounts-related queries (will be subfields of the top-level
    viewer.
    """
    chat_token = graphene.Field(graphene.String)

    @staticmethod
    @login_required
    def resolve_chat_token(inst, info, **args) -> str:
        """
        Provides an up-to-date chat token for the currently logged-in user.
        """
        # pylint: disable=unused-argument
        return info.context.user.get_chat_token()


users_field = graphene.relay.ConnectionField(
    UserConnection,
    resolver=UserConnection.resolve_users,
    **UserConnection.get_users_input_fields()
)

class TagsConnection(graphene.relay.Connection):
    """A custom Connection for queries on users tags. """

    class Meta:
        node = TagsType

    @staticmethod
    def get_tags_input_fields() -> dict:
        """
        this creates an înput field.
        """
        return {
            'name': graphene.String(),
        }

    @staticmethod
    def resolve_tags(inst, info, **args) -> QuerySet:
        """
        Resolves the most common tag query, filtered bu name
        """
        qs =  User.tags.most_common()

        name = args.get('name', None)

        if name:
            qs = qs.filter(name__contains=name)

        return qs

tags_field = graphene.relay.ConnectionField(
    TagsConnection,
    resolver=TagsConnection.resolve_tags,
    **TagsConnection.get_tags_input_fields()
)
