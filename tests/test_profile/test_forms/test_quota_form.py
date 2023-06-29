from profiles.forms.quota_forms import QuotaForm
from profiles.models import Quota
from resource_tracker_v2.models import AttributeDefinition
from tests.test_profile.base_test_profile import BaseTestProfile


class QuotaFormTests(BaseTestProfile):

    def setUp(self):
        super(QuotaFormTests, self).setUp()
        self.parameters = {
            "scope": self.test_org,
        }

    def test_quota_form_create(self):
        number_quota_before = Quota.objects.count()
        data = {
            f"attribute_definition_{self.cpu_attribute.id}": 200,
        }
        form = QuotaForm(data, **self.parameters)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(number_quota_before + 1, Quota.objects.count())

    def test_quota_form_update(self):
        cpu_quota = Quota.objects.create(limit=200, scope=self.test_org, attribute_definition=self.cpu_attribute)
        data = {
            f"attribute_definition_{self.cpu_attribute.id}": 100,
        }
        form = QuotaForm(data, **self.parameters)
        self.assertTrue(form.is_valid())
        form.save()
        cpu_quota.refresh_from_db()
        self.assertEqual(cpu_quota.limit, 100)

    def test_quota_form_create_no_quota_inserted_when_limit_zero(self):
        Quota.objects.create(limit=200, scope=self.test_org, attribute_definition=self.cpu_attribute)
        number_quota_before = Quota.objects.count()
        other_attribute = AttributeDefinition.objects.create(name="other_attribute")
        # update cpu quota but leave the other attribute limit to 0
        data = {
            f"attribute_definition_{self.cpu_attribute.id}": 100,
            f"attribute_definition_{other_attribute.id}": 0,
        }
        form = QuotaForm(data, **self.parameters)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(number_quota_before, Quota.objects.count())

    def test_quota_form_initial_values(self):
        Quota.objects.create(limit=200, scope=self.test_org, attribute_definition=self.cpu_attribute)
        form = QuotaForm(**self.parameters)
        self.assertEqual(form.fields[f"attribute_definition_{self.cpu_attribute.id}"].initial, 200)

    def test_quota_form_initial_and_max_values_when_team_scope(self):
        Quota.objects.create(limit=200, scope=self.test_org, attribute_definition=self.cpu_attribute)
        Quota.objects.create(limit=150, scope=self.team1, attribute_definition=self.cpu_attribute)
        parameters = {
            "scope": self.team1
        }
        form = QuotaForm(**parameters)
        self.assertEqual(form.fields[f"attribute_definition_{self.cpu_attribute.id}"].initial, 150)
        self.assertEqual(form.fields[f"attribute_definition_{self.cpu_attribute.id}"].max_value, 50)
