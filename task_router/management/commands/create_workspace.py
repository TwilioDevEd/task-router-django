from django.core.management.base import BaseCommand
from task_router.workspace import create_workspace, delete_workspace
from task_router import parser


class Command(BaseCommand):
    help = 'Creates a Task Router Workspace'

    def add_arguments(self, parser):
        parser.add_argument('host')
        parser.add_argument('bob_number')
        parser.add_argument('alice_number')

    def handle(self, *args, **options):
        workspace_json = parser.parse_workspace_json(options)
        try:
            delete_workspace(workspace_json['name'])
        except:
            pass

        workspace = create_workspace(workspace_json['name'],
                                     workspace_json['event_callback'])

        for worker in workspace_json['workers']:
            workspace.add_worker(worker['name'],
                                 attributes=worker['attributes'])

        for task_queue in workspace_json['task_queues']:
            workspace.add_queue(task_queue['name'],
                                task_queue['targetWorkers'])

        workflow_json = workspace_json['workflow']
        workflow = workspace.add_workflow(workflow_json['name'],
                                          workflow_json['callback'],
                                          workflow_json['timeout'],
                                          workflow_json['routingConfiguration'])

        idle = workspace.get_activity_by_name('Idle')
        print('#########################################')
        print("Workspace 'Django Task Router' was created successfully.")
        print('#########################################')
        print('You have to set the following environment vars:')
        print('export WORKFLOW_SID=%s' % workflow.sid)
        print('export POST_WORK_ACTIVITY_SID=%s' % idle.sid)
        print('#########################################')
