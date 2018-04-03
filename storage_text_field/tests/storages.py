from django.core.files.base import ContentFile
from django.core.files.storage import Storage

storage = dict()


class CustomerStorage(Storage):
    def exists(self, key):
        return key in storage

    def _save(self, name, content):
        storage[name] = content.file.read()
        return name

    def _open(self, name, mode='rb'):
        return ContentFile(storage[name].encode('utf-8'))
