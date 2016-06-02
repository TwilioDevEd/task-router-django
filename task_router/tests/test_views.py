from xmlunittest import XmlTestCase
from django.test import TestCase, Client
from task_router.views import POST_WORK_ACTIVITY_SID
import json


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

        expected_text = 'For ACME Rockets, press one. For ACME TNT, press two.'
        self.assertXpathValues(root, './Gather/Say/text()',
                               (expected_text))

    def test_enqueue(self):
        # Act
        response = self.client.get('/call/enqueue/')
        content = response.content
        root = self.assertXmlDocument(content)

        self.assertXpathValues(root, './Enqueue/Task/text()',
                               ('{"selected_product": "ACMERockets"}'))

    def test_assignment(self):
        # Act
        response = self.client.get('/assignment')
        content = response.content

        expected = {"instruction": "dequeue",
                    "post_work_activity_sid": POST_WORK_ACTIVITY_SID}
        self.assertEquals(json.loads(content), expected)
