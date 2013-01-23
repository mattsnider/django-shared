from django.conf import settings
from django.contrib.staticfiles.finders import BaseFinder
from django.core.files.storage import FileSystemStorage


class RootDirectoryFinder(BaseFinder):
    """
    A static files finder that looks in STATIC_ROOT.
    """
    storage_class = FileSystemStorage

    def __init__(self, *args, **kwargs):
        # The list of apps that are handled
        super(RootDirectoryFinder, self).__init__(*args, **kwargs)
        self.storage = self.storage_class(location=settings.STATIC_ROOT)

    def find(self, path, all=False):
        """
        Looks for files in the app directories.
        """
        if self.storage.exists(path):
            matched_path = self.storage.path(path)
            if matched_path:
                return matched_path
        return None