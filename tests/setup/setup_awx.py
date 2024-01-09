from django.test import TestCase
from django.test.testcases import TransactionTestCase
from rest_framework.test import APITestCase

from service_catalog.models import TowerServer, JobTemplate


class SetupDummyAWXCommon(TransactionTestCase):

    def setUp(self):
        # Setup tower
        self.tower = TowerServer.objects.create(name="Tower", host="localhost", token="dummytoken")
        survey = [
            {
                "max": 1024,
                "min": 0,
                "type": "integer",
                "choices": "",
                "default": 1,
                "required": False,
                "variable": "vcpu",
                "new_question": False,
                "question_name": "vCPU",
                "question_description": ""
            },
            {
                "max": 1024,
                "min": 0,
                "type": "integer",
                "choices": "",
                "default": 1,
                "required": False,
                "variable": "ram",
                "new_question": False,
                "question_name": "RAM",
                "question_description": ""
            }
        ]

        self.job_template_1 = JobTemplate.objects.create(name="Job template 1",
                                                         survey={"spec": survey},
                                                         tower_id=1,
                                                         tower_server=self.tower,
                                                         tower_job_template_data=dict())

        self.job_template_2 = JobTemplate.objects.create(name="Job template 2",
                                                         survey={},
                                                         tower_id=2,
                                                         tower_server=self.tower,
                                                         tower_job_template_data=dict())
        print("SetupDummyAWXCommon finished")


class SetupDummyAWX(TestCase, SetupDummyAWXCommon):
    pass


class SetupDummyAWXAPI(APITestCase, SetupDummyAWXCommon):
    pass
