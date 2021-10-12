from django.urls import reverse

from profiles.models import BillingGroup
from tests.test_profile.test_group.test_group_base import TestGroupBase


class TestGroupModel(TestGroupBase):

    def setUp(self):
        super(TestGroupModel, self).setUp()

    def test_create_billing_group(self):
        url = reverse('profiles:billing_group_create')
        test_list = [
            {'data': {'name': 'group_test2'}, 'offset': 1},
            {'data': {'name': 'test_billing_group2'}, 'offset': 1},
            {'data': {'name': ''}, 'offset': 1},
            {'data': {'foo': 'group'}, 'offset': 1},
            ]
        init_group_len = len(BillingGroup.objects.all())
        for test in test_list:
            self.client.post(url, data=test['data'])
            self.assertEquals(len(BillingGroup.objects.all()), init_group_len + test['offset'])

    def test_edit_billing_group(self):
        args_group = {
            'billing_group_id': self.test_billing_group.id
        }
        url = reverse('profiles:billing_group_edit', kwargs=args_group)
        test_list = [
            {'data': {'name': 'a'}, 'expected': 'a'},
            {'data': {'name': ''}, 'expected': 'a'},
            {'data': {'name': self.test_billing_group2.name}, 'expected': 'a'},
            {'data': {'foo': 'group'}, 'expected': 'a'},
            {'data': {'name': 'b'}, 'expected': 'b'},
        ]
        for test in test_list:
            self.client.post(url, data=test['data'])
            self.assertEquals(BillingGroup.objects.get(id=self.test_billing_group.id).name, test['expected'])

    def test_delete_billing_group(self):
        args_group = {
            'billing_group_id': self.test_billing_group.id
        }
        url = reverse('profiles:billing_group_delete', kwargs=args_group)
        self.client.post(url)
        self.assertFalse(BillingGroup.objects.filter(id=self.test_billing_group.id).exists())
        self.client.post(url)
        self.assertFalse(BillingGroup.objects.filter(id=self.test_billing_group.id).exists())

    def test_update_users_in_group(self):
        args_group = {
            'billing_group_id': self.test_billing_group.id
        }
        url = reverse('profiles:user_in_billing_group_update', kwargs=args_group)
        data_list = [
            {'users': [self.my_user.id, self.my_user2.id, self.my_user3.id, self.my_user4.id]},
            {'users': [self.my_user.id]},
            {'users': [self.my_user2.id, self.my_user3.id]},
        ]
        for data in data_list:
            self.client.post(url, data=data)
            self.assertEquals(list(set(data.get('users', []))),
                              list(set([user.id for user in self.test_billing_group.user_set.all()])))

    def test_remove_user_from_billing_group(self):
        test_list = [
            {'args_user': {'user_id': self.my_user.id}, 'offset': 0},
            {'args_user': {'user_id': self.my_user2.id}, 'offset': 1}
            ]
        args_group = {
            'billing_group_id': self.test_billing_group.id
        }
        init_users_len = len(self.test_billing_group.user_set.all())
        for test_data in test_list:
            url = reverse('profiles:user_in_billing_group_remove',
                          kwargs={**args_group, **test_data['args_user']})
            self.client.post(url)
            self.assertEquals(len(self.test_billing_group.user_set.all()), init_users_len - test_data['offset'])
