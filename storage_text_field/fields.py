import hashlib
import os

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models


class StorageTextField(models.CharField):
    def __init__(self, *args, **kwargs):
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
        file_path = default_storage.save(
            self.get_file_path(value).decode('utf-8'),
            ContentFile(value),
        )
        return super(StorageTextField, self).get_prep_value(file_path)

    def from_db_value(self, value, expression, connection, context):
        return default_storage.open(value).read().decode('utf-8')
