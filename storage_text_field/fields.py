from django.db import models


class StorageTextField(models.CharField):
    def __init__(self, *args, **kwargs):
        if 'max_length' not in kwargs:
            kwargs['max_length'] = 200
        super(StorageTextField, self).__init__(*args, **kwargs)
