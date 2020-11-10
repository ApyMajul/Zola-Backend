"""
Django storage class overide
"""

from django.core.files.storage import get_storage_class


class OverwriteStorage(get_storage_class()):
    """
    Django storage class overide. It replace a file if one have the same name
    """

    def _save(self, name, content):
        """
        Remove file with the same name
        """
        self.delete(name)
        return super(OverwriteStorage, self)._save(name, content)

    @staticmethod
    def get_available_name(name, max_length=None):
        """
        Get the file name
        """
        # pylint: disable=unused-argument
        return name
