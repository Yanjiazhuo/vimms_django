from django.test import TestCase

# Create your tests here.

from .models import Document

class DocumentModelTestCase(TestCase):
    def setUp(self):
        Document.objects.create(description="test0")
        Document.objects.create(description="test1")

    def test_model_use(self):
        """Document upload/download are correctly identified"""
        test0 = Document.objects.get(description="test0")
        test1 = Document.objects.get(description="test1")
        self.assertEqual(test0.description, 'test0')
        self.assertEqual(test1.description, 'test1')