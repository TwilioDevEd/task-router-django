from django.core.management.base import BaseCommand
from task_router import creator


class Command(BaseCommand):
    help = 'Deletes Sample Task Router Workspace'

    def handle(self, *args, **options):
        creator.delete_workspace('Django Task Router')
