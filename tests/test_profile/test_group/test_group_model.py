from django.urls import reverse

from tests.test_profile.test_group.test_group_base import TestGroupBase


class TestGroupProcessing(TestGroupBase):

    def setUp(self):
        super(TestGroupProcessing, self).setUp()

    def test_update_users_in_group(self):
        args_group = {
            'group_id': self.my_group.id
        }
        url = reverse('profiles:user_in_group_update', kwargs=args_group)
        data_list = [
            {'users': [self.my_user.id, self.my_user2.id, self.my_user3.id, self.my_user4.id]},
            {'users': [self.my_user.id]},
            {'users': [self.my_user2.id, self.my_user3.id]},
        ]
        for data in data_list:
            self.client.post(url, data=data)
            self.assertEquals(list(set(data.get('users', []))),
                              list(set([user.id for user in self.my_group.user_set.all()])))
