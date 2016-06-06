from django.core.management.base import BaseCommand
from task_router import creator
import json


class Command(BaseCommand):
    help = 'Creates a Task Router Workspace'

    def add_arguments(self, parser):
        parser.add_argument('host')
        parser.add_argument('bob_number')
        parser.add_argument('alice_number')

    def handle(self, *args, **options):
        with open('workspace.json') as json_file:
            json_string = json_file.read()
            json_string = json_string % options
            workspace_json = json.loads(json_string)
        workspace = creator.create_workspace(workspace_json['name'],
                                             workspace_json['event_callback'])
        for worker in workspace_json['workers']:
            creator.add_worker(workspace, worker['name'],
                               attributes=worker['attributes'])
        for task_queue in workspace_json['task_queues']:
            creator.add_queue(workspace, task_queue['name'],
                              task_queue['targetWorkers'])
        workflow_json = workspace_json['workflow']
        workflow = creator.add_workflow(workspace, workflow_json['name'],
                                        workflow_json['callback'],
                                        workflow_json['timeout'],
                                        workflow_json['routingConfiguration'])
        idle = creator.get_activity_by_name(workspace, 'Idle')
        print('#########################################')
        print("Workspace 'Django Task Router' was created successfully.")
        print('#########################################')
        print('You have to set the following environment vars:')
        print('export WORKSPACE_SID=%s' % workspace.sid)
        print('export WORKFLOW_SID=%s' % workflow.sid)
        print('export POST_WORK_ACTIVITY_SID=%s' % idle.sid)
        print('#########################################')
        # print('Bob\'s http://localhost:8000/agents/%s' % bob.sid)
        # print('Alice\' > http://localhost:8000/agents/%s' % alice.sid)
