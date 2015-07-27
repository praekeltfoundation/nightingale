import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


from .models import Project, UserProject


class APITestCase(TestCase):

    def setUp(self):
        self.adminclient = APIClient()
        self.normalclient = APIClient()


class AuthenticatedAPITestCase(APITestCase):

    def setUp(self):
        super(AuthenticatedAPITestCase, self).setUp()
        self.adminusername = 'testadminuser'
        self.adminpassword = 'testadminpass'
        self.adminuser = User.objects.create_superuser(
            self.adminusername,
            'testadminuser@example.com',
            self.adminpassword)
        admintoken = Token.objects.create(user=self.adminuser)
        self.admintoken = admintoken.key
        self.adminclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admintoken)
        self.normalusername = 'testnormaluser'
        self.normalpassword = 'testnormalpass'
        self.normaluser = User.objects.create_user(
            self.normalusername,
            'testnormaluser@example.com',
            self.normalpassword)
        normaltoken = Token.objects.create(user=self.normaluser)
        self.normaltoken = normaltoken.key
        self.normalclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.normaltoken)


class TestAccountsAPI(AuthenticatedAPITestCase):

    def make_project(self, code="testproject", name="Test Project"):
        post_data = {
            "code": code,
            "name": name,
            "metadata": {'a': 'a', 'b': 2}
        }
        response = self.adminclient.post('/api/v1/sys/projects/',
                                         json.dumps(post_data),
                                         content_type='application/json')
        return response.data["id"]

    def test_login(self):
        request = self.adminclient.post(
            '/api/token-auth/',
            {"username": "testadminuser", "password": "testadminpass"})
        token = request.data.get('token', None)
        self.assertIsNotNone(
            token, "Could not receive authentication token on login post.")
        self.assertEqual(
            request.status_code, 200,
            "Status code on /api/token-auth was %s (should be 200)."
            % request.status_code)

    def test_create_project_data(self):
        post_data = {
            "code": "testproject",
            "name": "Test Project",
            "metadata": {'a': 'a', 'b': 2}
        }
        response = self.adminclient.post('/api/v1/sys/projects/',
                                         json.dumps(post_data),
                                         content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Project.objects.last()
        self.assertEqual(d.code, 'testproject')
        self.assertEqual(d.name, 'Test Project')
        self.assertEqual(d.metadata, {'a': 'a', 'b': '2'})

    def test_create_project_data_denied_normaluser(self):
        post_data = {
            "code": "testproject",
            "name": "Test Project",
            "metadata": {'a': 'a', 'b': 2}
        }
        response = self.normalclient.post('/api/v1/sys/projects/',
                                          json.dumps(post_data),
                                          content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_projects_data(self):
        project1 = self.make_project(code="test1", name="Test 1")
        project2 = self.make_project(code="test2", name="Test 2")
        self.make_project(code="test3", name="Test 3")
        post_data = {
            "user": "/api/v1/sys/users/%s/" % self.normaluser.id,
            "projects": ["/api/v1/sys/projects/%s/" % project1,
                         "/api/v1/sys/projects/%s/" % project2]
        }
        response = self.adminclient.post('/api/v1/sys/userprojects/',
                                         json.dumps(post_data),
                                         content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = UserProject.objects.last()
        self.assertEqual(d.user.username, 'testnormaluser')
        self.assertEqual(d.projects.count(), 2)
