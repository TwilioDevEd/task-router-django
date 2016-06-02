from django.core.management.base import BaseCommand
from task_router import creator


class Command(BaseCommand):
    help = 'Creates and configures a Task Router'

    def add_arguments(self, parser):
        parser.add_argument('url')

    def handle(self, *args, **options):
        url = options['url']
        workspace = creator.create_workspace('Django Task Router')
        creator.add_worker(workspace, 'Bob', attributes={'products': ['ACMERockets']})
        creator.add_worker(workspace, 'Alice', attributes={'products': ['ACMETNT']})
        creator.add_queue(workspace, 'Rockets', 'products HAS "ACMERockets"')
        creator.add_queue(workspace, 'TNT', 'products HAS "ACMETNT"')
        workflow = creator.add_workflow(workspace, 'Sales', callback=url+'/assignment', timeout=30)
        print('Configured, workflow sid: %s' % workflow.sid)
