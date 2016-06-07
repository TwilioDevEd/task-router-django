from django.test import TestCase
from mock import Mock, patch
from task_router import workspace
from task_router.workspace import Workspace


class WorkspaceTests(TestCase):

    def setUp(self):
        self.router_client_mock = Mock()
        workspace.build_client = Mock(return_value=self.router_client_mock)

    def test_get_workspace(self):
        workspaces_mock = Mock()
        workspace1 = Mock()
        workspace1.friendly_name = 'My Workspace'
        workspace2 = Mock()
        workspace2.friendly_name = 'Other'
        workspaces_mock.list.return_value = [workspace1, workspace2]
        self.router_client_mock.workspaces = workspaces_mock

        workspace_instance = workspace.get_workspace_by_name('My Workspace')
        self.assertEqual(workspace1, workspace_instance)
        self.assertTrue(workspaces_mock.list.called)

    @patch('task_router.workspace.get_workspace_by_name')
    def test_delete_workspace(self, get_workspace_mock):
        workspaces_mock = Mock()
        workspace1 = Mock()
        workspace1.sid = 'sid123'
        get_workspace_mock.return_value = workspace1
        self.router_client_mock.workspaces = workspaces_mock

        workspace.delete_workspace('My Workspace')
        workspaces_mock.delete.assert_called_with(workspace1.sid)

    @patch('task_router.workspace.get_workspace_by_name')
    def test_create_workspace(self, get_workspace_mock):
        workspaces_mock = Mock()
        get_workspace_mock.return_value = None
        self.router_client_mock.workspaces = workspaces_mock

        workspace.create_workspace('My Workspace', event_callback='\\')
        workspaces_mock.create.assert_called_with(event_callback_url='\\',
                                                  friendly_name='My Workspace',
                                                  template=None)

    def test_add_worker(self):
        workers_mock = Mock()
        self.router_client_mock.workers.return_value = workers_mock

        Workspace(Mock()).add_worker('Bob One', attributes={'product': 'Test'})
        workers_mock.create.assert_called_with(
                attributes='{"product": "Test"}', friendly_name='Bob One')

    def test_add_queue(self):
        queues_mock = Mock()
        activities_mock = Mock()
        mocked_activities = [Mock(sid='123', friendly_name='Reserved'),
                             Mock(sid='321', friendly_name='Busy')]
        activities_mock.list.return_value = mocked_activities
        self.router_client_mock.task_queues.return_value = queues_mock
        self.router_client_mock.activities.return_value = activities_mock
        workspace_mock = Mock()

        Workspace(workspace_mock).add_queue('Users', worker_query="1==1")
        queues_mock.create.assert_called_with(assignment_activity_sid='321',
                                              friendly_name='Users',
                                              reservation_activity_sid='123',
                                              target_workers='1==1')

    def test_add_workflow(self):
        workflows_mock = Mock()
        self.router_client_mock.workflows.return_value = workflows_mock
        workspace = Workspace(Mock())
        workspace.get_workflow_json_configuration = lambda x: '{}'

        workspace.add_workflow('Flows', callback='/back')

        workflows_mock.create.assert_called_with(
                assignment_callback_url='/back',
                configuration='{}', fallback_assignment_callback_url='/back',
                friendly_name='Flows', task_reservation_timeout='30')
