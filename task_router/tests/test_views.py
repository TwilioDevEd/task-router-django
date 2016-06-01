from xmlunittest import XmlTestCase
from django.test import TestCase, Client
from unittest import skip

class HomePageTest(TestCase, XmlTestCase):

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        # Act
        response = self.client.get('/')

        # Assert
        # This is a class-based view, so we can mostly rely on Django's own
        # tests to make sure it works. We'll check for a bit of copy, though
        self.assertIn('Task Router', str(response.content))

    # @skip("WIP")
    def test_incoming_call(self):
        # Act
        response = self.client.get('/call/incoming/')
        content = response.content
        root = self.assertXmlDocument(content)

        say = root.xpath('./Gather/Say/text()')

        self.assertEquals(1, len(say), content)
        self.assertEquals('For ACME Rockets, press one. For ACME TNT, press two.', say[0])
