import json
import pytz
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


from reports.models import Category, ProjectCategory, Report
from accounts.models import Project, UserProject
from .models import Message


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
        self.project_id = self.make_user_project()
        self.snappy_id = self.make_snappy_integration(self.project_id)
        self.report_id = self.make_report()


class TestMessagesAPI(AuthenticatedAPITestCase):

    def make_snappy_integration(self, project):
        post_data = {
            "project": "/api/v1/sys/projects/%s/" % project,
            "integration_type": "Snappy",
            "details": {
                "snappy_api_key": "blah",
                "snappy_mailbox_id": "10",
                "snappy_api_url": "https://app.besnappy.com/api/v1",
                "snappy_from_email": "mike+%s@example.org"
            },
            "active": True
        }
        response = self.adminclient.post('/api/v1/sys/integrations/',
                                         json.dumps(post_data),
                                         content_type='application/json')
        return response.data["id"]

    def make_user_project(self):
        project1 = Project.objects.create(
            code="TESTPROJ1", name="Test Project 1")
        userproject = UserProject.objects.create(
            user=self.normaluser)
        userproject.projects.add(project1)
        userproject.save()
        return str(project1.id)

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

    def make_location(self, x, y):
        point_data = {
            "point": {
                "type": "Point",
                "coordinates": [
                        x,
                        y
                ]
            }
        }
        return point_data

    def make_report(self):
        category1 = self.make_category(name="Test Cat 1", order=1)
        post_data = {
            "contact_key": "579ed9e9c0554eeca149d7fccd9b54e5",
            "to_addr": "+27845001001",
            "categories": [category1],
            "location": self.make_location(18.0000000, -33.0000000),
        }
        # Post user request without description
        response = self.normalclient.post('/api/v1/report/',
                                          json.dumps(post_data),
                                          content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response.data["id"]

    def test_create_message_data(self):
        post_data = {
            "integration": "/api/v1/sys/integrations/%s/" % self.snappy_id,
            "report": "/api/v1/sys/reports/%s/" % self.report_id,
            "target": "SNAPPY",
            "message": "This is a test",
            "contact_key": "579ed9e9c0554eeca149d7fccd9b54e5",
            "from_addr": "+27845001001",
        }
        response = self.adminclient.post('/api/v1/sys/messages/',
                                         json.dumps(post_data),
                                         content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Message.objects.last()
        self.assertEqual(d.message, 'This is a test')

    # def test_create_category_data_denied_normaluser(self):
    #     post_data = {
    #         "name": "Test Category",
    #         "order": 2,
    #         "metadata": {'a': 'a', 'b': 2}
    #     }
    #     response = self.normalclient.post('/api/v1/sys/categories/',
    #                                       json.dumps(post_data),
    #                                       content_type='application/json')

    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
