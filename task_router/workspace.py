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


def get_by_name(name):
    workspaces = build_client().workspaces.list()
    return first(filter(lambda workspace: workspace.friendly_name == name, workspaces))


def delete(name):
    workspace = get_by_name(name)
    build_client().workspaces.delete(workspace.sid)


def create(name, event_callback):
    client = build_client()
    workspace = get_by_name(name)
    if not workspace:
        workspace = client.workspaces.create(
                friendly_name=name,
                event_callback_url=event_callback,
                template=None)
    workspace = Workspace(workspace)
    client.workspaces.update(
            workspace.sid,
            timeout_activity_sid=workspace.get_activity_by_name('Idle').sid)
    return workspace


class Workspace():

    def __init__(self, workspace):
        self.sid = workspace.sid
        self.client = build_client()

    def add_worker(self, name, attributes):
        worker = self.client.workers(self.sid).create(
            activity_sid=self.get_activity_by_name('Idle').sid,
            friendly_name=name,
            attributes=json.dumps(attributes))
        return worker

    def add_queue(self, name, worker_query):
        reservation_activity = self.get_activity_by_name('Reserved')
        assignment_activity = self.get_activity_by_name('Busy')
        queue = self.client.task_queues(self.sid).create(
                friendly_name=name,
                reservation_activity_sid=reservation_activity.sid,
                assignment_activity_sid=assignment_activity.sid,
                target_workers=worker_query
                )
        return queue

    def add_workflow(self, name, callback='http://example.com/',
                     timeout=30, configuration=None):
        workflow = self.client.workflows(self.sid).create(
            friendly_name=name,
            assignment_callback_url=callback,
            fallback_assignment_callback_url=callback,
            task_reservation_timeout=str(timeout),
            configuration=self.get_workflow_json_configuration(configuration))
        return workflow

    def get_activity_by_name(self, name):
        activities = self.client.activities(self.sid).list()
        return first(filter(lambda activity: activity.friendly_name == name, activities))

    def get_queue_by_name(self, name):
        queues = self.client.task_queues(self.sid).list()
        return first(filter(lambda queue: queue.friendly_name == name, queues))

    def get_workflow_json_configuration(self, configuration):
        default_queue = self.get_queue_by_name('Default')
        defaultRuleTarget = WorkflowRuleTarget(default_queue.sid, '1==1', 1, 30)

        rules = []
        for rule in configuration:
            queue = self.get_queue_by_name(rule['targetTaskQueue'])
            queueRuleTargets = []
            queueRuleTarget = WorkflowRuleTarget(queue.sid, None, 5, 30)
            queueRuleTargets.append(queueRuleTarget)
            queueRuleTargets.append(defaultRuleTarget)
            rules.append(WorkflowRule(rule['expression'], queueRuleTargets, None))

        config = WorkflowConfig(rules, None)
        return config.to_json()
