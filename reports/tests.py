import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


from .models import Category, ProjectCategory
from accounts.models import Project, UserProject


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


class TestReportsAPI(AuthenticatedAPITestCase):

    def make_category(self, name="test cat", order=1):
        post_data = {
            "name": name,
            "order": order,
            "metadata": {'a': 'a', 'b': 2}
        }
        response = self.adminclient.post('/api/v1/sys/categories/',
                                         json.dumps(post_data),
                                         content_type='application/json')
        return response.data["id"]

    def make_user_project(self):
        project1 = Project.objects.create(
            code="TESTPROJ1", name="Test Project 1")
        Project.objects.create(
            code="TESTPROJ2", name="Test Project 2")
        userproject = UserProject.objects.create(
            user=self.normaluser)
        userproject.projects.add(project1)
        userproject.save()
        return project1.id

    def test_create_category_data(self):
        post_data = {
            "name": "Test Category",
            "order": 2,
            "metadata": {'a': 'a', 'b': 2}
        }
        response = self.adminclient.post('/api/v1/sys/categories/',
                                         json.dumps(post_data),
                                         content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Category.objects.last()
        self.assertEqual(d.name, 'Test Category')
        self.assertEqual(d.order, 2)
        self.assertEqual(d.metadata, {'a': 'a', 'b': '2'})

    def test_create_category_data_denied_normaluser(self):
        post_data = {
            "name": "Test Category",
            "order": 2,
            "metadata": {'a': 'a', 'b': 2}
        }
        response = self.normalclient.post('/api/v1/sys/categories/',
                                          json.dumps(post_data),
                                          content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_project_categories_data(self):
        project = self.make_user_project()
        category1 = self.make_category(name="Test Cat 1", order=3)
        category2 = self.make_category(name="Test Cat 2", order=1)
        self.make_category(name="Test Cat 3", order=2)
        post_data = {
            "project": "/api/v1/sys/projects/%s/" % project,
            "categories": ["/api/v1/sys/categories/%s/" % category1,
                           "/api/v1/sys/categories/%s/" % category2]
        }
        # Post user project categories
        response = self.adminclient.post('/api/v1/sys/projectcategories/',
                                         json.dumps(post_data),
                                         content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check DB
        d = ProjectCategory.objects.last()
        self.assertEqual(d.project.name, 'Test Project 1')
        self.assertEqual(d.categories.count(), 2)

        # Check normal view (user should not have access to Test Cat 3)
        readonly = self.normalclient.get('/api/v1/categories/',
                                         content_type='application/json')

        self.assertEqual(readonly.status_code, status.HTTP_200_OK)
        self.assertEqual(len(readonly.data), 1)
        self.assertEqual(len(readonly.data[0]["categories"]), 2)
        # Should be ordered too
        self.assertEqual(readonly.data[0]["categories"][0]["name"],
                         "Test Cat 2")
        self.assertEqual(readonly.data[0]["categories"][1]["name"],
                         "Test Cat 1")
