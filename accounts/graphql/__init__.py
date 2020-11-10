"""
Provides the GraphQL Schema for the Accounts app.

This __init__ file is used to collect queries and mutation within single
classes that can be directly imported by the top-level schhema.
"""

import graphene
import graphql_jwt

from .mutations import (
    RegisterUserMutation,
    ProfileSettingsMutation,
    SetPasswordMutation,
)
from .mutations import (ObtainJSONWebToken, Verify)
from .queries import (Query, users_field, tags_field)


class Viewer(Query, graphene.ObjectType):
    """
    Defines fields that are to be merged to the top-level Viewer
    """
    users = users_field
    # tags = tags_field


class Mutation(graphene.ObjectType):
    """
    Defines fields that are to be top-level mutations
    """
    create_user = RegisterUserMutation.Field()
    profile_settings = ProfileSettingsMutation.Field()
    set_password = SetPasswordMutation.Field()

    token_auth = ObtainJSONWebToken.Field()
    verify_token = Verify.Field()
    refresh_token = graphql_jwt.relay.Refresh.Field()
    revoke_token = graphql_jwt.relay.Revoke.Field()
