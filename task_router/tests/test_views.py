import json

from django.conf import settings
from django.test import Client, TestCase
from mock import Mock, patch
from task_router import workspace
from task_router.models import MissedCall
from xmlunittest import XmlTestCase
from task_router import views


class HomePageTest(TestCase, XmlTestCase):

    def setUp(self):
        self.client = Client()
        self.original = workspace.setup
        setup_mock = Mock(
            return_value=workspace.WorkspaceInfo(
                Mock(sid='workspace_sid'),
                Mock(sid='workflow_sid'),
                {
                    'Offline': Mock(sid='offline_sid'),
                    'Unavailable': Mock(sid='unavailable_sid'),
                    'Available': Mock(sid='available_sid'),
                },
                {'+123': 'worker_sid'}
            )
        )
        workspace.setup = setup_mock
        views.setup_workspace()

    def tearDown(self):
        workspace.setup = self.original

    def test_home_page(self):
        # Act
        response = self.client.get('/')

        # Assert
        # This is a class-based view, so we can mostly rely on Django's own
        # tests to make sure it works. We'll check for a bit of copy, though
        self.assertIn('Task Router', str(response.content))

    def test_incoming_sms_changes_worker_activity_to_offline(self):
        client_mock = Mock()
        views.Client = Mock(return_value=client_mock)

        # Act
        response = self.client.post('/sms/incoming/', data={'Body': 'off', 'From': '+123'})

        expected_text = 'Your status has changed to Offline'
        self.assertIn(expected_text, response.content.decode('utf8'))

    def test_incoming_sms_changes_worker_activity_to_idle(self):
        client_mock = Mock()
        views.Client = Mock(return_value=client_mock)

        # Act
        response = self.client.post('/sms/incoming/', data={'Body': 'on', 'From': '+123'})

        expected_text = 'Your status has changed to Available'
        self.assertIn(expected_text, response.content.decode('utf8'))

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
                               ('{"selected_product": "ProgrammableSMS"}'))

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
                    "post_work_activity_sid": 'available_sid'}
        self.assertEqual(json.loads(content), expected)

    @patch('task_router.views._voicemail')
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

    @patch('task_router.views._voicemail')
    def test_event_persist_canceled_call(self, _):
        # Act
        response = self.client.post('/events', {
            'EventType': 'task.canceled',
            'TaskAttributes': '''
            {"from": "+266696687",
            "call_sid": "123",
            "selected_product": "ACMETNT"}
            '''
        })

        status_code = response.status_code

        self.assertEqual(200, status_code)
        missedCalls = MissedCall.objects.filter(phone_number='+266696687')

        self.assertEqual(1, len(missedCalls))
        self.assertEqual('ACMETNT', missedCalls[0].selected_product)

    def test_voicemail_on_missed_call(self):
        route_call_mock = Mock()
        from task_router import views
        views.route_call = route_call_mock
        # Act
        self.client.post('/events', {
            'EventType': 'workflow.timeout',
            'TaskAttributes': '''
            {"from": "+266696687",
            "call_sid": "123",
            "selected_product": "ACMERockets"}
            '''
        })
        expected_url = "http://twimlets.com/voicemail?Email=%s&Message=" % \
            settings.MISSED_CALLS_EMAIL_ADDRESS
        expected_url += 'Sorry%2C+All+agents+are+busy.+Please+leave+a+message.+'
        expected_url += 'We+will+call+you+as+soon+as+possible'
        route_call_mock.assert_called_with('123', expected_url)

    def test_sms_for_worker_going_offline(self):
        sender_mock = Mock()
        from task_router import views
        views.sms_sender = sender_mock
        views.TWILIO_NUMBER = '+54321'

        # Act
        self.client.post('/events', {
            'EventType': 'worker.activity.update',
            'WorkerActivityName': 'Offline',
            'WorkerAttributes': '{"contact_uri": "+1234"}'
        })

        expectedMessage = 'Your status has changed to Offline. Reply with '\
            '"On" to get back Online'
        sender_mock.send.assert_called_with(
                to='+1234', from_='+54321', body=expectedMessage)

    def test_event_ignore_others(self):
        # Act
        response = self.client.post('/events', {
            'EventType': 'other'
        })

        status_code = response.status_code

        self.assertEqual(200, status_code)
        missedCalls = MissedCall.objects.filter(phone_number='+111111111')

        self.assertEqual(0, len(missedCalls))
