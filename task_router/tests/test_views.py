from xmlunittest import XmlTestCase
from django.test import TestCase, Client
from mock import patch
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

        expected_text = 'For Programmable SMS, press one. For Voice, press any other key.'
        self.assertXpathValues(root, './Gather/Say/text()', (expected_text))

    def test_enqueue_digit_1(self):
        # Act
        response = self.client.post('/call/enqueue/', {'Digits': '1'})
        content = response.content
        root = self.assertXmlDocument(content)

        self.assertXpathValues(root, './Enqueue/Task/text()',
                               ('{"selected_product": "Programmable SMS"}'))

    def test_enqueue_digit_2(self):
        # Act
        response = self.client.post('/call/enqueue/', {'Digits': '2'})
        content = response.content
        root = self.assertXmlDocument(content)

        self.assertXpathValues(root, './Enqueue/Task/text()',
                               ('{"selected_product": "ProgrammableVoice"}'))

    def test_enqueue_digit_3(self):
        # Act
        response = self.client.post('/call/enqueue/', {'Digits': '3'})
        content = response.content
        root = self.assertXmlDocument(content)

        self.assertXpathValues(root, './Enqueue/Task/text()',
                               ('{"selected_product": "ProgrammableVoice"}'))

    def test_assignment(self):
        # Act
        response = self.client.post('/assignment')
        content = response.content.decode('utf8')

        expected = {"instruction": "dequeue",
                    "post_work_activity_sid": POST_WORK_ACTIVITY_SID}
        self.assertEqual(json.loads(content), expected)

    @patch('task_router.views._hangup_call')
    def test_event_persist_missed_call(self, _):
        # Act
        response = self.client.post('/events', {
            'EventType': 'workflow.timeout',
            'TaskAttributes': '''
            {"from": "+266696687",
            "call_sid": "123",
            "selected_product": "ACMERockets"}
            '''
        })

        status_code = response.status_code

        self.assertEqual(200, status_code)
        missedCalls = MissedCall.objects.filter(phone_number='+266696687')

        self.assertEqual(1, len(missedCalls))
        self.assertEqual('ACMERockets', missedCalls[0].selected_product)

    @patch('task_router.views._hangup_call')
    def test_hangups_on_missed_call(self, mocked_hangup_call):
        # Act
        self.client.post('/events', {
            'EventType': 'workflow.timeout',
            'TaskAttributes': '''
            {"from": "+266696687",
            "call_sid": "123",
            "selected_product": "ACMERockets"}
            '''
        })
        mocked_hangup_call.assert_called_with('123')

    def test_event_ignore_others(self):
        # Act
        response = self.client.post('/events', {
            'EventType': 'other',
            'TaskAttributes': '''
            {"from": "+266696687",
            "selected_product": "ACMERockets"}
            '''
        })

        status_code = response.status_code

        self.assertEqual(200, status_code)
        missedCalls = MissedCall.objects.filter(phone_number='+111111111')

        self.assertEqual(0, len(missedCalls))
