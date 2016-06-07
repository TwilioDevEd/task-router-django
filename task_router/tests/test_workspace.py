from django.test import TestCase
from mock import Mock, patch
from task_router import creator


class WorkspaceTests(TestCase):

    def setUp(self):
        self.router_client_mock = Mock()
        creator.build_client = Mock(return_value=self.router_client_mock)

    def test_get_workspace(self):
        workspaces_mock = Mock()
        workspace1 = Mock()
        workspace1.friendly_name = 'My Workspace'
        workspace2 = Mock()
        workspace2.friendly_name = 'Other'
        workspaces_mock.list.return_value = [workspace1, workspace2]
        self.router_client_mock.workspaces = workspaces_mock

        workspace = creator.get_workspace_by_name('My Workspace')
        self.assertEqual(workspace1, workspace)
        self.assertTrue(workspaces_mock.list.called)

    @patch('task_router.creator.get_workspace_by_name')
    def test_delete_workspace(self, get_workspace_mock):
        workspaces_mock = Mock()
        workspace1 = Mock()
        workspace1.sid = 'sid123'
        get_workspace_mock.return_value = workspace1
        self.router_client_mock.workspaces = workspaces_mock

        creator.delete_workspace('My Workspace')
        workspaces_mock.delete.assert_called_with(workspace1.sid)

    @patch('task_router.creator.get_workspace_by_name')
    def test_create_workspace(self, get_workspace_mock):
        workspaces_mock = Mock()
        get_workspace_mock.return_value = None
        self.router_client_mock.workspaces = workspaces_mock

        creator.create_workspace('My Workspace', event_callback='\\')
        workspaces_mock.create.assert_called_with(event_callback_url='\\',
                                                  friendly_name='My Workspace',
                                                  template=None)

    def test_add_worker(self):
        workers_mock = Mock()
        self.router_client_mock.workers.return_value = workers_mock

        creator.add_worker(Mock(), 'Bob One', attributes={'product': 'Test'})
        workers_mock.create.assert_called_with(
                attributes='{"product": "Test"}', friendly_name='Bob One')

    @patch('task_router.creator.get_queue_by_name')
    @patch('task_router.creator.get_activity_by_name')
    def test_add_queue(self, get_activity_mock, get_queue_mock):
        get_activity_mock.return_value = Mock(sid='123')
        get_queue_mock.return_value = None
        queues_mock = Mock()
        self.router_client_mock.task_queues.return_value = queues_mock

        creator.add_queue(Mock(), 'Users', worker_query="1==1")
        queues_mock.create.assert_called_with(assignment_activity_sid='123',
                                              friendly_name='Users',
                                              reservation_activity_sid='123',
                                              target_workers='1==1')

    @patch('task_router.creator.get_workflow_json_configuration')
    @patch('task_router.creator.get_queue_by_name')
    def test_add_workflow(self, get_queue_mock, get_configuration_mock):
        get_configuration_mock.return_value = '{}'
        get_queue_mock.return_value = Mock(sid='123')
        workflows_mock = Mock()
        self.router_client_mock.workflows.return_value = workflows_mock
        configuration = [{'targetTaskQueue': 'Default', 'expression': '1==1'}]

        creator.add_workflow(Mock(), 'Flows', callback='/back',
                             configuration=configuration)
        workflows_mock.create.assert_called_with(
                assignment_callback_url='/back',
                configuration='{}', fallback_assignment_callback_url='/back',
                friendly_name='Flows', task_reservation_timeout='30')
