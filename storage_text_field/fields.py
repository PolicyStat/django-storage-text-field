import hashlib
import os

from django.core.files.base import ContentFile
from django.core.files.storage import (
    Storage,
    default_storage,
    get_storage_class,
)
from django.db import models


class StorageTextField(models.CharField):
    def __init__(self, storage=None, *args, **kwargs):
        if storage is None:
            storage = default_storage
        if not isinstance(storage, Storage):
            storage = get_storage_class(storage)()
        self.storage = storage
        kwargs['max_length'] = 200
        super(StorageTextField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(StorageTextField, self).deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def get_file_path(self, value):
        str_self = str(self).encode('utf-8')
        digest = hashlib.sha224(str_self + value.encode('utf-8')).hexdigest()
        return os.path.join(digest.encode('utf-8'), str_self)

    def get_prep_value(self, value):
        file_path = self.storage.save(
            self.get_file_path(value).decode('utf-8'),
            ContentFile(value),
        )
        return super(StorageTextField, self).get_prep_value(file_path)

    def from_db_value(self, value, expression, connection, context):
        return self.storage.open(value).read().decode('utf-8')
