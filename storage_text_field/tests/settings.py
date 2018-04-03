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
