import uuid

from django.core.files.storage import default_storage
from django.db import connection
from django.test import TestCase

from unittest import skip

from storage_text_field.tests.models import (
    CustomStorageDocument,
    CustomStorageObjectDocument,
    Document,
    FromDBHookDocument,
    PreSaveHookDocument,
    from_db_hook,
    pre_save_hook,
)
from storage_text_field.tests import storages


class BaseTestCase(object):
    @property
    def html(self):
        return '<p>{}</p>'.format(uuid.uuid4())

    def pre_save_hook(self, value):
        return value

    def from_db_hook(self, value):
        return value

    def get_filepath_from_db(self, obj):
        cursor = connection.cursor()

        # You are not supposed to use string formatting when doing SQL queries,
        # but I hate the way we are supposed to do this. Since this is a test,
        # there is no chance of a SQL injection.
        query = 'SELECT html from {db_table} WHERE id = {pk}'
        cursor.execute(query.format(
            db_table=obj._meta.db_table,
            pk=obj.pk,
        ))
        file_path = cursor.fetchone()[0]
        return file_path

    def format_expected_value(self, value):
        return self.from_db_hook(self.pre_save_hook(value))

    def test_smoke_test(self):
        html = self.html
        document = self.Model.objects.create(
            html=html,
        )
        document.refresh_from_db()
        self.assertEqual(document.html, self.format_expected_value(html))

    def test_field_can_be_blank(self):
        document = self.Model.objects.create()
        document.refresh_from_db()
        self.assertEqual(document.html, self.format_expected_value(''))

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

    def test_changing_the_content_changes_the_filepath(self):
        html = self.html
        document = self.Model.objects.create(
            html=html,
        )
        document.refresh_from_db()
        original_file_path = self.get_filepath_from_db(document)

        # self.html creates new custom HTML.
        document.html = self.html
        document.save()
        self.assertNotEqual(
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
        with default_storage.open(html_file_path) as f:
            file_contents = f.read().decode('utf-8')
        self.assertEqual(file_contents, html)


class CustomStorageTestCase(BaseTestCase, TestCase):
    Model = CustomStorageDocument

    def setUp(self):
        super(CustomStorageTestCase, self).setUp()
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


class CustomStorageObjectTestCase(CustomStorageTestCase):
    Model = CustomStorageObjectDocument


class PreSaveHookTestCase(BaseTestCase, TestCase):
    Model = PreSaveHookDocument

    def pre_save_hook(self, value):
        return pre_save_hook(value)

    @skip('This test does not work with only the pre save hook')
    def test_only_save_on_storage_once(self):
        pass

    def test_html_is_updated_because_of_pre_save_hook(self):
        html = self.html
        document = self.Model.objects.create(
            html=html,
        )
        document.refresh_from_db()
        self.assertEqual(document.html, self.pre_save_hook(html))


class FromDBHookTestCase(BaseTestCase, TestCase):
    Model = FromDBHookDocument

    def from_db_hook(self, value):
        return from_db_hook(value)

    @skip('This test does not work with only the pre save hook')
    def test_only_save_on_storage_once(self):
        pass

    def test_html_is_updated_because_of_from_db_hook(self):
        html = self.html
        document = self.Model.objects.create(
            html=html,
        )
        document.refresh_from_db()
        self.assertEqual(document.html, self.from_db_hook(html))
