from django.db import models

from storage_text_field.fields import StorageTextField


class Document(models.Model):
    html = StorageTextField()
