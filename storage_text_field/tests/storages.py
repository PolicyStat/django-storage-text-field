from django.core.files.base import ContentFile
from django.core.files.storage import Storage

storage = dict()


class CustomStorage(Storage):
    def exists(self, key):
        return key in storage

    def _save(self, name, content):
        if self.exists(name):
            # We need to show that _save is not called if the file already
            # exists.
            raise AssertionError('This is not supposed to happen')
        storage[name] = content.file.read()
        return name

    def _open(self, name, mode='rb'):
        return ContentFile(storage[name].encode('utf-8'))
