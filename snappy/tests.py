import json
import responses
from django.contrib.auth.models import User
from django.test import TestCase
from django.db.models.signals import post_save
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from reports.models import Report
from accounts.models import Project, UserProject
from .models import Message, fire_msg_action_if_undelivered


class APITestCase(TestCase):

    def setUp(self):
        self.adminclient = APIClient()
        self.normalclient = APIClient()


class AuthenticatedAPITestCase(APITestCase):

    def _replace_post_save_hooks(self):
        has_listeners = lambda: post_save.has_listeners(Message)
        assert has_listeners(), (
            "Message model has no post_save listeners. Make sure"
            " helpers cleaned up properly in earlier tests.")
        post_save.disconnect(fire_msg_action_if_undelivered, sender=Message)
        assert not has_listeners(), (
            "Message model still has post_save listeners. Make sure"
            " helpers cleaned up properly in earlier tests.")

    def _restore_post_save_hooks(self):
        has_listeners = lambda: post_save.has_listeners(Message)
        assert not has_listeners(), (
            "Message model still has post_save listeners. Make sure"
            " helpers removed them properly in earlier tests.")
        post_save.connect(fire_msg_action_if_undelivered, sender=Message)

    def setUp(self):
        super(AuthenticatedAPITestCase, self).setUp()
        self._replace_post_save_hooks()
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
        self.vumi_id = self.make_vumi_integration(self.project_id)
        self.report_id = self.make_report()

    def tearDown(self):
        self._restore_post_save_hooks()


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

    def make_vumi_integration(self, project):
        post_data = {
            "project": "/api/v1/sys/projects/%s/" % project,
            "integration_type": "Vumi",
            "details": {
                "vumi_api_url": "http://example.com/api/v1/go",
                "vumi_account_key": "acc-key",
                "vumi_conversation_key": "conv-key",
                "vumi_conversation_token": "conv-token"
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
            "location": self.make_location(18.0000000, -33.0000000)
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

    @responses.activate
    def test_create_message_fire_task(self):
        # restore the post_save hook just for this test
        post_save.connect(fire_msg_action_if_undelivered, sender=Message)

        responses.add(responses.POST,
                      "https://app.besnappy.com/api/v1/note",
                      body="nonce", status=200,
                      content_type='application/json')

        responses.add(responses.POST,
                      "https://app.besnappy.com/api/v1/ticket/nonce/tags",
                      body="OK", status=200,
                      content_type='application/json')

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
        self.assertEqual(d.report.metadata["snappy_nonce"], 'nonce')
        self.assertEqual(len(responses.calls), 2)
        # remove to stop tearDown errors
        post_save.disconnect(fire_msg_action_if_undelivered, sender=Message)

    @responses.activate
    def test_create_webhook_fire_task(self):
        # restore the post_save hook just for this test
        post_save.connect(fire_msg_action_if_undelivered, sender=Message)

        responses.add(responses.POST,
                      "https://app.besnappy.com/api/v1/note",
                      body="nonce", status=200,
                      content_type='application/json')

        responses.add(responses.POST,
                      "https://app.besnappy.com/api/v1/ticket/nonce/tags",
                      body="OK", status=200,
                      content_type='application/json')

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
        self.assertEqual(d.report.metadata["snappy_nonce"], 'nonce')
        self.assertEqual(len(responses.calls), 2)
        # remove to stop tearDown errors
        post_save.disconnect(fire_msg_action_if_undelivered, sender=Message)

        # flake8: noqa
        webhookbody = "event=message.outgoing&data=%7B%22note%22%3A%7B%22id%22%3A101%2C%22account_id%22%3A50%2C%22ticket_id%22%3A11%2C%22facebook_message%22%3Anull%2C%22created_by_staff_id%22%3A2%2C%22created_by_contact_id%22%3Anull%2C%22scope%22%3A%22public%22%2C%22created_at%22%3A1438690631%2C%22updated_at%22%3A%222015-08-04%2012%3A17%3A11%22%2C%22content%22%3A%22This%20is%20a%20reply%5Cn%22%2C%22system%22%3A0%2C%22using_html%22%3A0%2C%22raw_headers%22%3Anull%2C%22ticket%22%3A%7B%22id%22%3A11%2C%22account_id%22%3A50%2C%22mailbox_id%22%3A10%2C%22created_via%22%3A%22email%22%2C%22last_reply_by%22%3A%22staff%22%2C%22last_reply_at%22%3A1438690631%2C%22opened_by_staff_id%22%3Anull%2C%22opened_by_contact_id%22%3A26305%2C%22opened_at%22%3A1438680515%2C%22status%22%3A%22replied%22%2C%22first_staff_reply_at%22%3A%222015-08-04%2010%3A15%3A07%22%2C%22default_subject%22%3A%22Re%3A%20Report%20from%20%2B27845001001%22%2C%22summary%22%3A%22This%20is%20a%20reply%5Cn%22%2C%22next_recipients%22%3A%7B%22cc%22%3A%5B%5D%2C%22bcc%22%3A%5B%5D%2C%22to%22%3A%5B%7B%22name%22%3A%22%2B27845001001%22%2C%22address%22%3A%22mike%2B11%40example.org%22%7D%5D%7D%2C%22nonce%22%3A%22nonce%22%2C%22created_at%22%3A1438680515%2C%22updated_at%22%3A%222015-08-04%2012%3A17%3A21%22%2C%22tags%22%3A%5B%22%23Arrest%22%5D%2C%22email_message_id%22%3A%22%3C8e2f6293e223cb589859addcbb39dfe1%40swift.generated%3E%22%2C%22contacts%22%3A%5B%7B%22id%22%3A26305%2C%22account_id%22%3A50%2C%22first_name%22%3A%22%22%2C%22last_name%22%3A%22%22%2C%22value%22%3A%22mike%2B11%40example.org%22%2C%22provider%22%3A%22email%22%2C%22created_at%22%3A%222013-10-31%2011%3A17%3A37%22%2C%22updated_at%22%3A%222013-10-31%2011%3A17%3A37%22%2C%22pivot%22%3A%7B%22ticket_id%22%3A668781%2C%22contact_id%22%3A26305%2C%22type%22%3A%22to%22%7D%2C%22address%22%3A%22mike%2B11%40example.org%22%2C%22type%22%3A%22to%22%7D%2C%7B%22id%22%3A26305%2C%22account_id%22%3A50%2C%22first_name%22%3A%22%22%2C%22last_name%22%3A%22%22%2C%22value%22%3A%22mike%2B11%40example.org%22%2C%22provider%22%3A%22email%22%2C%22created_at%22%3A%222013-10-31%2011%3A17%3A37%22%2C%22updated_at%22%3A%222013-10-31%2011%3A17%3A37%22%2C%22pivot%22%3A%7B%22ticket_id%22%3A11%2C%22contact_id%22%3A26305%2C%22type%22%3A%22from%22%7D%2C%22address%22%3A%22mike%2B11%40example.org%22%2C%22type%22%3A%22from%22%7D%5D%2C%22opener%22%3A%7B%22id%22%3A26305%2C%22account_id%22%3A50%2C%22first_name%22%3A%22%22%2C%22last_name%22%3A%22%22%2C%22value%22%3A%22mike%2B11%40example.org%22%2C%22provider%22%3A%22email%22%2C%22created_at%22%3A%222013-10-31%2011%3A17%3A37%22%2C%22updated_at%22%3A%222013-10-31%2011%3A17%3A37%22%2C%22address%22%3A%22mike%2B11%40example.org%22%7D%7D%2C%22creator%22%3A%7B%22id%22%3A58%2C%22email%22%3A%22devops%40example.com%22%2C%22sms_number%22%3A%2200271234567%22%2C%22first_name%22%3A%22Mike%22%2C%22last_name%22%3A%22Jones%22%2C%22photo%22%3Anull%2C%22culture%22%3A%22en%22%2C%22notify%22%3A1%2C%22created_at%22%3A%222012-12-10%2014%3A25%3A16%22%2C%22updated_at%22%3A%222015-08-03%2009%3A27%3A56%22%2C%22signature%22%3A%22%22%2C%22tour_played%22%3A1%2C%22timezone%22%3A%22Africa%2FJohannesburg%22%2C%22notify_new%22%3A1%2C%22news_read_at%22%3A%222015-08-03%2009%3A27%3A48%22%2C%22apple_device_token%22%3A%22nonono%22%2C%22remember_token%22%3A%22nono%22%2C%22mobile_notify%22%3A1%2C%22mobile_notify_new%22%3A1%2C%22mobile_viewing_account%22%3A200%2C%22verification_token%22%3A%228098098098%22%2C%22verified%22%3Atrue%2C%22android_device_token%22%3Anull%2C%22address%22%3A%22devops%40example.com%22%7D%7D%7D"

        response = self.adminclient.post(
            '/api/v1/snappywebhook/',
            webhookbody,
            content_type='application/x-www-form-urlencoded; charset=utf-8')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = Message.objects.last()
        self.assertEqual(d.message, 'This is a reply\n')
        self.assertEqual(d.target, 'VUMI')
        self.assertEqual(d.to_addr, '+27845001001')

    @responses.activate
    def test_create_message_reply_fire_task(self):
        # Update report as delivered
        report = Report.objects.get(id=self.report_id)
        report.metadata["snappy_nonce"] = "nonce"
        report.save()
        # restore the post_save hook just for this test
        post_save.connect(fire_msg_action_if_undelivered, sender=Message)

        responses.add(responses.POST,
                      "https://app.besnappy.com/api/v1/note",
                      body="nonce2", status=200,
                      content_type='application/json')

        post_data = {
            "report": self.report_id,
            "message": "This is a test",
            "contact_key": "579ed9e9c0554eeca149d7fccd9b54e5",
            "from_addr": "+27845001001",
        }
        response = self.normalclient.post('/api/v1/snappymessage/',
                                          json.dumps(post_data),
                                          content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Message.objects.last()
        self.assertEqual(d.delivered, True)
        # not updated to nonce2 because update
        self.assertEqual(d.report.metadata["snappy_nonce"], 'nonce')
        self.assertEqual(len(responses.calls), 1)
        # remove to stop tearDown errors
        post_save.disconnect(fire_msg_action_if_undelivered, sender=Message)
