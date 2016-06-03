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
        self.assertEquals(workspace1, workspace)
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
