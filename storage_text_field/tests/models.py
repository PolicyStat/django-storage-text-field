from django.db import models

from storage_text_field.fields import StorageTextField
from storage_text_field.tests.storages import CustomerStorage


class Document(models.Model):
    html = StorageTextField()


class CustomerStorageDocument(models.Model):
    html = StorageTextField(
        storage='storage_text_field.tests.storages.CustomerStorage',
    )


class CustomerStorageObjectDocument(models.Model):
    html = StorageTextField(
        storage=CustomerStorage(),
    )


def pre_save_hook(value):
    return value + '<strong>FOOBAR</strong>'


class PreSaveHookDocument(models.Model):
    html = StorageTextField(
        pre_save_hook=pre_save_hook,
    )
