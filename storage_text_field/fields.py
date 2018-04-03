import hashlib
import os

from django.core.files.base import ContentFile
from django.core.files.storage import (
    Storage,
    default_storage,
    get_storage_class,
)
from django.db import models


def default_pre_save_hook(value):
    return value


def default_from_db_hook(value):
    return value


class StorageTextField(models.CharField):
    def __init__(
            self,
            storage=None,
            pre_save_hook=None,
            from_db_hook=None,
            *args,
            **kwargs
    ):
        if storage is None:
            storage = default_storage
        if not isinstance(storage, Storage):
            storage = get_storage_class(storage)()
        if not pre_save_hook:
            pre_save_hook = default_pre_save_hook
        if not from_db_hook:
            from_db_hook = default_from_db_hook
        self.storage = storage
        self.pre_save_hook = pre_save_hook
        self.from_db_hook = from_db_hook
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
        value = self.pre_save_hook(value)
        file_path = self.get_file_path(value).decode('utf-8')
        if not self.storage.exists(file_path):
            file_path = self.storage.save(
                file_path,
                ContentFile(value),
            )
        return super(StorageTextField, self).get_prep_value(file_path)

    def from_db_value(self, value, expression, connection, context):
        content = self.storage.open(value).read()
        content = self.from_db_hook(content)
        return content.decode('utf-8')
