from twilio.rest import TwilioTaskRouterClient
from twilio.task_router.workflow_ruletarget import WorkflowRuleTarget
from twilio.task_router.workflow_rule import WorkflowRule
from twilio.task_router.workflow_config import WorkflowConfig
from django.conf import settings
import json


def first(items):
    items = list(items)
    return items[0] if items else None


def build_client():
    account_sid = settings.TWILIO_ACCOUNT_SID
    auth_token = settings.TWILIO_AUTH_TOKEN
    return TwilioTaskRouterClient(account_sid, auth_token)


def get_workspace_by_name(name):
    workspaces = build_client().workspaces.list()
    return first(filter(lambda workspace: workspace.friendly_name == name, workspaces))


def delete_workspace(name):
    workspace = get_workspace_by_name(name)
    build_client().workspaces.delete(workspace.sid)


def create_workspace(name, event_callback):
    client = build_client()
    workspace = get_workspace_by_name(name)
    if not workspace:
        workspace = client.workspaces.create(
                friendly_name=name,
                event_callback_url=event_callback,
                template=None)
    return workspace


def add_worker(workspace, name, attributes):
    client = build_client()
    worker = client.workers(workspace.sid).create(
        friendly_name=name,
        attributes=json.dumps(attributes))
    return worker


def get_activity_by_name(workspace, name):
    activities = build_client().activities(workspace.sid).list()
    return first(filter(lambda activity: activity.friendly_name == name, activities))


def get_queue_by_name(workspace, name):
    queues = build_client().task_queues(workspace.sid).list()
    return first(filter(lambda queue: queue.friendly_name == name, queues))


def add_queue(workspace, name, worker_query):
    client = build_client()
    queue = client.task_queues(workspace.sid).create(
       friendly_name=name,
       reservation_activity_sid=get_activity_by_name(workspace, 'Reserved').sid,
       assignment_activity_sid=get_activity_by_name(workspace, 'Busy').sid,
       target_workers=worker_query
       )
    return queue


def add_workflow(workspace, name, callback='http://example.com/',
                 timeout=30, configuration=None):
    client = build_client()
    workflow = client.workflows(workspace.sid).create(
        friendly_name=name,
        assignment_callback_url=callback,
        fallback_assignment_callback_url=callback,
        task_reservation_timeout=str(timeout),
        configuration=get_workflow_json_configuration(workspace,
                                                      configuration),
        )
    return workflow


def get_workflow_json_configuration(workspace, configuration):
    default_queue = get_queue_by_name(workspace, 'Default')
    defaultRuleTarget = WorkflowRuleTarget(default_queue.sid, '1==1', 1, 30)

    rules = []
    for rule in configuration:
        queue = get_queue_by_name(workspace, rule['targetTaskQueue'])
        queueRuleTargets = []
        queueRuleTarget = WorkflowRuleTarget(queue.sid, None, 5, 30)
        queueRuleTargets.append(queueRuleTarget)
        queueRuleTargets.append(defaultRuleTarget)
        rules.append(WorkflowRule(rule['expression'], queueRuleTargets, None))

    config = WorkflowConfig(rules, None)
    return config.to_json()
