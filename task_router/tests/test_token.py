from django.test import TestCase
from mock import Mock
from task_router import token


class TokenTest(TestCase):

    def test_get_token(self):
        # given
        capability_mock = Mock()
        token.TwilioCapability = Mock(return_value=capability_mock)
        capability_mock.generate.return_value = 'token123'

        # when
        generated_token = token.generate('agent10')
        self.assertEquals('token123', generated_token)

        # then
        token.TwilioCapability.assert_called_with('sid321', 'auth123')
        capability_mock.allow_client_incoming.assert_called_with('agent10')
