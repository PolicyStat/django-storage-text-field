import uuid

from django.core.files.storage import default_storage
from django.db import connection
from django.test import TestCase

from storage_text_field.tests.models import (
    CustomerStorageDocument,
    CustomerStorageObjectDocument,
    Document,
)
from storage_text_field.tests import storages


class BaseTestCase(object):
    @property
    def html(self):
        return '<p>{}</p>'.format(uuid.uuid4())

    def get_filepath_from_db(self, obj):
        cursor = connection.cursor()

        query = 'SELECT html from %s WHERE id = %d'
        cursor.execute(query % (obj._meta.db_table, obj.pk))
        file_path = cursor.fetchone()[0]
        return file_path

    def test_smoke_test(self):
        html = self.html
        document = self.Model.objects.create(
            html=html,
        )
        document.refresh_from_db()
        self.assertEqual(document.html, html)

    def test_only_save_on_storage_once(self):
        html = self.html
        document = self.Model.objects.create(
            html=html,
        )
        document.refresh_from_db()
        original_file_path = self.get_filepath_from_db(document)
        document.save()
        self.assertEqual(
            original_file_path,
            self.get_filepath_from_db(document),
        )


class SmokeTestCase(BaseTestCase, TestCase):
    Model = Document

    def test_db_is_saving_file_path_to_content(self):
        html = self.html
        document = self.Model.objects.create(
            html=html,
        )

        html_file_path = self.get_filepath_from_db(document)
        self.assertEqual(
            default_storage.open(html_file_path).read().decode('utf-8'),
            html,
        )


class CustomerStorageTestCase(BaseTestCase, TestCase):
    Model = CustomerStorageDocument

    def setUp(self):
        super(CustomerStorageTestCase, self).setUp()
        # Clear the custom storage.
        storages.storage = dict()

    def test_custom_storage_is_used(self):
        html = self.html
        self.Model.objects.create(
            html=html,
        )
        self.assertEqual(len(storages.storage), 1)
        self.assertEqual(
            list(storages.storage.values())[0],
            html,
        )


class CustomerStorageObjectTestCase(CustomerStorageTestCase):
    Model = CustomerStorageObjectDocument
