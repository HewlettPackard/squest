def check_data_in_dict(self, expected_data_list, data_list):
    for expected_data, data in zip(expected_data_list, data_list):
        for key_var, val_var in expected_data.items():
            self.assertIn(key_var, data.keys())
            if isinstance(val_var, list) and isinstance(data[key_var], list):
                self.assertEqual(set(val_var), set(data[key_var]))
            else:
                self.assertEqual(val_var, data[key_var])
