import json
import pytz
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


from .models import Category, ProjectCategory, Report
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
        readonly = self.normalclient.get('/api/v1/category/',
                                         content_type='application/json')

        self.assertEqual(readonly.status_code, status.HTTP_200_OK)
        self.assertEqual(len(readonly.data), 1)
        self.assertEqual(len(readonly.data[0]["categories"]), 2)
        # Should be ordered too
        self.assertEqual(readonly.data[0]["categories"][0]["name"],
                         "Test Cat 2")
        self.assertEqual(readonly.data[0]["categories"][1]["name"],
                         "Test Cat 1")

    def test_get_project_categories_data(self):
        project = self.make_user_project()
        category1 = self.make_category(name="Test Cat 1", order=3)
        category2 = self.make_category(name="Test Cat 2", order=1)
        post_data = {
            "project": "/api/v1/sys/projects/%s/" % project,
            "categories": ["/api/v1/sys/categories/%s/" % category1,
                           "/api/v1/sys/categories/%s/" % category2]
        }
        # Post user project categories
        self.adminclient.post('/api/v1/sys/projectcategories/',
                              json.dumps(post_data),
                              content_type='application/json')

        # Check normal view record access
        readonly = self.normalclient.get('/api/v1/category/%s/' % category1,
                                         content_type='application/json')
        self.assertEqual(readonly.status_code, status.HTTP_200_OK)
        self.assertEqual(readonly.data["name"], "Test Cat 1")

    def test_create_report_data(self):
        project = self.make_user_project()
        category1 = self.make_category(name="Test Cat 1", order=1)
        location1 = Point(18.0000000, -33.0000000)
        post_data = {
            "contact_key": "579ed9e9c0554eeca149d7fccd9b54e5",
            "to_addr": "+27845001001",
            "categories": ["/api/v1/sys/categories/%s/" % category1],
            "project": "/api/v1/sys/projects/%s/" % project,
            "location": self.make_location(18.0000000, -33.0000000),
            "description": "Test incident",
            "incident_at": "2015-02-02 07:10"

        }
        # Post user project categories
        response = self.adminclient.post('/api/v1/sys/reports/',
                                         json.dumps(post_data),
                                         content_type='application/json')
        # print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check DB
        d = Report.objects.last()
        self.assertEqual(d.contact_key, '579ed9e9c0554eeca149d7fccd9b54e5')
        self.assertEqual(d.to_addr, '+27845001001')
        self.assertEqual(d.project.name, 'Test Project 1')
        self.assertEqual(d.categories.all().count(), 1)
        self.assertEqual(d.location.point, location1)
        self.assertEqual(d.description, 'Test incident')
        self.assertEqual(d.incident_at, datetime(2015, 2, 2, 7, 10,
                                                 tzinfo=pytz.utc))

    def test_create_report_data_normalclient(self):
        self.make_user_project()
        category1 = self.make_category(name="Test Cat 1", order=1)
        category2 = self.make_category(name="Test Cat 2", order=1)
        location1 = Point(18.0000000, -33.0000000)
        post_data = {
            "contact_key": "579ed9e9c0554eeca149d7fccd9b54e5",
            "to_addr": "+27845001001",
            "categories": [category1, category2],
            "location": self.make_location(18.0000000, -33.0000000),
            "description": "Test incident",
            "incident_at": "2015-02-02 07:10"

        }
        # Post user project categories
        response = self.normalclient.post('/api/v1/report/',
                                          json.dumps(post_data),
                                          content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check DB has auto-added keys
        d = Report.objects.last()
        self.assertEqual(d.contact_key, '579ed9e9c0554eeca149d7fccd9b54e5')
        self.assertEqual(d.to_addr, '+27845001001')
        self.assertEqual(d.project.name, 'Test Project 1')
        self.assertEqual(d.categories.all().count(), 2)
        self.assertEqual(d.location.point, location1)
        self.assertEqual(d.description, 'Test incident')
        self.assertEqual(d.incident_at, datetime(2015, 2, 2, 7, 10,
                                                 tzinfo=pytz.utc))

    def test_update_report_data_normalclient(self):
        self.make_user_project()
        category1 = self.make_category(name="Test Cat 1", order=1)
        category2 = self.make_category(name="Test Cat 2", order=1)
        post_data = {
            "contact_key": "579ed9e9c0554eeca149d7fccd9b54e5",
            "to_addr": "+27845001001",
            "categories": [category1, category2],
            "location": self.make_location(18.0000000, -33.0000000),
            "incident_at": "2015-02-02 07:10"

        }
        # Post user request without description
        response = self.normalclient.post('/api/v1/report/',
                                          json.dumps(post_data),
                                          content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        rid = response.data["id"]

        patch_data = {
            "description": "Added after"
        }
        # Post user request without description
        response2 = self.normalclient.patch('/api/v1/report/%s/' % rid,
                                            json.dumps(patch_data),
                                            content_type='application/json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        d = Report.objects.last()
        self.assertEqual(d.description, 'Added after')
