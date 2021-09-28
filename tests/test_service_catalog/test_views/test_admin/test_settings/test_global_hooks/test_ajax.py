from django.urls import reverse

from service_catalog.models import InstanceState, RequestState
from tests.test_service_catalog.base import BaseTest


class GlobalHookAjaxTest(BaseTest):

    def test_ajax_load_model_state(self):
        url = reverse('service_catalog:ajax_load_model_state')
        test_map = [
            {"model": "Instance",
             "expected_option": InstanceState.choices
             },
            {"model": "Request",
             "expected_option": RequestState.choices
             }
        ]

        for test in test_map:
            data = {
                "model": test["model"]
            }
            response = self.client.get(url, data=data)
            self.assertEquals(200, response.status_code)
            self.assertEquals(test["expected_option"], response.context["options"])
