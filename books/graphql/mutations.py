"""
Provides graphql mutations for the books app.
"""
from datetime import datetime

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django import forms

import graphene
from graphene_django.forms.mutation import DjangoModelFormMutation, DjangoFormMutation
from graphql import GraphQLError
from graphql_relay import from_global_id

from graphql_jwt.utils import get_payload
from graphql_jwt.decorators import login_required

from books.models import Book, Writer, Reader
from books.graphql.types import BookType, WriterType, ReaderType

from accounts.graphql.types import UserType
from lib.fields import PossiblyAbsentOrBlankCharField, TagsField

# ########## FORMS ########## #
class CreateBookForm(forms.ModelForm):
    """
    Form used by the register book mutation
    """
    class Meta:
        model = Book
        fields = ('title', 'description', 'genre', 'tags')

    writer = forms.ModelMultipleChoiceField(queryset=Writer.objects.all())

    # writer = forms.ModelChoiceField(queryset=Writer.objects.all())

    def save(self, commit: bool = True) -> Book:
        """
        Enregistre une première fois le book pour qu'il ait une id avant
        d'être relié avec un auteur
        """
        book = Book(
            title=self.instance.title,
            description=self.instance.description,
            genre=self.instance.genre,
        )

        book.save()

        return book

class UpdateBookForm(forms.Form):
    """
    Form used by the book update mutation
    """

    pk = forms.IntegerField(
        required=True,
    )

    title = forms.CharField(
        required=False,
        max_length=Book._meta.get_field('title').max_length,
    )

    writer = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Writer.objects.all(),
    )

    description = forms.CharField(
        required=False,
        max_length=Book._meta.get_field('description').max_length,
    )

    genre = forms.CharField(
        required=False,
    )

    tags = TagsField()

    ISBN = forms.CharField(
        required=False,
    )

    def save(self, info, commit: bool = True) -> Book:
        """
        Saves the changes made to the database (if any)
        """
        book = Book.objects.get(pk=self.cleaned_data['pk'])
        touched = False

        if self.cleaned_data.get('tags') is not None:
            tags = self.cleaned_data.get('tags')
            book.tags.set(*tags)

        for field in ('title', 'description', 'genre', 'ISBN'):
            if len(self.cleaned_data[field]) > 0 and (self.cleaned_data[field] != getattr(book, field)):
                setattr(book, field, self.cleaned_data[field])
                touched = True


        for field in ('writer',):
            if len(self.cleaned_data[field]) > 0 and (self.cleaned_data[field] != getattr(book, field)):
                touched = True
                if field == 'writer':
                    for w in self.cleaned_data['writer']:
                        book.writer.add(w)

        if touched:
            book.save()
        return book


# ########## MUTATIONS ########## #
class CreateBookMutation(DjangoModelFormMutation):
    """
    Mutation for book registration
    """
    class Meta:
        form_class = CreateBookForm

    book = graphene.Field(BookType)

    @classmethod
    @login_required
    def perform_mutate(cls, form: CreateBookForm, info):
        """
        Set the owner as the current user as we save the artwork.
        """
        obj = form.save(commit=False)
        obj.creation_date = timezone.now()

        for t in form.cleaned_data['tags']:
            obj.tags.add(t)

        for w in form.cleaned_data['writer']:
            obj.writer.add(w)

        obj.owner = info.context.user
        obj.save()

        return cls(errors=[], book=obj)

class UpdateBookMutation(DjangoFormMutation):
    """
    Mutation allowing the use to change book
    """
    class Meta:
        form_class = UpdateBookForm

    book = graphene.Field(BookType)

    @classmethod
    @login_required
    def perform_mutate(cls, form: UpdateBookForm, info):

        obj = form.save(info)
        obj.owner = info.context.user
        obj.save()

        kwargs = {"book": obj}
        return cls(errors=[], **kwargs)


# ########## Writer ########## #
class CreateWriter(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        link = graphene.String()
        writer_id = graphene.String(required=False)

    writer = graphene.Field(WriterType)

    def mutate(self, info, name, link, writer_id=None):
        if writer_id:
            id = from_global_id(writer_id)[1]
            writer = Writer.objects.get(pk=id)

            if name:
                writer.name = name

            if link:
                writer.link = link

            writer.save()

        else:
            writer = Writer.objects.create(
                name=name,
                link=link,
            )
        return CreateWriter(writer=writer)

# ########## Vote ########## #
class CreateReader(graphene.Mutation):
    book = graphene.Field(BookType)
    user = graphene.Field(UserType)
    status = graphene.String()

    class Arguments:
        book_id = graphene.Int()
        statuts = graphene.String()

    @login_required
    def mutate(self, info, book_id, statuts):
        user = info.context.user
        book = Book.objects.filter(pk=book_id).first()
        status = statuts

        if Reader.objects.filter(user=user.id, book=book.id).exists():
            Reader.objects.filter(user=user.id, book=book.id).update(
                status=statuts
            )

        else:
            Reader.objects.create(
                user=user,
                book=book,
                status=statuts,
            )

        return CreateReader(user=user, book=book, status=status)

class DeleteReader(graphene.Mutation):
    ok = graphene.Boolean()
    reader = graphene.Field(ReaderType)

    class Arguments:
        id = graphene.ID()

    @classmethod
    def mutate(cls, root, info, id):
        obj = Reader.objects.get(id=id)
        obj.delete()
        return cls(ok=True)

