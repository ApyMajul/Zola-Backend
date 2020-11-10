"""
Provides GraphQL types for the comments app.
"""

import graphene
from graphene_django import DjangoObjectType
from comments.models import Comment
from accounts.graphql.types import UserType

class CommentType(DjangoObjectType):
    """
    A type for the comment
    """
    class Meta:
        model = Comment
        interfaces = (graphene.relay.Node,)
        fields = ('message', 'publication_date', 'owner', 'content', 'parent', 'pk')
        filter_fields = {
            'publication_date': ['exact',],
            'owner': ['exact',],
            'content': ['exact',],
        }

    # upvotes = graphene.Field(graphene.List(UserType))
    # downvotes = graphene.Field(graphene.List(UserType))
    pk = graphene.String(source='pk')

    # def resolve_upvotes(self, info) -> str:
    #     return self.upvotes.all()

    # def resolve_downvotes(self, info) -> str:
    #     return self.downvotes.all()

    # def resolve_user_vote(self, info) -> str:
    #     """
    #     Resolves user vote exist on this comment.
    #     """
    #     if user.info in self.upvotes.all():
    #         return 'user in upvotes'
    #     elif user.info in self.downvotes.all():
    #         return 'user in downvotes'
    #     else:
    #         return ''
