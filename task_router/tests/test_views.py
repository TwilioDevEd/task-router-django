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

    @skip("WIP")
    def test_incoming_call(self):
        # Act
        response = self.client.get('/call/incoming/')

        root = self.assertXmlDocument(response.data)
        say = root.xpath('./Gather/say()')
# <Response>
#   <Gather action="/call/enqueue" numDigits="1" timeout="5">
#     <Say>For ACME Rockets, press one.&</Say>
#     <Say>For ACME TNT, press two.</Say>
#   </Gather>
# </Response>
        self.assertEquals(2, len(sat), response.data)
        self.assertEquals('For ACME Rockets, press one.', say[0])
        self.assertEquals('For ACME TNT, press two.', say[1])
