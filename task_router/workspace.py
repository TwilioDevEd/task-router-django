from twilio.rest import Client
from django.conf import settings
import json

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


CLIENT = build_client()
CACHE = {}


def activities_dict(workspace_sid):
    activities = build_client().taskrouter.workspaces(workspace_sid)\
                               .activities.list()

    return dict((activity.friendly_name, activity) for activity in activities)


class WorkspaceInfo:

    def __init__(self, workspace, workflow, activities, workers):
        self.workflow_sid = workflow.sid
        self.workspace_sid = workspace.sid
        self.activities = activities
        self.post_work_activity_sid = activities['Idle'].sid
        self.workers = workers


def setup():
    if 'WORKSPACE_INFO' not in CACHE:
        workspace = create_workspace()
        activities = activities_dict(workspace.sid)
        workers = create_workers(workspace, activities)
        queues = create_task_queues(workspace, activities)
        workflow = create_workflow(workspace, queues)
        CACHE['WORKSPACE_INFO'] = WorkspaceInfo(workspace, workflow, activities, workers)
    return CACHE['WORKSPACE_INFO']


def create_workspace():
    try:
        workspace = first(CLIENT.taskrouter.workspaces.list(friendly_name=WORKSPACE_NAME))
        CLIENT.taskrouter.workspaces(workspace.sid).delete()
    except:
        pass

    events_callback = HOST+'/events'

    return CLIENT.taskrouter.workspaces.create(
            friendly_name=WORKSPACE_NAME,
            event_callback_url=events_callback,
            template=None)


def create_workers(workspace, activities):
    alice_attributes = {
        "products": ["ProgrammableVoice"],
        "contact_uri": ALICE_NUMBER
    }

    alice = CLIENT.taskrouter.workspaces(workspace.sid)\
                  .workers.create(activity_sid=activities['Idle'].sid,
                                  friendly_name='Alice',
                                  attributes=json.dumps(alice_attributes))

    bob_attributes = {
        "products": ["ProgrammableSMS"],
        "contact_uri": BOB_NUMBER
    }

    bob = CLIENT.taskrouter.workspaces(workspace.sid)\
                .workers.create(activity_sid=activities['Idle'].sid,
                                friendly_name='Bob',
                                attributes=json.dumps(bob_attributes))

    return {BOB_NUMBER: bob.sid, ALICE_NUMBER: alice.sid}


def create_task_queues(workspace, activities):
    default_queue = CLIENT.taskrouter.workspaces(workspace.sid).task_queues\
                    .create(friendly_name='Default',
                            reservation_activity_sid=activities['Reserved'].sid,
                            assignment_activity_sid=activities['Busy'].sid,
                            target_workers='1==1')

    sms_queue = CLIENT.taskrouter.workspaces(workspace.sid).task_queues\
                      .create(friendly_name='SMS',
                              reservation_activity_sid=activities['Reserved'].sid,
                              assignment_activity_sid=activities['Busy'].sid,
                              target_workers='"ProgrammableSMS" in products')

    voice_queue = CLIENT.taskrouter.workspaces(workspace.sid).task_queues\
                        .create(friendly_name='Voice',
                                reservation_activity_sid=activities['Reserved'].sid,
                                assignment_activity_sid=activities['Busy'].sid,
                                target_workers='"ProgrammableVoice" in products')

    return {'sms': sms_queue, 'voice': voice_queue, 'default': default_queue}


def create_workflow(workspace, queues):
    defaultTarget = {
        'queue': queues['sms'].sid,
        'Priority': 5,
        'Timeout': 30
    }

    smsTarget = {
        'queue': queues['sms'].sid,
        'Priority': 5,
        'Timeout': 30
    }

    voiceTarget = {
        'queue': queues['voice'].sid,
        'Priority': 5,
        'Timeout': 30
    }

    default_filter = {
        'queue': queues['default'].sid,
        'Expression': '1==1',
        'Priority': 1,
        'Timeout': 30
    }

    voiceFilter = {
        'expression': 'selected_product=="ProgrammableVoice"',
        'targets': [voiceTarget, defaultTarget]
    }

    smsFilter = {
        'expression': 'selected_product=="ProgrammableSMS"',
        'targets': [smsTarget, defaultTarget]
    }

    config = {
        'task_routing': {
            'filters': [voiceFilter, smsFilter],
            'default_filter': default_filter
        }
    }

    callback_url = HOST + '/assignment'

    return CLIENT.taskrouter.workspaces(workspace.sid)\
                 .workflows.create(friendly_name='Sales',
                                   assignment_callback_url=callback_url,
                                   fallback_assignment_callback_url=callback_url,
                                   task_reservation_timeout=15,
                                   configuration=json.dumps(config))
