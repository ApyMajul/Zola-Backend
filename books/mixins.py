"""
Mixins
"""

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
import operator

class ReaderMixin(models.Model):

    class Meta:
        abstract = True


    def get_reader_book(self):
        print("hihouuuuuuuuuuuuuuuuuuuuuuuu", self)
        # qs = list(qs)
        # print(qs)

        # readers = []
        # for x in qs:
        #     attr = getattr(self, 'reader_book', None)
        #     print(getattr(self, 'reader_book', None))
        #     return attr

        print(type(getattr(self, 'reader_book', None)))
        print(getattr(self, 'reader_book', None))

