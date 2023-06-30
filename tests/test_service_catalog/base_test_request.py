from django.test import TestCase
from rest_framework.test import APITestCase

from resource_tracker_v2.models import ResourceGroup, AttributeDefinition, Transformer, Resource
from service_catalog.models import Request, Instance, Support
from tests.test_service_catalog.base import BaseTestCommon


class BaseTestRequestCommon(BaseTestCommon):

    def setUp(self):
        super(BaseTestRequestCommon, self).setUp()
        form_data = {'text_variable': 'my_var'}
        self.test_instance = Instance.objects.create(name="test_instance_1",
                                                     service=self.service_test,
                                                     quota_scope=self.test_quota_scope_org,
                                                     requester=self.standard_user)

        # add a first request
        self.test_request = Request.objects.create(fill_in_survey=form_data,
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)

        self.support_test = Support.objects.create(title="support_1", instance=self.test_instance)

        # second instance for second user
        self.test_instance_2 = Instance.objects.create(name="test_instance_2",
                                                       service=self.service_test,
                                                       quota_scope=self.test_quota_scope_org2,
                                                       requester=self.standard_user_2)
        self.support_test2 = Support.objects.create(title="support_2", instance=self.test_instance_2)

        self.rg_physical_servers = ResourceGroup.objects.create(name="Physical servers")
        self.cpu_attribute = AttributeDefinition.objects.create(name="CPU")
        Transformer.objects.create(resource_group=self.rg_physical_servers,
                                   attribute_definition=self.cpu_attribute)
        self.resource_server = Resource.objects.create(name="server1", resource_group=self.rg_physical_servers)
        self.resource_server.set_attribute(self.cpu_attribute, 12)


class BaseTestRequest(TestCase, BaseTestRequestCommon):
    pass


class BaseTestRequestAPI(APITestCase, BaseTestRequestCommon):
    pass
