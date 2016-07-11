from django.core.management.base import BaseCommand
from task_router import workspace
from django.conf import settings
HOST = settings.HOST
ALICE_NUMBER = settings.ALICE_NUMBER
BOB_NUMBER = settings.BOB_NUMBER


class CreateWorkspaceCommand(BaseCommand):
    help = 'Creates a Task Router Workspace'

    def handle(self, *args, **options):
        workspace.setup()

Command = CreateWorkspaceCommand
