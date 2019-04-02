import hashlib
import os
import six

from django.conf import settings
from django.core.cache import caches
from django.core.files.base import ContentFile
from django.core.files.storage import (
    Storage,
    default_storage,
    get_storage_class,
)
from django.db import models
from django.utils.functional import lazy


def default_pre_save_hook(value):
    return value


def default_from_db_hook(value):
    return value


def default_file_path_hook(value):
    return value


class StorageTextField(models.CharField):
    def __init__(
            self,
            storage=None,
            pre_save_hook=None,
            from_db_hook=None,
            file_path_hook=None,
            use_cache=False,
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
        if not file_path_hook:
            file_path_hook = default_file_path_hook
        self.storage = storage
        self.pre_save_hook = pre_save_hook
        self.from_db_hook = from_db_hook
        self.file_path_hook = file_path_hook
        self.use_cache = use_cache
        if self.use_cache:
            self.cache_config = getattr(
                settings,
                'STORAGE_TEXT_FIELD_CACHE_CONFIG',
                'default',
            )
            self.cache_duration = getattr(
                settings,
                'STORAGE_TEXT_FIELD_CACHE_DURATION',
                60 * 60 * 24,  # One Day
            )
            self.cache = caches[self.cache_config]
        kwargs['max_length'] = 200
        super(StorageTextField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(StorageTextField, self).deconstruct()
        del kwargs['max_length']
        kwargs['pre_save_hook'] = self.pre_save_hook
        kwargs['from_db_hook'] = self.from_db_hook
        kwargs['file_path_hook'] = self.file_path_hook
        kwargs['storage'] = self.storage
        kwargs['use_cache'] = self.use_cache
        return name, path, args, kwargs

    def get_file_path(self, value):
        str_self = str(self).encode('utf-8')
        digest = hashlib.sha224(
            str_self + six.text_type(value).encode('utf-8')
        ).hexdigest()
        return self.file_path_hook(os.path.join(
            digest.encode('utf-8'),
            str_self,
        ))

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
        def get_from_storage():
            return self.storage.open(value).read()

        def result():
            if self.use_cache:
                content = self.cache.get(value)
                if content is None:
                    content = get_from_storage()
            else:
                content = get_from_storage()
            content = self.from_db_hook(content)
            try:
                return_value = six.text_type(content.decode('utf-8'))
            except (UnicodeEncodeError, AttributeError):
                return_value = six.text_type(content)
            if self.use_cache:
                self.cache.set(value, return_value, self.cache_duration)
            return return_value

        return lazy(result, six.text_type)()
