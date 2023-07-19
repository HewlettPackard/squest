from service_catalog.models import CustomLink
from service_catalog.templatetags.custom_links import get_single_button, get_dropdown_button, custom_links
from tests.test_service_catalog.base_test_request import BaseTestRequest


class TestCustomLinks(BaseTestRequest):

    def setUp(self):
        super(TestCustomLinks, self).setUp()
        self.test_instance.spec = {
            "key1": "value1",
            "my_list": [
                "item1",
                "item2"
            ]
        }
        self.test_instance.save()

        self.context_text = {
            "instance": self.test_instance
        }

        self.text = "text"
        self.url = "http://my_url"
        self.test_custom_link = CustomLink.objects.create(name="test", text=self.text, url=self.url)
        self.test_custom_link.services.add(self.service_test)
        self.test_custom_link.save()

    def test_get_single_button_no_jinja(self):
        result = get_single_button(context=self.context_text, custom_link=self.test_custom_link)
        expected = '<a href="http://my_url" class="btn btn-sm btn-default ml-1">text</a>'
        self.assertEqual(result, expected)

    def test_get_single_button_with_jinja(self):
        self.test_custom_link.text = "text-{{ instance.name }}"
        self.test_custom_link.url = "http://my_url/{{ instance.spec.key1 }}"
        self.test_custom_link.save()

        result = get_single_button(context=self.context_text, custom_link=self.test_custom_link)
        expected = '<a href="http://my_url/value1" class="btn btn-sm btn-default ml-1">text-test_instance_1</a>'
        self.assertEqual(result, expected)

    def test_get_single_button_with_invalid_jinja(self):
        self.test_custom_link.url = "http://my_url/{{ instance.non_existing_key[0] }}"
        self.test_custom_link.save()

        result = get_single_button(context=self.context_text, custom_link=self.test_custom_link)
        self.assertTrue("disabled" in result)

    def test_get_dropdown_button(self):
        self.test_custom_link.text = "{{ item }}"
        self.test_custom_link.url = "http://my_url/{{ item }}"
        self.test_custom_link.loop = "{{ instance.spec.my_list }}"
        self.test_custom_link.save()

        result = get_dropdown_button(context=self.context_text, custom_link=self.test_custom_link)
        self.assertIn('<a class="dropdown-item" href="http://my_url/item1">item1</a>', result)
        self.assertIn('<a class="dropdown-item" href="http://my_url/item2">item2</a>', result)

    def test_get_dropdown_button_invalid_jinja(self):
        self.test_custom_link.text = "{{ item }}"
        self.test_custom_link.url = "http://my_url/{{ item }}"
        self.test_custom_link.loop = "{{ instance.spec.non_exist }}"
        self.test_custom_link.save()

        result = get_dropdown_button(context=self.context_text, custom_link=self.test_custom_link)
        self.assertTrue("disabled" in result)

    def test_get_custom_link(self):
        result = custom_links(user=self.superuser, instance=self.test_instance)
        expected = '<a href="http://my_url" class="btn btn-sm btn-default ml-1">text</a>'
        self.assertEqual(result, expected)

    def test_get_custom_link_different_service(self):
        self.test_custom_link.services.set([self.service_test_2])
        self.test_custom_link.save()

        result = custom_links(user=self.superuser, instance=self.test_instance)
        expected = ''
        self.assertEqual(result, expected)

    def test_get_custom_link_disabled(self):
        self.test_custom_link.enabled = False
        self.test_custom_link.save()

        result = custom_links(user=self.superuser, instance=self.test_instance)
        expected = ''
        self.assertEqual(expected, result)

    def test_get_custom_link_admin_only(self):
        self.test_custom_link.is_admin_only = True
        self.test_custom_link.save()

        result = custom_links(user=self.standard_user, instance=self.test_instance)
        expected_as_end_user = ''
        self.assertEqual(result, expected_as_end_user)

        result = custom_links(user=self.superuser, instance=self.test_instance)
        expected_as_admin = '<a href="http://my_url" class="btn btn-sm btn-default ml-1">text</a>'
        self.assertEqual(result, expected_as_admin)

    def test_get_custom_link_when_valid(self):
        self.test_custom_link.when = "instance.spec.key1 == 'value1'"
        self.test_custom_link.save()
        result = custom_links(user=self.superuser, instance=self.test_instance)
        expected = '<a href="http://my_url" class="btn btn-sm btn-default ml-1">text</a>'
        self.assertEqual(result, expected)

    def test_get_custom_link_when_non_valid(self):
        self.test_custom_link.when = "instance.spec.key1 == 'not_the_right_value'"
        self.test_custom_link.save()
        result = custom_links(user=self.superuser, instance=self.test_instance)
        expected = ''
        self.assertEqual(result, expected)
