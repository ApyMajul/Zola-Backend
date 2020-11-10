"""
Top-level GraphQL Schema

Per-app schema elements are imported here and collected via inheritance to build
the Schema instance used by graphene.
"""

import graphene
from graphene import DateTime

from accounts.graphql import Viewer as AccountsViewer
from accounts.graphql.types import PrivateUserType
from accounts.graphql import Mutation as AccountsMutation

from books.graphql import Viewer as BooksViewer
from books.graphql.types import BookType, WriterType
from books.graphql import Mutation as BooksMutation

from comments.graphql import Viewer as CommentsViewer
from comments.graphql.types import CommentType
from comments.graphql import Mutation as CommentsMutation

class Viewer(AccountsViewer, BooksViewer, CommentsViewer, graphene.ObjectType):
    """
    The viewer field is used as a root field for all queries (i.e all queries
    are fields of viewer). Have this class inherit the Viewer defined in your
    class to add its field to the schema
    """
    current_user = graphene.Field(PrivateUserType)
    is_logged_in = graphene.Field(graphene.Boolean)

    class Meta:
        interfaces = (graphene.relay.Node,)

class Query(graphene.ObjectType):
    """
    The top-level query only exposes Relay's Node and the viewer, other
    queries should be defined as fields on Viewer.
    """
    node = graphene.relay.Node.Field()
    viewer = graphene.Field(Viewer)

    def resolve_viewer(self, info):
        #pylint: disable=no-self-use
        """
        The Viewer always resolves to the current logged-in user or the default
        anonymous user
        """
        if info.context.user.is_anonymous:
            return Viewer(current_user=None, is_logged_in=False)
        return Viewer(current_user=info.context.user, is_logged_in=True)

class Mutation(AccountsMutation, BooksMutation, CommentsMutation):
    """
    Have this class inherit your module's Mutation class to add mutations to
    the schem.
    """
    ...

schema = graphene.Schema(query=Query, mutation=Mutation, types=[DateTime])
