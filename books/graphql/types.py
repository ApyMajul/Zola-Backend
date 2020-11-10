"""
Provides GraphQL types for the books app.
"""

import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from taggit.models import Tag
from taggit.managers import TaggableManager
from books.models import Book, Writer, Reader, Reader

@convert_django_field.register(TaggableManager)
def convert_tags_to_list_of_string(field, registry=None):
    """
    Convert tags objects into a list of string
    """
    return graphene.List(graphene.String, source='get_tags')

class WriterType(DjangoObjectType):
    """
    A type for the writer
    """
    class Meta:
        model = Writer
        interfaces = (graphene.relay.Node,)
        fields = ('name', 'link', 'pk',)
        filter_fields = {
            'name': ['exact', 'icontains'],
            'link': ['exact', 'icontains'],
        }

    pk = graphene.String(source='pk')

class ReaderType(DjangoObjectType):
    """
    A type for the Reader
    """
    class Meta:
        model = Reader
        interfaces = (graphene.relay.Node,)
        fields = ('book', 'user', 'status', 'pk',)
        filter_fields = {
            'user': ['exact',],
            'book': ['exact',],
            'status': ['exact',],
        }

    pk = graphene.String(source='pk')

class BookType(DjangoObjectType):
    """
    A type for the book
    """
    class Meta:
        model = Book
        interfaces = (graphene.relay.Node,)
        use_connection = False
        fields = ('title', 'description', 'genre', 'owner', 'tags', 'pk',)
        filter_fields = {
            'title': ['exact', 'icontains', 'istartwith'],
            'genre': ['exact', 'icontains', 'istartwith'],
            'owner': ['exact', 'icontains', 'istartwith'],
        }

    writer = graphene.Field(graphene.List(WriterType))
    pk = graphene.String(source='pk')
    similar_books = graphene.List(lambda: BookType)
    reader = graphene.Field(graphene.List(ReaderType))

    def resolve_writer(self, info) -> str:
        return self.writer.all()

    def resolve_reader(self, info) -> str:
        #readers_book renvoi tous les objets user associés au livre via reader
        readers_book = self.reader.all()
        readers_objects = []

        for person in readers_book:
            #pour chaque user associé au livre je fais chercher l'objet reader
            x = Reader.objects.get(book=self, user=person)
            readers_objects.append(x)

        return readers_objects

    def resolve_similar_books(self, info):
        """
        books taged similarly to the requested user.
        """
        return self.tags.similar_objects()

class BookOrderBy(graphene.Enum):
    """
    This provides the schema's BookOrderBy Enum type, for oredering BookConnection.

    The class name is what the GraphQl scheam Enum type name should be, the
    left-hand side below is what the Enum values should be, and the right-hand side is what our
    resolver will receive.
    """

    title_ASC = 'title'
    title_DESC = '-title'
    writer_ASC = 'writer'
    writer_DESC = '-writer'
    genre_ASC = 'genre'
    genre_DESC = '-genre'
    publicationDate_ASC = 'publication_date'
    publicationDate_DESC = '-publication_date'
    owner_ASC = 'owner'
    owner_DESC = '-owner'
    creationDate_ASC = 'creation_date'
    creationDate_DESC = '-creation_date'

class TagsType(DjangoObjectType):
    """
    A type for the representation of a tag used by the book model.
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
    tagged_books = graphene.Int()

    def resolve_tagged_books(self, info) -> int:
        """
        Resolves the number of users tagged with this tag
        """
        return self.books_taggedbook_item.count()
