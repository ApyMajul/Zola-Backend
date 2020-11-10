"""
Provides graphQL mutation for the comments app.
"""
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django import forms

from mptt.forms import TreeNodeChoiceField

import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation, DjangoFormMutation
from graphql import GraphQLError
from graphql_relay import from_global_id

from graphql_jwt.utils import get_payload
from graphql_jwt.decorators import login_required

from comments.models import Comment
from comments.graphql.types import CommentType
from books.models import Book
from books.graphql.types import BookType
from accounts.graphql.types import UserType

class CreateCommentForm(forms.ModelForm):
    """
    Form used bu create comment mutation
    """
    class Meta:
        model = Comment
        fields = ('message', 'content', 'parent',)

    content = forms.ModelChoiceField(queryset=Book.objects.all())
    parent = TreeNodeChoiceField(queryset=Comment.objects.all())

    def save(self, commit: bool = True) -> Comment:
        comment = Comment(
            message= self.instance.message,
            content = self.instance.content,
            parent = self.instance.parent,
        )

        comment.save()

        return comment

class CreateCommentMutation(DjangoModelFormMutation):
    """
    Mutation for comment creation
    """
    class Meta:
        form_class = CreateCommentForm

    comment = graphene.Field(CommentType)

    @classmethod
    @login_required
    def perfom_mutate(cls, form: CreateCommentForm, info):
        """
        set the owner, the date as we save the artwork
        """
        obj = form.save(commit=False)
        obj.publication_date = timezone.now()
        obj.owner = info.context.user
        obj.save()

        return cls(errors=[], comment=obj)
