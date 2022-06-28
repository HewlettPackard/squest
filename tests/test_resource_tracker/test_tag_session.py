from django.urls import reverse

from resource_tracker.models import ResourceGroup, ResourcePool
from tests.test_resource_tracker.base_test_resource_tracker import BaseTestResourceTracker


class TestTagSession(BaseTestResourceTracker):

    def setUp(self):
        super(TestTagSession, self).setUp()
        self.resource_group_list_url = reverse('resource_tracker:resource_group_list')
        self.resource_pool_list_url = reverse('resource_tracker:resource_pool_list')

    def test_get_resource_group_with_one_tag(self):
        # add a tag to a RG
        target_tag = "tag1"
        self.rg_physical_servers.tags.add(target_tag)
        self.rg_physical_servers.save()

        # try to get all resource
        response = self.client.get(self.resource_group_list_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), ResourceGroup.objects.all().count())

        # get the page by giving a tag into the URL (like the button apply filter)
        url = self.resource_group_list_url + f"?tag={target_tag}"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), 1)

        # move to another page
        url = reverse('service_catalog:doc_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # go back to the resource group list without a tag in the URL
        response = self.client.get(self.resource_group_list_url, follow=True)  # follow the redirect
        self.assertEqual(200, response.status_code)
        self.assertIn("tag_redirect", response.request["QUERY_STRING"])
        self.assertIn(target_tag, response.request["QUERY_STRING"])
        self.assertEqual(len(response.context["table"].data.data), 1)

        # remove the tags from the filter
        url = self.resource_group_list_url + "?tag_redirect="
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(len(response.context["table"].data.data), ResourceGroup.objects.all().count())

    def test_get_resource_pool_with_one_tag(self):
        target_tag = "tag2"
        substr = 'card-title'

        # add a tag to a RG
        self.rp_vcenter.tags.add(target_tag)
        self.rp_vcenter.save()

        # try to get all resource
        response = self.client.get(self.resource_pool_list_url)
        self.assertEqual(200, response.status_code)
        number_of_card_title = response.content.decode("utf-8").count(substr)
        # the left filter menu use a card title. We remove it from the counter
        number_of_card_title = number_of_card_title - 1
        self.assertEqual(number_of_card_title, ResourcePool.objects.all().count())
        self.assertEqual(response.context["resource_pools"].qs.count(), ResourcePool.objects.all().count())

        # get the page by giving a tag into the URL (like the button apply filter)
        url = self.resource_pool_list_url + f"?tag={target_tag}"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["resource_pools"].qs.count(),
                         ResourcePool.objects.filter(tags__name__in=[target_tag]).count())

        # move to another page
        url = reverse('service_catalog:doc_list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

        # go back to the resource group list without a tag in the URL
        response = self.client.get(self.resource_pool_list_url, follow=True)  # follow the redirect
        self.assertEqual(200, response.status_code)
        self.assertIn("tag_redirect", response.request["QUERY_STRING"])
        self.assertIn(target_tag, response.request["QUERY_STRING"])
        self.assertEqual(response.context["resource_pools"].qs.count(),
                         ResourcePool.objects.filter(tags__name__in=[target_tag]).count())

        # remove the tags from the filter
        url = self.resource_pool_list_url + "?tag_redirect="
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.context["resource_pools"].qs.count(), ResourcePool.objects.all().count())
