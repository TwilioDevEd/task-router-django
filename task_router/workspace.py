import json

from django.conf import settings
from twilio.rest import Client

HOST = settings.HOST
ALICE_NUMBER = settings.ALICE_NUMBER
BOB_NUMBER = settings.BOB_NUMBER
WORKSPACE_NAME = 'Twilio Workspace'


def first(items):
    return items[0] if items else None


def build_client():
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    return Client(account_sid, auth_token)


CACHE = {}


def activities_dict(client, workspace_sid):
    activities = client.taskrouter.workspaces(workspace_sid)\
                                  .activities.list()

    return {activity.friendly_name: activity for activity in activities}


class WorkspaceInfo:

    def __init__(self, workspace, workflow, activities, workers):
        self.workflow_sid = workflow.sid
        self.workspace_sid = workspace.sid
        self.activities = activities
        self.post_work_activity_sid = activities['Available'].sid
        self.workers = workers


def setup():
    client = build_client()
    if 'WORKSPACE_INFO' not in CACHE:
        workspace = create_workspace(client)
        activities = activities_dict(client, workspace.sid)
        workers = create_workers(client, workspace, activities)
        queues = create_task_queues(client, workspace, activities)
        workflow = create_workflow(client, workspace, queues)
        CACHE['WORKSPACE_INFO'] = WorkspaceInfo(workspace, workflow, activities, workers)
    return CACHE['WORKSPACE_INFO']


def create_workspace(client):
    try:
        workspace = first(client.taskrouter.workspaces.list(friendly_name=WORKSPACE_NAME))
        client.taskrouter.workspaces(workspace.sid).delete()
    except Exception:
        pass

    events_callback = HOST + '/events/'

    return client.taskrouter.workspaces.create(
            friendly_name=WORKSPACE_NAME,
            event_callback_url=events_callback,
            template=None)


def create_workers(client, workspace, activities):
    alice_attributes = {
        "products": ["ProgrammableVoice"],
        "contact_uri": ALICE_NUMBER
    }

    alice = client.taskrouter.workspaces(workspace.sid)\
                  .workers.create(friendly_name='Alice',
                                  attributes=json.dumps(alice_attributes))

    bob_attributes = {
        "products": ["ProgrammableSMS"],
        "contact_uri": BOB_NUMBER
    }

    bob = client.taskrouter.workspaces(workspace.sid)\
                .workers.create(friendly_name='Bob',
                                attributes=json.dumps(bob_attributes))

    return {BOB_NUMBER: bob.sid, ALICE_NUMBER: alice.sid}


def create_task_queues(client, workspace, activities):
    default_queue = client.taskrouter.workspaces(workspace.sid).task_queues\
                    .create(friendly_name='Default',
                            assignment_activity_sid=activities['Unavailable'].sid,
                            target_workers='1==1')

    sms_queue = client.taskrouter.workspaces(workspace.sid).task_queues\
                      .create(friendly_name='SMS',
                              assignment_activity_sid=activities['Unavailable'].sid,
                              target_workers='"ProgrammableSMS" in products')

    voice_queue = client.taskrouter.workspaces(workspace.sid).task_queues\
                        .create(friendly_name='Voice',
                                assignment_activity_sid=activities['Unavailable'].sid,
                                target_workers='"ProgrammableVoice" in products')

    return {'sms': sms_queue, 'voice': voice_queue, 'default': default_queue}


def create_workflow(client, workspace, queues):
    defaultTarget = {
        'queue': queues['sms'].sid,
        'priority': 5,
        'timeout': 30
    }

    smsTarget = {
        'queue': queues['sms'].sid,
        'priority': 5,
        'timeout': 30
    }

    voiceTarget = {
        'queue': queues['voice'].sid,
        'priority': 5,
        'timeout': 30
    }

    default_filter = {
        'filter_friendly_name': 'Default Filter',
        'queue': queues['default'].sid,
        'Expression': '1==1',
        'priority': 1,
        'timeout': 30
    }

    voiceFilter = {
        'filter_friendly_name': 'Voice Filter',
        'expression': 'selected_product=="ProgrammableVoice"',
        'targets': [voiceTarget, defaultTarget]
    }

    smsFilter = {
        'filter_friendly_name': 'SMS Filter',
        'expression': 'selected_product=="ProgrammableSMS"',
        'targets': [smsTarget, defaultTarget]
    }

    config = {
        'task_routing': {
            'filters': [voiceFilter, smsFilter],
            'default_filter': default_filter
        }
    }

    callback_url = HOST + '/assignment/'

    return client.taskrouter.workspaces(workspace.sid)\
                 .workflows.create(friendly_name='Sales',
                                   assignment_callback_url=callback_url,
                                   fallback_assignment_callback_url=callback_url,
                                   task_reservation_timeout=15,
                                   configuration=json.dumps(config))
