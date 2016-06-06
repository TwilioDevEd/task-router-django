from django.core.management.base import BaseCommand
from task_router import creator
import json


class Command(BaseCommand):
    help = 'Deletes Sample Task Router Workspace'

    def handle(self, *args, **options):
        with open('workspace.json') as json_file:
            workspace_json = json.load(json_file)
        creator.delete_workspace(workspace_json['name'])
