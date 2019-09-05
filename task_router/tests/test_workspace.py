import vcr
from django.conf import settings
from django.test import TestCase
from task_router import workspace


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
    filter_headers=['authorization'],
    cassette_library_dir='fixtures',
    before_record_response=scrub_string(settings.TWILIO_ACCOUNT_SID, '<account_sid>'),
)


class WorkspaceTests(TestCase):
    @filtered_vcr.use_cassette()
    def test_setup_creates_a_workspace(self):
        workspace.HOST = 'http://example.com'
        workspace.BOB_NUMBER = '+15005550006'
        workspace.ALICE_NUMBER = '+15005550008'
        workspace_info = workspace.setup()
        self.assertEqual('WW580b329219b59fe3fcb39a5f0ca8de69',
                         workspace_info.workflow_sid)
        self.assertEqual('WAaa135269109e84059e8ae7c49105a4d2',
                         workspace_info.activities['Available'].sid)
        self.assertEqual(workspace_info.activities['Available'].sid,
                         workspace_info.post_work_activity_sid)
