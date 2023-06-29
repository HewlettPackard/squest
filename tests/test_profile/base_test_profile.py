from django.test import TestCase
from rest_framework.test import APITestCase

from profiles.models import RequestNotification, InstanceNotification, Organization, Team
from service_catalog.models import Request, RequestState, InstanceState, Instance
from tests.test_service_catalog.base_test_request import BaseTestRequestCommon


class BaseTestProfileCommon(BaseTestRequestCommon):

    def setUp(self):
        super(BaseTestProfileCommon, self).setUp()
        self.test_instance.spec = {
            "spec_key1": "spec_value1"
        }
        self.test_instance.user_spec = {
            "user_spec_key1": "user_spec_value1"
        }
        self.test_instance.save()

        self.request_notification_filter_test = RequestNotification.objects.create(name="request_test_filter",
                                                                                   profile=self.superuser.profile)
        self.request_notification_filter_test_2 = RequestNotification.objects.create(name="request_test_filter_2",
                                                                                     profile=self.superuser.profile)
        self.request_notification_filter_test_3 = RequestNotification.objects.create(name="request_test_filter_3",
                                                                                     profile=self.superuser_2.profile)

        self.support_notification_filter_test = InstanceNotification.objects.create(name="support_test_filter",
                                                                                    profile=self.superuser.profile)
        self.support_notification_filter_test_2 = InstanceNotification.objects.create(name="support_test_filter_2",
                                                                                      profile=self.superuser.profile)
        self.support_notification_filter_test_3 = InstanceNotification.objects.create(name="support_test_filter_3",
                                                                                      profile=self.superuser_2.profile)

        self.test_instance_2.service = self.service_test_2
        self.test_instance_2.state = InstanceState.AVAILABLE
        self.test_instance_2.save()

        self.test_request_2 = Request.objects.create(fill_in_survey={},
                                                     instance=self.test_instance_2,
                                                     operation=self.update_operation_test,
                                                     user=self.standard_user)
        self.test_request_2.state = RequestState.ACCEPTED
        self.test_request_2.save()

        self.test_instance_3 = Instance.objects.create(name="test_instance_3",
                                                       service=self.service_empty_survey_test,
                                                       requester=self.standard_user_2,
                                                       state=InstanceState.ARCHIVED)
        self.test_request_3 = Request.objects.create(fill_in_survey={},
                                                     instance=self.test_instance_3,
                                                     operation=self.delete_operation_test,
                                                     user=self.standard_user,
                                                     state=RequestState.FAILED)

        self.test_org = Organization.objects.create(name="test_org")
        self.team1 = Team.objects.create(org=self.test_org, name="team1")


class BaseTestProfile(TestCase, BaseTestProfileCommon):
    pass


class BaseTestProfileAPI(APITestCase, BaseTestProfileCommon):
    pass
