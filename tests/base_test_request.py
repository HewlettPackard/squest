from guardian.mixins import UserObjectPermission

from service_catalog.models import Request, Instance, Support
from tests.base import BaseTest


class BaseTestRequest(BaseTest):

    def setUp(self):
        super(BaseTestRequest, self).setUp()
        form_data = {'instance_name': 'test instance', 'text_variable': 'my_var'}
        self.test_instance = Instance.objects.create(name="test_instance_1", service=self.service_test)
        # give user perm on this instance
        UserObjectPermission.objects.assign_perm('change_instance', self.standard_user, obj=self.test_instance)
        UserObjectPermission.objects.assign_perm('view_instance', self.standard_user, obj=self.test_instance)
        # add a first request
        self.test_request = Request.objects.create(fill_in_survey=form_data,
                                                   instance=self.test_instance,
                                                   operation=self.create_operation_test,
                                                   user=self.standard_user)

        self.support_test = Support.objects.create(title="support_1", instance=self.test_instance)

        # second instance for second user
        self.test_instance_2 = Instance.objects.create(name="test_instance_2", service=self.service_test)
        # give user perm on this instance
        UserObjectPermission.objects.assign_perm('change_instance', self.standard_user_2, obj=self.test_instance_2)
        UserObjectPermission.objects.assign_perm('view_instance', self.standard_user_2, obj=self.test_instance_2)
