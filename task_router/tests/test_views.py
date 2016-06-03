from xmlunittest import XmlTestCase
from django.test import TestCase, Client
from task_router.views import POST_WORK_ACTIVITY_SID
from task_router.models import MissedCall

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

    def test_incoming_call(self):
        # Act
        response = self.client.post('/call/incoming/')
        content = response.content
        root = self.assertXmlDocument(content)

        expected_text = 'For ACME Rockets, press one. For ACME TNT, press any other key.'
        self.assertXpathValues(root, './Gather/Say/text()', (expected_text))

    def test_enqueue_digit_1(self):
        # Act
        response = self.client.post('/call/enqueue/', {'Digits': '1'})
        content = response.content
        root = self.assertXmlDocument(content)

        self.assertXpathValues(root, './Enqueue/Task/text()',
                               ('{"selected_product": "ACMERockets"}'))

    def test_enqueue_digit_2(self):
        # Act
        response = self.client.post('/call/enqueue/', {'Digits': '2'})
        content = response.content
        root = self.assertXmlDocument(content)

        self.assertXpathValues(root, './Enqueue/Task/text()',
                               ('{"selected_product": "ACMETNT"}'))

    def test_enqueue_digit_3(self):
        # Act
        response = self.client.post('/call/enqueue/', {'Digits': '3'})
        content = response.content
        root = self.assertXmlDocument(content)

        self.assertXpathValues(root, './Enqueue/Task/text()',
                               ('{"selected_product": "ACMETNT"}'))

    def test_assignment(self):
        # Act
        response = self.client.post('/assignment')
        content = response.content

        expected = {"instruction": "dequeue",
                    "post_work_activity_sid": POST_WORK_ACTIVITY_SID}
        self.assertEquals(json.loads(content), expected)

    def test_event_persist_missed_call(self):
        # Act
        response = self.client.post('/events', {
            'EventType': 'workflow.timeout',
            'from': '+266696687',
            'selected_product': 'ACMERockets'
        })

        status_code = response.status_code

        self.assertEquals(200, status_code)
        missedCalls = MissedCall.objects.filter(phone_number='+266696687')

        self.assertEquals(1, len(missedCalls))
        self.assertEquals('ACMERockets', missedCalls[0].selected_product)

    def test_event_ignore_others(self):
        # Act
        response = self.client.post('/events', {
            'EventType': 'other',
            'from': '+111111111',
            'selected_product': 'ACMERockets'
        })

        status_code = response.status_code

        self.assertEquals(200, status_code)
        missedCalls = MissedCall.objects.filter(phone_number='+111111111')

        self.assertEquals(0, len(missedCalls))