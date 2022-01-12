from django.db.models.signals import post_save


def check_data_in_dict(self, expected_data_list, data_list):
    for expected_data, data in zip(expected_data_list, data_list):
        for key_var, val_var in expected_data.items():
            self.assertIn(key_var, data.keys())
            if isinstance(val_var, list) and isinstance(data[key_var], list):
                self.assertEqual(set(val_var), set(data[key_var]))
            else:
                self.assertEqual(val_var, data[key_var])


def skip_auto_calculation(func):
    def _skip_auto_calculation(self):
        from resource_tracker.models import ResourceAttribute
        from resource_tracker.models.resource_attribute import on_change
        post_save.disconnect(on_change, sender=ResourceAttribute)
        func(self)
        post_save.connect(on_change, sender=ResourceAttribute)

    return _skip_auto_calculation
