import uuid

from django.core.files.storage import default_storage
from django.db import connection
from django.test import TestCase

from storage_text_field.tests.models import Document


class SmokeTestCase(TestCase):
    @property
    def html(self):
        return '<p>{}</p>'.format(uuid.uuid4())

    def test_smoke_test(self):
        html = self.html
        document = Document.objects.create(
            html=html,
        )
        document.refresh_from_db()
        self.assertEqual(document.html, html)

    def test_db_is_saving_file_path_to_content(self):
        html = self.html
        document = Document.objects.create(
            html=html,
        )

        cursor = connection.cursor()

        query = 'SELECT html from tests_document WHERE id = %d'
        cursor.execute(query % document.pk)
        html_value = cursor.fetchone()[0]
        self.assertEqual(
            default_storage.open(html_value).read().decode('utf-8'),
            html,
        )
