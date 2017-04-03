from django.test import TestCase
from mock import Mock
from task_router import sms_sender


class SMSSenderTests(TestCase):

    def test_send_sms(self):
        client_mock = Mock()
        sms_sender.Client = Mock(return_value=client_mock)
        client_mock.messages = Mock()

        sms_sender.send(to='+123', from_='+321', body='hi')
        client_mock.api.messages.create.assert_called_with(
                to='+123', from_='+321', body='hi')
