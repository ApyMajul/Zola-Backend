"""
Provides GraphQL queries for the book app.
"""

import graphene
import django_filters
from graphql_jwt.decorators import login_required
from django.db.models.query import QuerySet
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError

from books.models import Book, Writer, Reader, Reader
from .types import BookType, WriterType, BookOrderBy, ReaderType, TagsType


class BookConnection(graphene.relay.Connection):
    """A custom connection for queries on book"""

    class Meta:
        node = BookType

    @staticmethod
    def get_book_input_fields() -> dict:
        """
        this creates an input field using the BookOrderBy custom enum
        """
        return {
            'order_by': graphene.Argument(BookOrderBy),
            'title': graphene.String(),
            'tags': graphene.List(graphene.String),
        }

    @staticmethod
    def resolve_books(inst, info, **args) -> QuerySet:
        """
        Resolves the books query
        """
        qs = Book.objects.all()

        title = args.get('title', None)
        tags = args.get('tags', None)
        order_by = args.get('order_by', None)

        if tags and title:
            raise GraphQLError(_("'tags' and title inputs cannot be used together."))

        if tags:
            qs = qs.filter(reduce(operator.or_, (Q(tags__name__contains=x) for x in tags))).distinct()

        if title:
            return qs.filter(title=title)

        if order_by:
            qs =qs.order_by(order_by)

        return qs


class Query(graphene.ObjectType):
    writer = graphene.relay.Node.Field(WriterType)
    writers = DjangoFilterConnectionField(WriterType)
    Reader = DjangoFilterConnectionField(ReaderType)


books_field = graphene.relay.ConnectionField(
    BookConnection,
    resolver=BookConnection.resolve_books,
    **BookConnection.get_book_input_fields()
)

class TagsConnection(graphene.relay.Connection):
    """A custom connection for queries on books tags. """

    class Meta:
        node = TagsType

    @staticmethod
    def get_tags_input_fields() -> dict:
        """
        this creates an input fields.
        """
        return {
            'name': graphene.String(),
        }

    @staticmethod
    def resolve_tags(inst, info, **args) -> QuerySet:
        """
        Resolves the most common tag query, filtered by name
        """
        qs = Book.tags.most_common()

        name = args.get('name', None)

        if name:
            qs = qs.filter(name__contains=name)

        return qs

tags_field = graphene.relay.ConnectionField(
    TagsConnection,
    resolver=TagsConnection.resolve_tags,
    **TagsConnection.get_tags_input_fields()
)
