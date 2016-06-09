from django.core.management.base import BaseCommand
from task_router import workspace_parser
from task_router import workspace


class CreateWorkspaceCommand(BaseCommand):
    help = 'Creates a Task Router Workspace'

    def add_arguments(self, parser):
        parser.add_argument('host')
        parser.add_argument('bob_number')
        parser.add_argument('alice_number')

    def handle(self, *args, **options):
        workspace_json = workspace_parser.parse(options)
        try:
            workspace.delete(workspace_json['name'])
        except:
            pass

        self.workspace = workspace.create(workspace_json['name'],
                                          workspace_json['event_callback'])

        self.add_workers(workspace_json['workers'])

        self.add_task_queues(workspace_json['task_queues'])

        workflow = self.add_workflow(workspace_json['workflow'])

        idle = self.workspace.get_activity_by_name('Idle')
        print('#########################################')
        print("Workspace 'Django Task Router' was created successfully.")
        print('#########################################')
        print('You have to set the following environment vars:')
        print('export WORKFLOW_SID=%s' % workflow.sid)
        print('export POST_WORK_ACTIVITY_SID=%s' % idle.sid)
        print('#########################################')

    def add_workers(self, workers):
        for worker in workers:
            self.workspace.add_worker(worker['name'],
                                      attributes=worker['attributes'])

    def add_task_queues(self, task_queues):
        for task_queue in task_queues:
            self.workspace.add_queue(task_queue['name'],
                                     task_queue['targetWorkers'])

    def add_workflow(self, workflow):
        return self.workspace.add_workflow(workflow['name'],
                                           workflow['callback'],
                                           workflow['timeout'],
                                           workflow['routingConfiguration'])

Command = CreateWorkspaceCommand
