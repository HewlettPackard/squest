from service_catalog.forms.email_template_form import EmailTemplateSendForm
from service_catalog.models import EmailTemplate, Instance, InstanceState
from tests.test_service_catalog.base import BaseTest


class TestEmailTemplateSendForm(BaseTest):

    def setUp(self):
        super(TestEmailTemplateSendForm, self).setUp()
        self.test_email_template = EmailTemplate.objects.create(name="test_email_template",
                                                                email_title="test email template")
        # TEST with a service
        self.test_instance = Instance.objects.create(name="test_instance_1",
                                                     service=self.service_test,
                                                     requester=self.standard_user,
                                                     quota_scope=self.test_quota_scope)
        self.test_instance_2 = Instance.objects.create(name="test_instance_2",
                                                       service=self.service_test_2,
                                                       requester=self.standard_user_2,
                                                       quota_scope=self.test_quota_scope2)

    def test_init_with_a_service(self):
        self.test_email_template.services.set([self.service_test])
        self.test_email_template.save()
        test_form = EmailTemplateSendForm(email_template=self.test_email_template)
        self.assertIn(self.standard_user.id, test_form.fields['users'].initial)

    def test_init_with_instance_state(self):
        self.test_instance_2.state = InstanceState.AVAILABLE
        self.test_instance_2.save()
        self.test_email_template.instance_states = [InstanceState.AVAILABLE]
        self.test_email_template.save()
        test_form = EmailTemplateSendForm(email_template=self.test_email_template)
        self.assertIn(self.standard_user_2.id, test_form.fields['users'].initial)

    def test_init_with_quota_scope(self):
        self.test_email_template.quota_scopes.set([self.test_quota_scope2])
        self.test_email_template.save()
        test_form = EmailTemplateSendForm(email_template=self.test_email_template)
        self.assertIn(self.standard_user_2.id, test_form.fields['users'].initial)

    def test_init_with_when(self):
        self.test_instance.spec = {
            "location": "grenoble"
        }
        self.test_instance.save()
        self.test_email_template.when = "instance.spec['location'] == 'grenoble'"
        self.test_email_template.save()
        test_form = EmailTemplateSendForm(email_template=self.test_email_template)
        self.assertIn(self.standard_user.id, test_form.fields['users'].initial)
