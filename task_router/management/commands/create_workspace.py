from django.core.management.base import BaseCommand
from task_router import creator


class Command(BaseCommand):
    help = 'Creates a Task Router Workspace'

    def add_arguments(self, parser):
        parser.add_argument('url')
        parser.add_argument('bob_number')
        parser.add_argument('alice_number')

    def handle(self, *args, **options):
        url = options['url']
        bob_number = options['bob_number']
        alice_number = options['alice_number']
        workspace = creator.create_workspace('Django Task Router')
        bob = creator.add_worker(workspace, 'Bob',
                           attributes={
                             'products': ['ACMERockets'],
                             'contact_uri': bob_number})
        alice = creator.add_worker(workspace, 'Alice',
                           attributes={
                             'products': ['AACMETNT'],
                             'contact_uri': alice_number})
        creator.add_queue(workspace, 'Rockets', 'products HAS "ACMERockets"')
        creator.add_queue(workspace, 'TNT', 'products HAS "ACMETNT"')
        creator.add_queue(workspace, 'Default', '1==1')
        workflow = creator.add_workflow(workspace, 'Sales',
                                        callback=url+'/assignment',
                                        timeout=30)
        idle = creator.get_activity_by_name(workspace, 'Idle')
        print('#########################################')
        print("Workspace 'Django Task Router' was created successfully.")
        print('#########################################')
        print('You have to set the following environment vars:')
        print('export WORKSPACE_SID=%s' % workspace.sid)
        print('export WORKFLOW_SID=%s' % workflow.sid)
        print('export POST_WORK_ACTIVITY_SID=%s' % idle.sid)
        print('#########################################')
        print('To access agent Bob\'s page > http://localhost:8000/agents/%s' % bob.sid)
        print('To access agent Alice\'s page > http://localhost:8000/agents/%s' % alice.sid)
