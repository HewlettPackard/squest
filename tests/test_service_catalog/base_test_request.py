from resource_tracker.models import ResourceGroup
from service_catalog.models import Request, Instance, Support
from tests.test_service_catalog.base import BaseTest


class BaseTestRequest(BaseTest):

    def setUp(self):
        super(BaseTestRequest, self).setUp()
        form_data = {'instance_name': 'test instance', 'text_variable': 'my_var'}
        self.test_instance = Instance.objects.create(name="test_instance_1",
                                                     service=self.service_test,
                                                     spoc=self.standard_user)

        # add a first request
        self.test_request = Request.objects.create(fill_in_survey=form_data,
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)

        self.support_test = Support.objects.create(title="support_1", instance=self.test_instance)

        # second instance for second user
        self.test_instance_2 = Instance.objects.create(name="test_instance_2",
                                                       service=self.service_test,
                                                       spoc=self.standard_user_2)
        self.support_test2 = Support.objects.create(title="support_2", instance=self.test_instance_2)


        self.rg_physical_servers = ResourceGroup.objects.create(name="Physical servers")
        self.rg_physical_servers_cpu_attribute = self.rg_physical_servers.add_attribute_definition(name="CPU")
        self.resource_server = self.rg_physical_servers.create_resource(name=f"resource_server")
        self.resource_server.set_attribute(self.rg_physical_servers_cpu_attribute, 12)
