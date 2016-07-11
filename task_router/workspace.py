from twilio.rest import TwilioTaskRouterClient
from twilio.task_router.workflow_ruletarget import WorkflowRuleTarget
from twilio.task_router.workflow_rule import WorkflowRule
from twilio.task_router.workflow_config import WorkflowConfig
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
    return TwilioTaskRouterClient(account_sid, auth_token)


CLIENT = build_client()
CACHE = {}


def activities_dict(workspace_sid):
    activities = build_client().activities(workspace_sid).list()
    return dict((activity.friendly_name, activity) for activity in activities)


class WorkspaceInfo:

    def __init__(self, workflow, activities):
        self.workflow_sid = workflow.sid
        self.activities = activities
        self.post_work_activity_sid = activities['Idle'].sid


def setup():
    if 'WORKSPACE_INFO' not in CACHE:
        workspace = create_workspace()
        activities = activities_dict(workspace.sid)
        create_workers(workspace, activities)
        queues = create_task_queues(workspace, activities)
        workflow = create_workflow(workspace, queues)
        CACHE['WORKSPACE_INFO'] = WorkspaceInfo(workflow, activities)
    return CACHE['WORKSPACE_INFO']


def create_workspace():
    try:
        workspace = first(CLIENT.workspaces.list(friendly_name=WORKSPACE_NAME))
        CLIENT.workspaces.delete(workspace.sid)
    except:
        pass

    events_callback = HOST+'/events'
    return CLIENT.workspaces.create(
            friendly_name=WORKSPACE_NAME,
            event_callback_url=events_callback,
            template=None)


def create_workers(workspace, activities):
    alice_attributes = {
        "products": ["ProgrammableVoice"],
        "contact_uri": ALICE_NUMBER
    }
    CLIENT.workers(workspace.sid).create(
        activity_sid=activities['Idle'].sid,
        friendly_name='Alice',
        attributes=json.dumps(alice_attributes))
    bob_attributes = {
        "products": ["ProgrammableSMS"],
        "contact_uri": BOB_NUMBER
    }
    CLIENT.workers(workspace.sid).create(
        activity_sid=activities['Idle'].sid,
        friendly_name='Bob',
        attributes=json.dumps(bob_attributes))


def create_task_queues(workspace, activities):
    default_queue = CLIENT.task_queues(workspace.sid).create(
            friendly_name='Default',
            reservation_activity_sid=activities['Reserved'].sid,
            assignment_activity_sid=activities['Busy'].sid,
            target_workers='1==1'
            )
    sms_queue = CLIENT.task_queues(workspace.sid).create(
            friendly_name='SMS',
            reservation_activity_sid=activities['Reserved'].sid,
            assignment_activity_sid=activities['Busy'].sid,
            target_workers='selected_product=="ProgrammableSMS"')
    voice_queue = CLIENT.task_queues(workspace.sid).create(
            friendly_name='Voice',
            reservation_activity_sid=activities['Reserved'].sid,
            assignment_activity_sid=activities['Busy'].sid,
            target_workers='selected_product=="ProgrammableVoice"'
            )

    return {'sms': sms_queue, 'voice': voice_queue, 'default': default_queue}


def create_workflow(workspace, queues):
    defaultRuleTarget = WorkflowRuleTarget(queues['default'].sid, '1==1', 1, 30)

    rules = []
    queueRuleTargets = []
    queueRuleTarget = WorkflowRuleTarget(queues['sms'].sid, None, 5, 30)
    queueRuleTargets.append(queueRuleTarget)
    queueRuleTargets.append(defaultRuleTarget)
    rules.append(
            WorkflowRule("selected_product==\"ProgrammableSMS\"",
                         [queueRuleTarget, defaultRuleTarget], None))
    queueRuleTargets = []
    queueRuleTarget = WorkflowRuleTarget(queues['voice'].sid, None, 5, 30)
    queueRuleTargets.append(queueRuleTarget)
    queueRuleTargets.append(defaultRuleTarget)
    rules.append(
            WorkflowRule("selected_product==\"ProgrammableVoice\"",
                         [queueRuleTarget, defaultRuleTarget], None))

    config = WorkflowConfig(rules, defaultRuleTarget)
    return CLIENT.workflows(workspace.sid).create(
        friendly_name='Sales',
        assignment_callback_url=HOST + '/assignment',
        fallback_assignment_callback_url=HOST + '/assignment',
        task_reservation_timeout=15,
        configuration=config.to_json())
