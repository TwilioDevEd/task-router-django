from django.test import TestCase, Client


class HomePageTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        # Act
        response = self.client.get('/')

        # Assert
        # This is a class-based view, so we can mostly rely on Django's own
        # tests to make sure it works. We'll check for a bit of copy, though
        self.assertIn('Task Router', str(response.content))
