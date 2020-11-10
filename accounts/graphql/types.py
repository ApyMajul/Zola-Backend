"""
Provides GraphQL types for the accounts app.
"""

import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from taggit.models import Tag
from taggit.managers import TaggableManager
from accounts.models import User

@convert_django_field.register(TaggableManager)
def convert_tags_to_list_of_string(field, registry=None):
    """
    Conver tags object into a list of string.
    """
    return graphene.List(graphene.String, source='get_tags')

class UserType(DjangoObjectType):
    """
    A type for the "public" representation of a user
    """
    class Meta:
        model = User
        interfaces = (graphene.relay.Node,)
        use_connection = False
        only_fields = (
            'pk',
            'username',
            'short_description',
            'tags',
            'location',
            'location_id',
            'first_name',
            'last_name',
            'avatar',
        )

    pk = graphene.String(source='pk')
    similar_users = graphene.List(lambda: UserType)

    def resolve_avatar(self, info) -> str:
        """
        Resolves the avatar field.
        """
        return self.avatar.url

    def resolve_similar_users(self, info):
        """
        Users tagged similarly to the requested user.
        """
        return self.tags.similar_objects()

class PrivateUserType(DjangoObjectType):
    """
    A type of the "private" representation of a user.

    Provides more data that public UserType, meant to be used when
    requesting a user's own account (i.e for the viewer field).
    """
    class Meta:
        model = User
        interfaces = (graphene.relay.Node,)
        use_connection = False
        filter_fields = ['username']
        only_fields = (
            'pk',
            'email',
            'username',
            'short_description',
            'tags',
            'location',
            'location_id',
            'first_name',
            'last_name',
            'avatar',
            'is_staff',
            'confirmed_email',
            'is_superuser',
            'date_joined',
            'date_updated',
        )

    pk = graphene.String(source='pk')
    has_password = graphene.Boolean()

    def resolve_has_password(self, info) -> bool:
        """
        Resolves the has_password field.
        """
        return self is not None and self.has_usable_password()

    def resolve_avatar(self, info) -> str:
        """
        Resolves the avatar field.
        """
        if self.avatar is not None:
            return self.avatar.url
        return ''

class UserOrderBy(graphene.Enum):
    """
    This provides the schema's UserOrderBy Enum type, for ordering UserConnection.

    The class name ('UserOrderBy') is what the GraphQL schema Enum type name should be, the
    left-hand side below is what the Enum values should be, and the right-hand side is what our
    resolver will receive.
    """

    firstName_ASC = 'first_name'
    firstName_DESC = '-first_name'
    lastName_ASC = 'last_name'
    lastName_DESC = '-last_name'
    email_ASC = 'email'
    email_DESC = '-email'
    username_ASC = 'username'
    username_DESC = '-username'
    dateJoined_ASC = 'date_joined'
    dateJoined_DESC = '-date_joined'

class TagsType(DjangoObjectType):
    """
    A type for the representation of a tag used bu the User model.
    """
    class Meta:
        model = Tag
        interfaces = (graphene.relay.Node,)
        use_connection = False
        only_fields = (
            'pk',
            'slug',
            'name',
        )

    pk = graphene.String(source='pk')
    tagged_users = graphene.Int()

    def resolve_tagged_users(self, info) -> int:
        """
        Resolves the number of users tagged with this tag.
        """
        return self.accounts_taggeduser_items.count()
