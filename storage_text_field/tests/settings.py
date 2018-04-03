import os
import uuid


SECRET_KEY = str(uuid.uuid4())

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


INSTALLED_APPS = [
    'storage_text_field.tests',
]

MEDIA_ROOT = os.path.join(
    os.path.dirname(__file__),
    'media_root',
)
