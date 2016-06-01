from django.core.management.base import BaseCommand
from task_router import creator


class Command(BaseCommand):
    help = 'Creates and configures a Task Router'

    def handle(self, *args, **options):
        workspace = creator.create_workspace('Django Task Router')
        creator.add_worker(workspace, 'Bob', attributes={'products': ['ACME Rockets']})
        creator.add_worker(workspace, 'Alice', attributes={'products': ['ACME TNT']})
        creator.add_queue(workspace, 'Rockets', 'products HAS "ACME Rockets"')
        creator.add_queue(workspace, 'TNT', 'products HAS "ACME TNT"')
        workflow = creator.add_workflow(workspace, 'Sales', callback='http://example.com/', timeout=30)
        print('Configured, workflow sid: %s' % workflow.sid)
