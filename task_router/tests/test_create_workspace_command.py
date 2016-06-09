from django.test import TestCase
from mock import Mock, call
from ..management.commands.create_workspace import CreateWorkspaceCommand


class CreateWorkspaceCommandTests(TestCase):

    def setUp(self):
        self.command = CreateWorkspaceCommand()
        self.command.workspace = Mock()
        self.workspace = self.command.workspace

    def test_add_workers_from_parsed_json(self):
        workers = [
            {'name': 'Bob',
             'attributes': {'products': ['TestProduct1']}},
            {'name': 'Alice',
             'attributes': {'products': ['TestProduct2']}}]
        self.command.add_workers(workers)

        bob_call = call('Bob', attributes={'products': ['TestProduct1']})
        alice_call = call('Alice', attributes={'products': ['TestProduct2']})
        self.workspace.add_worker.assert_has_calls([bob_call, alice_call])

    def test_add_task_queues_from_parsed_json(self):
        task_queues = [
            {'name': 'Queue1',
             'targetWorkers': '"TestProduct1" in products'},
            {'name': 'Queue2',
             'targetWorkers': '"TestProduct2" in products'}]
        self.command.add_task_queues(task_queues)

        queue1_call = call('Queue1', '"TestProduct1" in products')
        queue2_call = call('Queue2', '"TestProduct2" in products')
        self.workspace.add_queue.assert_has_calls([queue1_call, queue2_call])

    def test_add_workflows_from_parsed_json(self):
        workflow = {'name': 'Workflow1',
                    'callback': '/endpoint1',
                    'timeout': '42',
                    'routingConfiguration': 'config1'}
        self.command.add_workflow(workflow)

        self.workspace.add_workflow.assert_called_with(
                'Workflow1', '/endpoint1', '42', 'config1')
