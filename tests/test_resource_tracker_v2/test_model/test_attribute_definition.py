from tests.test_resource_tracker_v2.base_test_resource_tracker_v2 import BaseTestResourceTrackerV2


class TestModelAttributeDefinition(BaseTestResourceTrackerV2):

    def setUp(self) -> None:
        super(TestModelAttributeDefinition, self).setUp()

    def test_delete_attribute_definition(self):
        self._validate_state_before_deletion()
        self.vcpu_attribute.delete()
        self._validate_state_after_deletion()
