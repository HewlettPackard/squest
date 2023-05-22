from django.urls import reverse

from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TestTransformerViews(BaseTestResourceTrackerV2):

    def setUp(self):
        super(TestTransformerViews, self).setUp()

    def test_delete_transformer(self):
        self.assertTrue(self.server1.resource_attributes.filter(attribute_definition=self.core_attribute).exists())
        self.assertTrue(self.server2.resource_attributes.filter(attribute_definition=self.core_attribute).exists())
        args = {
            'resource_group_id': self.cluster.id,
            'attribute_id': self.core_attribute.id,
        }
        response = self.client.post(reverse('resource_tracker:resource_group_attribute_delete', kwargs=args))
        self.assertEqual(302, response.status_code)
        self.server1.refresh_from_db()
        self.server2.refresh_from_db()
        self.assertFalse(self.server1.resource_attributes.filter(attribute_definition=self.core_attribute).exists())
        self.assertFalse(self.server2.resource_attributes.filter(attribute_definition=self.core_attribute).exists())
