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
