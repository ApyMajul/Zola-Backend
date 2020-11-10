"""
Provides the GraphQL Schema for the comment app.

This __init__ file is used to collect queries and mutation within single
classes that can be directly imported by the top-level schema.
"""

import graphene

from .mutations import (
    CreateCommentMutation,
)

from .queries import (
    Query
)

class Viewer(Query, graphene.ObjectType):
    """
    Defines fields that are to be merged to the top leve Viewer
    """
    ...

class Mutation(graphene.ObjectType):
    """
    Defines fields that are to be top-level mutations
    """
    create_comment = CreateCommentMutation.Field()
