import datetime
import responses
from django.contrib.auth.models import User
from django.test import TestCase
from django.db.models.signals import post_save
from django.contrib.gis.db.models import PointField

from reports.models import Report, Category, ProjectCategory, Location
from accounts.models import Project, UserProject, Integration
from .models import Submission, fire_subm_action_if_undelivered
from .tasks import send_submission


class SubmissionsTestCase(TestCase):
    def _replace_post_save_hooks(self):
        has_listeners = lambda: post_save.has_listeners(Submission)
        assert has_listeners(), (
            "Submission model has no post_save listeners. Make sure helpers"
            " cleaned up properly in earlier tests.")
        post_save.disconnect(fire_subm_action_if_undelivered, sender=Submission)
        assert not has_listeners(), (
            "Submission model still has post_save listeners. Make sure helpers"
            " cleaned up properly in earlier tests.")

    def _restore_post_save_hooks(self):
        has_listeners = lambda: post_save.has_listeners(Submission)
        assert not has_listeners(), (
            "Submission model still has post_save listeners. Make sure helpers"
            " removed them properly in earlier tests.")
        post_save.connect(fire_subm_action_if_undelivered, sender=Submission)

    def setUp(self):
        super(SubmissionsTestCase, self).setUp()
        self._replace_post_save_hooks()
        self.normalusername = 'testnormaluser'
        self.normalpassword = 'testnormalpass'
        self.normaluser = User.objects.create_user(
            self.normalusername,
            'testnormaluser@example.com',
            self.normalpassword)
        self.project = self.make_user_project()

    def tearDown(self):
        self._restore_post_save_hooks()

class TestSubmissions(SubmissionsTestCase):
    def make_ona_integration(self, project, activate = True):
        ona_integration = Integration.objects.create(
            project=project, integration_type="Ona", details = {
                "url": "https://ona.io/api/v1/submissions",
                "username": "testuser",
                "password": "testuserpass",
                "form_id": "test_form"
            },
            active = activate
        )
        ona_integration.save()
        return ona_integration

    def make_user_project(self):
        project3 = Project.objects.create(
            code="TESTPROJ3", name = "Test Project 3")
        userproject = UserProject.objects.create(
            user=self.normaluser)
        userproject.projects.add(project3)
        userproject.save()
        return project3

    def make_category(self, name="test cat", order=1):
        category1 = Category.objects.create(
            name = name,
            order= order,
            metadata= {}
        )
        projectcategory = ProjectCategory.objects.create(
            project=self.project)
        projectcategory.categories.add(category1)
        projectcategory.save()
        return category1

    def make_location(self, x, y):
        point_data = Location.objects.create(point="SRID=4326;POINT (%s %s)" %(x,y))
        point_data.save()
        return point_data

    def make_report(self, project, metadata = {}):
        category1 = self.make_category(name="Test Cat 1", order=1)
        location = self.make_location(18.0000000, -33.0000000)
        report = Report.objects.create(
            contact_key = "579ed9e9c0554eeca149d7fccd9b54e5",
            to_addr = "+27845001001",
            location = location,
            incident_at = datetime.datetime.now(),
            metadata = metadata
        )
        report.save()
        report.categories.add(category1)
        project.reports.add(report)
        return report

    
