import uuid

from django.test import TestCase

from storage_text_field.tests.models import Document


class Foo(TestCase):
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
