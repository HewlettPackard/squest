from service_catalog.forms import ServiceForm
from service_catalog.forms.form_utils import FormUtils
from service_catalog.models import OperationType
from tests.test_service_catalog.base import BaseTest


class TestServiceForm(BaseTest):

    def setUp(self):
        super(TestServiceForm, self).setUp()
        self.data_list = [
            {
                "name": "new_service",
                "description": "a new service",
                "permission": FormUtils.get_default_permission_for_operation(),
            },
            {
                "name": "new_service_2",
                "description": "a new service 2",
                "permission": FormUtils.get_default_permission_for_operation(),
            },
            {
                "name": "new_service_3",
                "description": "a new service 3",
                "permission": FormUtils.get_default_permission_for_operation(),
            },
            {
                "name": "new_service_4",
                "description": "a new service 4",
                "permission": -1,
            },
            {
                "name": "new_service_5",
                "description": "a new service 5",
                "permission": FormUtils.get_default_permission_for_operation(),
            },
        ]
        self.failed_expected = ["new_service_4"]

    def test_create_service(self):
        for data in self.data_list:
            form = ServiceForm(data)
            if form.is_valid():
                new_service = form.save()
                test_list = self.get_test_list(data, new_service)
                for test in test_list:
                    self.assertEqual(test['value'], test['expected'])
            else:
                self.assertIn(data['name'], self.failed_expected)

    def test_edit_service(self):
        for data in self.data_list:
            form = ServiceForm(data, instance=self.service_test)
            if form.is_valid():
                form.save()
                test_list = self.get_test_list(data, self.service_test)
                for test in test_list:
                    self.assertEqual(test['value'], test['expected'])
            else:
                self.assertIn(data['name'], self.failed_expected)

    def test_edit_service_on_disabled_service(self):
        create_operation = self.service_test.operations.filter(type=OperationType.CREATE)[0]
        create_operation.job_template = None
        create_operation.save()
        self.service_test.save()
        data = self.data_list[0]
        form = ServiceForm(data, instance=self.service_test)
        self.assertEqual(True, form.fields['enabled'].disabled)
        self.assertEqual("'CREATE' operation with a job template is required to enable this service.", form.fields['enabled'].help_text)



    @staticmethod
    def get_test_list(data, service):
        return [
            {
                'name': "name",
                'value': service.name,
                'expected': data['name']
            },
            {
                'name': "description",
                'value': service.description,
                'expected': data['description']
            },
        ]