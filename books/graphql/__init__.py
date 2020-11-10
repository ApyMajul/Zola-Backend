"""
Provides the GraphQL Schema for the books app.

This __init__ file is used to collect queries and mutation within single
classes that can be directly imported by the top-level schema.
"""

import graphene

from .mutations import (
    CreateBookMutation,
    UpdateBookMutation,
    CreateWriter,
    CreateReader,
    DeleteReader,
)

from .queries import (Query, books_field, tags_field)

class Viewer(Query, graphene.ObjectType):
    """
    Defines fields that are to be merged to the top-level Viewer
    """
    books = books_field
    tags = tags_field


class Mutation(graphene.ObjectType):
    """
    Defines fields that are to be top-level mutations
    """
    create_book = CreateBookMutation.Field()
    update_book = UpdateBookMutation.Field()
    create_writer = CreateWriter.Field()
    create_reader = CreateReader.Field()
    delete_reader = DeleteReader.Field()


