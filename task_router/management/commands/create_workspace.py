from django.core.management.base import BaseCommand
from task_router import creator


class Command(BaseCommand):
    help = 'Creates and configures a Task Router'

    def add_arguments(self, parser):
        parser.add_argument('url')
        parser.add_argument('bob_number')

    def handle(self, *args, **options):
        url = options['url']
        bob_number = options['bob_number']
        workspace = creator.create_workspace('Django Task Router')
        creator.add_worker(workspace, 'Bob', attributes={'products': ['ACMERockets'], 'contact_uri': bob_number})
        creator.add_worker(workspace, 'Alice', attributes={'products': ['ACMETNT']})
        creator.add_queue(workspace, 'Rockets', 'products HAS "ACMERockets"')
        creator.add_queue(workspace, 'TNT', 'products HAS "ACMETNT"')
        workflow = creator.add_workflow(workspace, 'Sales', callback=url+'/assignment', timeout=30)
        print('Configured, remember to configure the environment vars:')
        print('export WORKSPACE_SID=%s' % workspace.sid)
        print('export WORKFLOW_SID=%s' % workflow.sid)