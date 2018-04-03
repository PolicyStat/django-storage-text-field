from django.test import TestCase

from storage_text_field.tests.models import Document


class Foo(TestCase):
    def test_smoke_test(self):
        document = Document.objects.create(
            html='<p>foo</p>',
        )
        self.assertEqual(document.html, '<p>foo</p>')
