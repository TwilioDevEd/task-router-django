from django.test import TestCase
from task_router import workspace
from django.conf import settings
import vcr


def scrub_string(string, replacement=''):
    def before_record_response(response):
        current_body = response['body']['string'].decode('utf8')
        fixed_body = current_body.replace(string, replacement)
        response['body']['string'] = fixed_body.encode('utf8')
        return response
    return before_record_response

filtered_vcr = vcr.VCR(
    # Uncomment the line below to re-record the cassette
    # record_mode='all',
    cassette_library_dir='fixtures',
    before_record_response=scrub_string(settings.TWILIO_ACCOUNT_SID, '<account_sid>'),
)


class WorkspaceTests(TestCase):

    @filtered_vcr.use_cassette(filter_headers=['authorization'])
    def test_setup_creates_a_workspace(self):
        workspace.HOST = 'http://example.com'
        workspace.BOB_NUMBER = '+15005550006'
        workspace.ALICE_NUMBER = '+15005550008'
        workspace_info = workspace.setup()
        self.assertEqual('WW4446abc28a7664d738a283da8c857f5d',
                         workspace_info.workflow_sid)
        self.assertEqual('WAe08a8fa2540d404062b965b237cafd17',
                         workspace_info.activities['Offline'].sid)
        self.assertEqual(workspace_info.activities['Idle'].sid,
                         workspace_info.post_work_activity_sid)
