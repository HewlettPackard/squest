from rest_framework import status
from rest_framework.reverse import reverse

from resource_tracker_v2.models import Transformer, AttributeDefinition, ResourceGroup
from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2API


class TestTransformerAPIView(BaseTestResourceTrackerV2API):

    def setUp(self):
        super(TestTransformerAPIView, self).setUp()
        self._list_create_url = reverse('api_transformer_list_create',  kwargs={"resource_group_id": self.cluster.id})
        self._details_url = reverse('api_transformer_details', kwargs={"resource_group_id": self.cluster.id,
                                                                       "pk": self.core_transformer.id})

        self.new_rg = ResourceGroup.objects.create(name="new_rg")
        self.new_attribute = AttributeDefinition.objects.create(name="new_attribute")
        self.new_transformer = Transformer.objects.create(resource_group=self.new_rg,
                                                          attribute_definition=self.new_attribute)

    def test_transformer_list(self):
        response = self.client.get(self._list_create_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["count"], self.cluster.transformers.count())
        for transformer in response.json()['results']:
            self.assertTrue("resource_group" in transformer)
            self.assertTrue("attribute_definition" in transformer)
            self.assertTrue("consume_from_resource_group" in transformer)
            self.assertTrue("consume_from_attribute_definition" in transformer)
            self.assertTrue("factor" in transformer)
            self.assertTrue("total_consumed" in transformer)
            self.assertTrue("total_produced" in transformer)
            self.assertTrue("yellow_threshold_percent_consumed" in transformer)
            self.assertTrue("red_threshold_percent_consumed" in transformer)

    def test_transformer_list_filter_by_name(self):
        url = self._list_create_url + f"?attribute_definition={self.core_attribute.id}"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, response.json()["count"])

    def test_transformer_create_no_consumer(self):
        other_attribute = AttributeDefinition.objects.create(name="other_attribute")
        data = {
            "attribute_definition": other_attribute.id,
            "consume_from_resource_group": None,
            "consume_from_attribute_definition": None,
        }
        number_transformer_before = Transformer.objects.all().count()
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(number_transformer_before + 1,
                         Transformer.objects.all().count())
        last_transformer = Transformer.objects.last()
        self.assertEqual(last_transformer.resource_group.id, self.cluster.id)
        self.assertEqual(last_transformer.attribute_definition.id, other_attribute.id)
        self.assertIsNone(last_transformer.consume_from_resource_group)
        self.assertIsNone(last_transformer.consume_from_attribute_definition)

    def test_transformer_create_with_consumer(self):
        data = {
            "attribute_definition": self.new_attribute.id,
            "consume_from_resource_group": self.new_rg.id,
            "consume_from_attribute_definition": self.new_attribute.id,
        }
        number_transformer_before = Transformer.objects.all().count()
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(number_transformer_before + 1,
                         Transformer.objects.all().count())
        last_transformer = Transformer.objects.last()
        self.assertEqual(last_transformer.resource_group.id, self.cluster.id)
        self.assertEqual(last_transformer.attribute_definition.id, self.new_attribute.id)
        self.assertEqual(last_transformer.consume_from_resource_group.id, self.new_rg.id)
        self.assertEqual(last_transformer.consume_from_attribute_definition.id, self.new_attribute.id)
        self.assertEqual(last_transformer.factor, 1)

    def test_transformer_get_details(self):
        response = self.client.get(self._details_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("id" in response.json())
        self.assertTrue("resource_group" in response.json())
        self.assertTrue("attribute_definition" in response.json())
        self.assertTrue("consume_from_resource_group" in response.json())
        self.assertTrue("consume_from_attribute_definition" in response.json())
        self.assertEqual(response.json()["id"], self.core_transformer.id)
        self.assertEqual(response.json()["resource_group"], self.cluster.id)
        self.assertEqual(response.json()["attribute_definition"], self.core_attribute.id)
        self.assertIsNone(response.json()["consume_from_resource_group"])
        self.assertIsNone(response.json()["consume_from_attribute_definition"])

    def test_transformer_update_consumer(self):
        other_rg = ResourceGroup.objects.create(name="other_rg")
        other_attribute = AttributeDefinition.objects.create(name="other_attribute")
        Transformer.objects.create(resource_group=other_rg,
                                   attribute_definition=other_attribute)
        data = {
            "attribute_definition": self.core_attribute.id,
            "consume_from_resource_group": other_rg.id,
            "consume_from_attribute_definition": other_attribute.id,
        }
        response = self.client.put(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.core_transformer.refresh_from_db()
        self.assertEqual(self.core_transformer.consume_from_resource_group, other_rg)
        self.assertEqual(self.core_transformer.consume_from_attribute_definition, other_attribute)
        self.assertEqual(self.core_transformer.factor, 1)

    def test_transformer_update_consumer_to_invalid_attribute(self):
        data = {
            "attribute_definition": self.core_attribute.id,
            "consume_from_resource_group": self.new_rg.id,
            "consume_from_attribute_definition": self.vcpu_attribute.id,
        }
        response = self.client.put(self._details_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_circular_loop(self):
        data = {
            "attribute_definition": self.core_attribute.id,
            "consume_from_resource_group": self.ocp_projects.id,
            "consume_from_attribute_definition": self.request_cpu.id
        }
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_provide_consume_from_rg_without_attribute(self):
        data = {
            "attribute_definition": self.core_attribute.id,
            "consume_from_resource_group": self.new_rg.id,
            "consume_from_attribute_definition": None
        }
        response = self.client.post(self._list_create_url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
