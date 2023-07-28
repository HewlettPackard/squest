from django.test.testcases import TransactionTestCase
import ast
import logging

logger = logging.getLogger(__name__)


def check_data_in_dict(self, expected_data_list, data_list):
    for expected_data, data in zip(expected_data_list, data_list):
        for key_var, val_var in expected_data.items():
            self.assertIn(key_var, data.keys())
            if (isinstance(val_var, list) or isinstance(val_var, set)) and (
                    isinstance(data[key_var], list) or isinstance(data[key_var], set)):
                logger.info(f"Test for key '{key_var}'")
                self.assertEqual(set(val_var), set(data[key_var]))
            elif isinstance(data[key_var], bytes):
                self.assertEqual(ast.literal_eval(str(val_var)), ast.literal_eval(data[key_var].decode("utf-8")))
            elif isinstance(data[key_var], dict) and isinstance(val_var, str):
                self.assertEqual(ast.literal_eval(val_var), data[key_var])
            else:
                logger.info(f"Test for key '{key_var}'")
                self.assertEqual(val_var, data[key_var])


class TransactionTestUtils(TransactionTestCase):
    def assertQuerysetEqualID(self, qs1, qs2):
        self.assertEqual(qs1.model, qs2.model)
        self.assertListEqual(
            list(qs1.order_by('id').values_list("id", flat=True)),
            list(qs2.order_by('id').values_list("id", flat=True))
        )
