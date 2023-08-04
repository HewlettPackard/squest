import json
from unittest import mock

from django.utils import timezone

from profiles.models import Permission
from service_catalog.models import RequestState, Request, RequestMessage, InstanceState, Instance, SupportMessage, Doc, \
    GlobalHook, Announcement, BootstrapType, CustomLink, ApprovalWorkflow, ApprovalStep
from service_catalog.models.custom_link import LinkButtonClassChoices
from tests.test_service_catalog.base_test_request import BaseTestRequest
from tests.views import TestingGetUIViews, TestingPostUIViews, TestPermissionUIViews


class TestServiceCatalogPermissionsViews(BaseTestRequest, TestPermissionUIViews):

    def test_request_views_crud(self):
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_list',
                perm_str='service_catalog.list_request',
            ),
            TestingGetUIViews(
                url='service_catalog:request_archived_list',
                perm_str='service_catalog.list_request',
            ),
            TestingGetUIViews(
                url='service_catalog:request_details',
                perm_str='service_catalog.view_request',
                url_kwargs={'pk': self.test_request.id}
            ),
            TestingGetUIViews(
                url='service_catalog:request_edit',
                perm_str='service_catalog.change_request',
                url_kwargs={'pk': self.test_request.id}
            ),
            TestingPostUIViews(
                url='service_catalog:request_edit',
                perm_str='service_catalog.change_request',
                url_kwargs={'pk': self.test_request.id},
                data={
                    "fill_in_survey": "{}",
                    "instance": self.test_instance.id,
                    "operation": self.create_operation_test.id,
                    "user": self.standard_user.id,
                    "date_complete": "",
                    "date_archived": "",
                    "tower_job_id": "",
                    "state": "FAILED",
                    "periodic_task": "",
                    "periodic_task_date_expire": "",
                    "failure_message": ""
                }
            ),
            TestingGetUIViews(
                url='service_catalog:request_delete',
                perm_str='service_catalog.delete_request',
                url_kwargs={'pk': self.test_request.id}
            ),
            TestingPostUIViews(
                url='service_catalog:request_delete',
                perm_str='service_catalog.delete_request',
                url_kwargs={'pk': self.test_request.id},

            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_views_cancel(self):
        self.test_request.state = RequestState.SUBMITTED
        self.test_request.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_cancel',
                perm_str='service_catalog.cancel_request',
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostUIViews(
                url='service_catalog:request_cancel',
                perm_str='service_catalog.cancel_request',
                url_kwargs={'pk': self.test_request.id},
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_views_need_info(self):
        self.test_request.state = RequestState.SUBMITTED
        self.test_request.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_need_info',
                perm_str='service_catalog.need_info_request',
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostUIViews(
                url='service_catalog:request_need_info',
                perm_str='service_catalog.need_info_request',
                url_kwargs={'pk': self.test_request.id},
                data={
                    'content': 'My comment'
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_views_re_submit(self):
        self.test_request.state = RequestState.NEED_INFO
        self.test_request.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_re_submit',
                perm_str='service_catalog.re_submit_request',
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostUIViews(
                url='service_catalog:request_re_submit',
                perm_str='service_catalog.re_submit_request',
                url_kwargs={'pk': self.test_request.id},
                data={
                    'content': 'My comment'
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_views_reject(self):
        self.test_request.state = RequestState.SUBMITTED
        self.test_request.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_reject',
                perm_str='service_catalog.reject_request',
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostUIViews(
                url='service_catalog:request_reject',
                perm_str='service_catalog.reject_request',
                url_kwargs={'pk': self.test_request.id},
                data={
                    'content': 'My comment'
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_views_accept(self):
        self.test_request.state = RequestState.SUBMITTED
        self.test_request.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_accept',
                perm_str='service_catalog.accept_request',
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostUIViews(
                url='service_catalog:request_accept',
                perm_str='service_catalog.accept_request',
                url_kwargs={'pk': self.test_request.id},
                data={
                    'text_variable': 'my_var',
                    'multiplechoice_variable': 'choice1',
                    'multiselect_var': 'multiselect_1',
                    'textarea_var': '2',
                    'password_var': 'password1234',
                    'integer_var': '1',
                    'float_var': '0.6'
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_views_process(self):
        self.test_request.state = RequestState.ACCEPTED
        self.test_request.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_process',
                perm_str='service_catalog.process_request',
                url_kwargs={'pk': self.test_request.id},
            ),
            TestingPostUIViews(
                url='service_catalog:request_process',
                perm_str='service_catalog.process_request',
                url_kwargs={'pk': self.test_request.id},
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_views_archive(self):
        self.test_request.state = RequestState.COMPLETE
        self.test_request.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_archive',
                perm_str='service_catalog.archive_request',
                url_kwargs={'pk': self.test_request.id},
                expected_status_code=302
            ),
            TestingPostUIViews(
                url='service_catalog:request_archive',
                perm_str='service_catalog.archive_request',
                url_kwargs={'pk': self.test_request.id},
                expected_not_allowed_status_code=405,
                expected_status_code=405
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_views_unarchive(self):
        self.test_request.state = RequestState.ARCHIVED
        self.test_request.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_unarchive',
                perm_str='service_catalog.unarchive_request',
                url_kwargs={'pk': self.test_request.id},
                expected_status_code=302
            ),
            TestingPostUIViews(
                url='service_catalog:request_unarchive',
                perm_str='service_catalog.unarchive_request',
                url_kwargs={'pk': self.test_request.id},
                expected_not_allowed_status_code=405,
                expected_status_code=405
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_views_bulk_delete(self):
        self.test_request.state = RequestState.ARCHIVED
        self.test_request.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_bulk_delete',
                perm_str='service_catalog.delete_request',
                data={
                    'selection': [request.id for request in Request.objects.all()]

                }
            ),
            TestingPostUIViews(
                url='service_catalog:request_bulk_delete',
                perm_str='service_catalog.delete_request',
                data={
                    'selection': [request.id for request in Request.objects.all()]

                }
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_requestmessage_views(self):
        self.request_message = RequestMessage.objects.create(
            sender=self.testing_user,
            request=self.test_request,
            content="Existing message"
        )
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:requestmessage_create',
                perm_str='service_catalog.add_requestmessage',
                url_kwargs={'request_id': self.test_request.id}
            ),
            TestingPostUIViews(
                url='service_catalog:requestmessage_create',
                perm_str='service_catalog.add_requestmessage',
                url_kwargs={'request_id': self.test_request.id},
                data={
                    'content': 'new message'
                }
            ),
            TestingGetUIViews(
                url='service_catalog:requestmessage_edit',
                perm_str='service_catalog.change_requestmessage',
                url_kwargs={'request_id': self.test_request.id, 'pk': self.request_message.id}
            ),
            TestingPostUIViews(
                url='service_catalog:requestmessage_edit',
                perm_str='service_catalog.change_requestmessage',
                url_kwargs={'request_id': self.test_request.id, 'pk': self.request_message.id},
                data={
                    'content': 'message updated'
                }
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_portfolio_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:portfolio_list',
                perm_str='service_catalog.list_portfolio',
            ),
            TestingGetUIViews(
                url='service_catalog:portfolio_create',
                perm_str='service_catalog.add_portfolio',
            ),
            TestingPostUIViews(
                url='service_catalog:portfolio_create',
                perm_str='service_catalog.add_portfolio',
                data={
                    'name': 'New name'
                }
            ),
            TestingGetUIViews(
                url='service_catalog:portfolio_edit',
                perm_str='service_catalog.change_portfolio',
                url_kwargs={'pk': self.portfolio_test_1.id}
            ),
            TestingPostUIViews(
                url='service_catalog:portfolio_edit',
                perm_str='service_catalog.change_portfolio',
                url_kwargs={'pk': self.portfolio_test_1.id},
                data={
                    'name': 'name updated'
                }
            ),
            TestingGetUIViews(
                url='service_catalog:portfolio_delete',
                perm_str='service_catalog.delete_portfolio',
                url_kwargs={'pk': self.portfolio_test_1.id}
            ),
            TestingPostUIViews(
                url='service_catalog:portfolio_delete',
                perm_str='service_catalog.delete_portfolio',
                url_kwargs={'pk': self.portfolio_test_1.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_service_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:service_list',
                perm_str='service_catalog.list_service',
            ),
            TestingGetUIViews(
                url='service_catalog:service_create',
                perm_str='service_catalog.add_service',
            ),
            TestingPostUIViews(
                url='service_catalog:service_create',
                perm_str='service_catalog.add_service',
                data={
                    'name': 'New service',
                    'description': 'A new service',
                }
            ),
            TestingGetUIViews(
                url='service_catalog:service_edit',
                perm_str='service_catalog.change_service',
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:service_edit',
                perm_str='service_catalog.change_service',
                url_kwargs={'pk': self.service_test.id},
                data={
                    'name': 'Service updated',
                    'description': 'Description of service test updated',
                }
            ),
            TestingGetUIViews(
                url='service_catalog:service_delete',
                perm_str='service_catalog.delete_service',
                url_kwargs={'pk': self.service_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:service_delete',
                perm_str='service_catalog.delete_service',
                url_kwargs={'pk': self.service_test.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_operation_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:operation_list',
                perm_str='service_catalog.list_operation',
                url_kwargs={'service_id': self.service_test.id}
            ),
            TestingGetUIViews(
                url='service_catalog:create_operation_list',
                perm_str='service_catalog.list_operation',
                url_kwargs={'service_id': self.service_test.id}
            ),
            TestingGetUIViews(
                url='service_catalog:operation_create',
                perm_str='service_catalog.add_operation',
                url_kwargs={'service_id': self.service_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:operation_create',
                perm_str='service_catalog.add_operation',
                url_kwargs={'service_id': self.service_test.id},
                data={
                    'name': 'New operation',
                    'description': 'a new operation',
                    'job_template': self.job_template_test.id,
                    'type': 'CREATE',
                    'process_timeout_second': 60
                }
            ),
            TestingGetUIViews(
                url='service_catalog:operation_details',
                perm_str='service_catalog.view_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id}
            ),
            TestingGetUIViews(
                url='service_catalog:operation_edit',
                perm_str='service_catalog.change_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:operation_edit',
                perm_str='service_catalog.change_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id},
                data={
                    'name': 'Operation updated',
                    'description': 'Updated operation description',
                    'job_template': self.job_template_test.id,
                    'type': 'DELETE',
                    'process_timeout_second': 120
                }
            ),
            TestingGetUIViews(
                url='service_catalog:operation_edit_survey',
                perm_str='service_catalog.change_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.update_operation_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:operation_edit_survey',
                perm_str='service_catalog.change_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.update_operation_test.id},
                data={
                    'form-0-id': self.update_operation_test.tower_survey_fields.get(name='text_variable').id,
                    'form-0-default': 'default_var',
                    'form-1-id': self.update_operation_test.tower_survey_fields.get(name='multiplechoice_variable').id,
                    'form-1-is_customer_field': 'on',
                    'form-1-default': 'default_var',
                    'form-TOTAL_FORMS': 2,
                    'form-INITIAL_FORMS': 2
                }
            ),
            TestingGetUIViews(
                url='service_catalog:operation_delete',
                perm_str='service_catalog.delete_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:operation_delete',
                perm_str='service_catalog.delete_operation',
                url_kwargs={'service_id': self.service_test.id, 'pk': self.create_operation_test.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_request_service_views(self):
        self.empty_role.permissions.add(
            Permission.objects.get(content_type__app_label='profiles', codename='consume_quota_scope'))
        self.create_operation_test_2.is_admin_operation = True
        self.create_operation_test_2.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:request_service',
                perm_str='service_catalog.request_on_service',
                url_kwargs={'service_id': self.service_test.id, 'operation_id': self.create_operation_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:request_service',
                perm_str='service_catalog.request_on_service',
                url_kwargs={'service_id': self.service_test.id, 'operation_id': self.create_operation_test.id},
                data={
                    "0-name": "instance_1",
                    "0-quota_scope": self.test_quota_scope.id,
                    "service_request_wizard_view-current_step": "0",
                },
                expected_status_code=200
            ),
            TestingPostUIViews(
                url='service_catalog:request_service',
                perm_str='service_catalog.request_on_service',
                url_kwargs={'service_id': self.service_test.id, 'operation_id': self.create_operation_test.id},
                data={
                    "1-text_variable": "text_value_1",
                    "1-multiplechoice_variable": "text_value_2",
                    "service_request_wizard_view-current_step": "1",
                },
            ),
            TestingGetUIViews(
                url='service_catalog:request_service',
                perm_str='service_catalog.admin_request_on_service',
                url_kwargs={'service_id': self.service_test_2.id, 'operation_id': self.create_operation_test_2.id}
            ),
            TestingPostUIViews(
                url='service_catalog:request_service',
                perm_str='service_catalog.admin_request_on_service',
                url_kwargs={'service_id': self.service_test_2.id, 'operation_id': self.create_operation_test_2.id},
                data={
                    "0-name": "instance_1",
                    "0-quota_scope": self.test_quota_scope.id,
                    "service_request_wizard_view-current_step": "0",
                },
                expected_status_code=200
            ),
            TestingPostUIViews(
                url='service_catalog:request_service',
                perm_str='service_catalog.admin_request_on_service',
                url_kwargs={'service_id': self.service_test_2.id, 'operation_id': self.create_operation_test_2.id},
                data={
                    "1-text_variable": "text_value_1",
                    "1-multiplechoice_variable": "text_value_2",
                    "service_request_wizard_view-current_step": "1",
                },
            ),
        ]
        self.run_permissions_tests(testing_view_list)

    def test_instance_views(self):
        self.test_instance.state = InstanceState.AVAILABLE
        self.test_instance_2.state = InstanceState.AVAILABLE
        self.test_instance_2.service = self.update_operation_test_2.service
        self.test_instance.save()
        self.test_instance_2.save()

        self.update_operation_test_2.is_admin_operation = True
        self.update_operation_test_2.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:instance_list',
                perm_str='service_catalog.list_instance',
            ),
            TestingGetUIViews(
                url='service_catalog:instance_details',
                perm_str='service_catalog.view_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingGetUIViews(
                url='service_catalog:instance_request_new_operation',
                perm_str='service_catalog.request_on_instance',
                url_kwargs={'instance_id': self.test_instance.id, 'operation_id': self.update_operation_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:instance_request_new_operation',
                perm_str='service_catalog.request_on_instance',
                url_kwargs={'instance_id': self.test_instance.id, 'operation_id': self.update_operation_test.id},
                data={
                    'text_variable': 'test'
                }
            ),
            TestingGetUIViews(
                url='service_catalog:instance_request_new_operation',
                perm_str='service_catalog.admin_request_on_instance',
                url_kwargs={'instance_id': self.test_instance_2.id, 'operation_id': self.update_operation_test_2.id}
            ),
            TestingPostUIViews(
                url='service_catalog:instance_request_new_operation',
                perm_str='service_catalog.admin_request_on_instance',
                url_kwargs={'instance_id': self.test_instance_2.id, 'operation_id': self.update_operation_test_2.id},
                data={
                    'text_variable': 'test'
                }
            ),
            TestingGetUIViews(
                url='service_catalog:instance_edit',
                perm_str='service_catalog.change_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPostUIViews(
                url='service_catalog:instance_edit',
                perm_str='service_catalog.change_instance',
                url_kwargs={'pk': self.test_instance.id},
                data={
                    'name': 'new_instance_name',
                    'service': self.service_test_2.id,
                    'requester': self.standard_user_2.id,
                    'state': InstanceState.PROVISIONING,
                    'quota_scope': self.test_quota_scope.id,
                    'spec': json.dumps({"key1": "val1", "key2": "val2"}),
                    'user_spec': json.dumps({"key1": "val1", "key2": "val2"}),
                }
            ),
            TestingGetUIViews(
                url='service_catalog:instance_delete',
                perm_str='service_catalog.delete_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPostUIViews(
                url='service_catalog:instance_delete',
                perm_str='service_catalog.delete_instance',
                url_kwargs={'pk': self.test_instance.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_instance_views_bulk_delete(self):
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:instance_bulk_delete',
                perm_str='service_catalog.delete_instance',
                data={
                    'selection': [instance.id for instance in Instance.objects.all()]

                }),
            TestingPostUIViews(
                url='service_catalog:instance_bulk_delete',
                perm_str='service_catalog.delete_instance',
                data={
                    'selection': [instance.id for instance in Instance.objects.all()]

                }
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_instance_views_state_machine(self):
        self.test_instance.state = InstanceState.DELETED
        self.test_instance.save()
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:instance_archive',
                perm_str='service_catalog.archive_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPostUIViews(
                url='service_catalog:instance_archive',
                perm_str='service_catalog.archive_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingGetUIViews(
                url='service_catalog:instance_unarchive',
                perm_str='service_catalog.unarchive_instance',
                url_kwargs={'pk': self.test_instance.id}
            ),
            TestingPostUIViews(
                url='service_catalog:instance_unarchive',
                perm_str='service_catalog.unarchive_instance',
                url_kwargs={'pk': self.test_instance.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_support_views(self):
        test_message = SupportMessage.objects.create(
            support=self.support_test,
            content='test',
            sender=self.testing_user
        )
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:support_list',
                perm_str='service_catalog.list_support',
            ),
            TestingGetUIViews(
                url='service_catalog:support_create',
                perm_str='service_catalog.add_support',
                url_kwargs={'instance_id': self.support_test.instance.id}
            ),
            TestingPostUIViews(
                url='service_catalog:support_create',
                perm_str='service_catalog.add_support',
                data={
                    'title': 'New support',
                    'content': 'message'
                },
                url_kwargs={'instance_id': self.support_test.instance.id}
            ),
            TestingGetUIViews(
                url='service_catalog:support_details',
                perm_str='service_catalog.view_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
            ),
            TestingPostUIViews(
                url='service_catalog:support_details',
                perm_str='service_catalog.add_supportmessage',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                data={
                    'content': 'message'
                }
            ),
            TestingGetUIViews(
                url='service_catalog:supportmessage_edit',
                perm_str='service_catalog.change_supportmessage',
                url_kwargs={'instance_id': self.support_test.instance.id, 'support_id': self.support_test.id,
                            'pk': test_message.id},
            ),
            TestingPostUIViews(
                url='service_catalog:supportmessage_edit',
                perm_str='service_catalog.change_supportmessage',
                url_kwargs={'instance_id': self.support_test.instance.id, 'support_id': self.support_test.id,
                            'pk': test_message.id},
                data={
                    'content': 'message'
                }
            ),
            TestingGetUIViews(
                url='service_catalog:support_close',
                perm_str='service_catalog.close_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                expected_status_code=302
            ),
            TestingPostUIViews(
                url='service_catalog:support_close',
                perm_str='service_catalog.close_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingGetUIViews(
                url='service_catalog:support_reopen',
                perm_str='service_catalog.reopen_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                expected_status_code=302
            ),
            TestingPostUIViews(
                url='service_catalog:support_reopen',
                perm_str='service_catalog.reopen_support',
                url_kwargs={'instance_id': self.support_test.instance.id, 'pk': self.support_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_doc_views(self):
        doc = Doc.objects.create(title="test_doc", content="# tittle 1")
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:doc_list',
                perm_str='service_catalog.list_doc',
            ),
            TestingGetUIViews(
                url='service_catalog:doc_details',
                perm_str='service_catalog.view_doc',
                url_kwargs={'pk': doc.id}
            ),

        ]
        self.run_permissions_tests(testing_view_list)

    def test_towerserver_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:towerserver_list',
                perm_str='service_catalog.list_towerserver',
            ),
            TestingGetUIViews(
                url='service_catalog:towerserver_create',
                perm_str='service_catalog.add_towerserver',
            ),
            TestingPostUIViews(
                url='service_catalog:towerserver_create',
                perm_str='service_catalog.add_towerserver',
                data={
                    "name": "New tower",
                    "host": "tower.domain.local",
                    "token": "xxxx",
                    "extra_vars": "{}"
                }
            ),
            TestingGetUIViews(
                url='service_catalog:towerserver_details',
                perm_str='service_catalog.view_towerserver',
                url_kwargs={'pk': self.tower_server_test.id}
            ),
            TestingGetUIViews(
                url='service_catalog:towerserver_edit',
                perm_str='service_catalog.change_towerserver',
                url_kwargs={'pk': self.tower_server_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:towerserver_edit',
                perm_str='service_catalog.change_towerserver',
                url_kwargs={'pk': self.tower_server_test.id},
                data={
                    "name": "Tower server updated",
                    "host": "https://tower-updated.domain.local",
                    "token": "xxxx-updated"
                }
            ),
            TestingGetUIViews(
                url='service_catalog:towerserver_sync',
                perm_str='service_catalog.sync_towerserver',
                url_kwargs={'tower_id': self.tower_server_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingPostUIViews(
                url='service_catalog:towerserver_sync',
                perm_str='service_catalog.sync_towerserver',
                url_kwargs={'tower_id': self.tower_server_test.id},
                expected_status_code=202,
            ),
            TestingGetUIViews(
                url='service_catalog:jobtemplate_sync',
                perm_str='service_catalog.sync_towerserver',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id},
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingPostUIViews(
                url='service_catalog:jobtemplate_sync',
                perm_str='service_catalog.sync_towerserver',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id},
                expected_status_code=202,
            ),
            TestingGetUIViews(
                url='service_catalog:towerserver_delete',
                perm_str='service_catalog.delete_towerserver',
                url_kwargs={'pk': self.tower_server_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:towerserver_delete',
                perm_str='service_catalog.delete_towerserver',
                url_kwargs={'pk': self.tower_server_test.id}
            )
        ]
        with mock.patch("towerlib.towerlib.Tower.__init__") as mock_tower_lib:
            with mock.patch("service_catalog.models.tower_server.TowerServer.sync") as mock_tower_sync:
                mock_tower_lib.return_value = None
                self.run_permissions_tests(testing_view_list)

    def test_jobtemplate_views(self):
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:jobtemplate_list',
                perm_str='service_catalog.list_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id},
            ),
            TestingGetUIViews(
                url='service_catalog:jobtemplate_details',
                perm_str='service_catalog.view_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id}
            ),
            TestingGetUIViews(
                url='service_catalog:job_template_compliancy',
                perm_str='service_catalog.view_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id}
            ),
            TestingGetUIViews(
                url='service_catalog:jobtemplate_delete',
                perm_str='service_catalog.delete_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id}
            ),
            TestingPostUIViews(
                url='service_catalog:jobtemplate_delete',
                perm_str='service_catalog.delete_jobtemplate',
                url_kwargs={'tower_id': self.tower_server_test.id, 'pk': self.job_template_test.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_globalhook_views(self):
        global_hook = GlobalHook.objects.create(
            name="hook1",
            model="Instance",
            state="PROVISIONING",
            job_template=self.job_template_test
        )
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:globalhook_list',
                perm_str='service_catalog.list_globalhook',
            ),
            TestingGetUIViews(
                url='service_catalog:globalhook_create',
                perm_str='service_catalog.add_globalhook',
            ),
            TestingPostUIViews(
                url='service_catalog:globalhook_create',
                perm_str='service_catalog.add_globalhook',
                data={
                    "name": "New hook",
                    "model": "Instance",
                    "state": "PROVISIONING",
                    "job_template": self.job_template_test.id,
                    "extra_vars": "{}"
                }
            ),
            TestingGetUIViews(
                url='service_catalog:globalhook_edit',
                perm_str='service_catalog.change_globalhook',
                url_kwargs={'pk': global_hook.id}
            ),
            TestingPostUIViews(
                url='service_catalog:globalhook_edit',
                perm_str='service_catalog.change_globalhook',
                url_kwargs={'pk': global_hook.id},
                data={
                    "name": "Hook updated",
                    "model": "Instance",
                    "state": "PENDING",
                    "job_template": self.job_template_test.id,
                    "extra_vars": {}
                }
            ),
            TestingPostUIViews(
                url='service_catalog:ajax_load_model_state',
                perm_str='service_catalog.add_globalhook',
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingGetUIViews(
                url='service_catalog:ajax_load_model_state',
                perm_str='service_catalog.add_globalhook',
                data={
                    "model": 'Instance'
                }
            ),
            TestingGetUIViews(
                url='service_catalog:ajax_load_model_state',
                perm_str='service_catalog.change_globalhook',
                data={
                    "model": 'Instance'
                }
            ),
            TestingPostUIViews(
                url='service_catalog:ajax_load_service_operations',
                perm_str='service_catalog.change_globalhook',
                expected_status_code=405,
                expected_not_allowed_status_code=405
            ),
            TestingGetUIViews(
                url='service_catalog:ajax_load_service_operations',
                perm_str='service_catalog.add_globalhook',
                data={
                    'service': self.service_test.id
                }
            ),
            TestingGetUIViews(
                url='service_catalog:ajax_load_service_operations',
                perm_str='service_catalog.change_globalhook',
                data={
                    'service': self.service_test.id
                }
            ),
            TestingGetUIViews(
                url='service_catalog:globalhook_delete',
                perm_str='service_catalog.delete_globalhook',
                url_kwargs={'pk': global_hook.id}
            ),
            TestingPostUIViews(
                url='service_catalog:globalhook_delete',
                perm_str='service_catalog.delete_globalhook',
                url_kwargs={'pk': global_hook.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_announcement_views(self):
        announcement = Announcement.objects.create(
            title='My announcement title',
            message='My announcement message',
            date_start=timezone.now() - timezone.timedelta(days=1),
            date_stop=timezone.now() + timezone.timedelta(days=1),
            created_by=self.testing_user,
            type=BootstrapType.INFO
        )
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:announcement_list',
                perm_str='service_catalog.list_announcement',
            ),
            TestingGetUIViews(
                url='service_catalog:announcement_create',
                perm_str='service_catalog.add_announcement',
            ),
            TestingPostUIViews(
                url='service_catalog:announcement_create',
                perm_str='service_catalog.add_announcement',
                data={
                    'title': 'My announcement title info',
                    'message': 'My announcement message info',
                    'date_start': timezone.now(),
                    'date_stop': timezone.now() + timezone.timedelta(days=2),
                    'type': BootstrapType.INFO
                }
            ),
            TestingGetUIViews(
                url='service_catalog:announcement_edit',
                perm_str='service_catalog.change_announcement',
                url_kwargs={'pk': announcement.id}
            ),
            TestingPostUIViews(
                url='service_catalog:announcement_edit',
                perm_str='service_catalog.change_announcement',
                url_kwargs={'pk': announcement.id},
                data={
                    'title': 'My announcement title danger',
                    'message': 'My announcement message danger',
                    'date_start': timezone.now(),
                    'date_stop': timezone.now() + timezone.timedelta(days=7),
                    'type': BootstrapType.DANGER
                }
            ),
            TestingGetUIViews(
                url='service_catalog:announcement_delete',
                perm_str='service_catalog.delete_announcement',
                url_kwargs={'pk': announcement.id}
            ),
            TestingPostUIViews(
                url='service_catalog:announcement_delete',
                perm_str='service_catalog.delete_announcement',
                url_kwargs={'pk': announcement.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_customlink_views(self):
        custom_link = CustomLink.objects.create(
            name="test_custom_link",
            text="custom_link",
            url="https://custom-link.domain"
        )
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:customlink_list',
                perm_str='service_catalog.list_customlink',
            ),
            TestingGetUIViews(
                url='service_catalog:customlink_create',
                perm_str='service_catalog.add_customlink',
            ),
            TestingPostUIViews(
                url='service_catalog:customlink_create',
                perm_str='service_catalog.add_customlink',
                data={
                    "name": "custom_link_1",
                    "text": "custom_link__text_1",
                    "url": "http://example.domain",
                    "button_class": LinkButtonClassChoices.DEFAULT
                }
            ),
            TestingGetUIViews(
                url='service_catalog:customlink_edit',
                perm_str='service_catalog.change_customlink',
                url_kwargs={'pk': custom_link.id}
            ),
            TestingPostUIViews(
                url='service_catalog:customlink_edit',
                perm_str='service_catalog.change_customlink',
                url_kwargs={'pk': custom_link.id},
                data={
                    "name": "updated_name",
                    "text": "updated_text",
                    "url": "http://updated.domain",
                    "button_class": LinkButtonClassChoices.BLUE
                }
            ),
            TestingGetUIViews(
                url='service_catalog:customlink_delete',
                perm_str='service_catalog.delete_customlink',
                url_kwargs={'pk': custom_link.id}
            ),
            TestingPostUIViews(
                url='service_catalog:customlink_delete',
                perm_str='service_catalog.delete_customlink',
                url_kwargs={'pk': custom_link.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_approvalworkflow_views(self):
        approval_workflow = ApprovalWorkflow.objects.create(
            name="test_approval_workflow",
            operation=self.create_operation_test
        )
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:approvalworkflow_list',
                perm_str='service_catalog.list_approvalworkflow',
            ),
            TestingGetUIViews(
                url='service_catalog:approvalworkflow_details',
                perm_str='service_catalog.view_approvalworkflow',
                url_kwargs={'pk': approval_workflow.id}
            ),
            TestingGetUIViews(
                url='service_catalog:approvalworkflow_create',
                perm_str='service_catalog.add_approvalworkflow',
            ),
            TestingPostUIViews(
                url='service_catalog:approvalworkflow_create',
                perm_str='service_catalog.add_approvalworkflow',
                data={
                    'name': 'New approvalworkflow',
                    'operation': self.update_operation_test.id,
                    'scope': self.test_quota_scope.id,
                }
            ),
            TestingGetUIViews(
                url='service_catalog:approvalworkflow_edit',
                perm_str='service_catalog.change_approvalworkflow',
                url_kwargs={'pk': approval_workflow.id}
            ),
            TestingPostUIViews(
                url='service_catalog:approvalworkflow_edit',
                perm_str='service_catalog.change_approvalworkflow',
                url_kwargs={'pk': approval_workflow.id},
                data={
                    'name': 'Approvalworkflow updated',
                    'operation': self.create_operation_test.id,
                    'scope': self.test_quota_scope.id,
                }
            ),
            TestingGetUIViews(
                url='service_catalog:approvalworkflow_delete',
                perm_str='service_catalog.delete_approvalworkflow',
                url_kwargs={'pk': approval_workflow.id}
            ),
            TestingPostUIViews(
                url='service_catalog:approvalworkflow_delete',
                perm_str='service_catalog.delete_approvalworkflow',
                url_kwargs={'pk': approval_workflow.id}
            )
        ]
        self.run_permissions_tests(testing_view_list)

    def test_approvalstep_views(self):
        approval_workflow = ApprovalWorkflow.objects.create(
            name="test_approval_workflow",
            operation=self.create_operation_test
        )
        approval_step = ApprovalStep.objects.create(
            name="test_approval_step_1",
            approval_workflow=approval_workflow
        )
        approval_step_2 = ApprovalStep.objects.create(
            name="test_approval_step_2",
            approval_workflow=approval_workflow
        )
        testing_view_list = [
            TestingGetUIViews(
                url='service_catalog:approvalstep_create',
                perm_str='service_catalog.add_approvalstep',
                url_kwargs={'approval_workflow_id': approval_workflow.id},
            ),
            TestingPostUIViews(
                url='service_catalog:approvalstep_create',
                perm_str='service_catalog.add_approvalstep',
                url_kwargs={'approval_workflow_id': approval_workflow.id},
                data={
                    'name': 'New approval step',
                    'permission': Permission.objects.filter(content_type__model='approvalstep').first().id,
                    'readable_fields': [],
                    'editable_fields': [],
                    'approval_workflow': approval_workflow.id
                }
            ),
            TestingGetUIViews(
                url='service_catalog:approvalstep_edit',
                perm_str='service_catalog.change_approvalstep',
                url_kwargs={'approval_workflow_id': approval_workflow.id, 'pk': approval_step.id}
            ),
            TestingPostUIViews(
                url='service_catalog:approvalstep_edit',
                perm_str='service_catalog.change_approvalstep',
                url_kwargs={'approval_workflow_id': approval_workflow.id, 'pk': approval_step.id},
                data={
                    'name': 'Approval step update',
                    'permission': Permission.objects.filter(content_type__model='approvalstep').first().id,
                    'readable_fields': [],
                    'editable_fields': [],
                    'approval_workflow': approval_workflow.id
                }
            ),
            TestingGetUIViews(
                url='service_catalog:ajax_approval_step_position_update',
                perm_str='service_catalog.change_approvalstep',
                expected_status_code=405,
                expected_not_allowed_status_code=405,
            ),
            TestingPostUIViews(
                url='service_catalog:ajax_approval_step_position_update',
                perm_str='service_catalog.change_approvalstep',
                data={
                    'listStepToUpdate': json.dumps([
                        {
                            "position": approval_step_2.position,
                            "id": approval_step.id
                        }, {
                            "position": approval_step.position,
                            "id": approval_step_2.id
                        }
                    ])
                },
                expected_status_code=202
            ),

            TestingGetUIViews(
                url='service_catalog:approvalstep_delete',
                perm_str='service_catalog.delete_approvalstep',
                url_kwargs={'approval_workflow_id': approval_workflow.id, 'pk': approval_step.id}
            ),
            TestingPostUIViews(
                url='service_catalog:approvalstep_delete',
                perm_str='service_catalog.delete_approvalstep',
                url_kwargs={'approval_workflow_id': approval_workflow.id, 'pk': approval_step.id}
            ),
        ]
        self.run_permissions_tests(testing_view_list)
