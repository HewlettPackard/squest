from django.contrib.auth.models import User

from profiles.models import Scope
from service_catalog.forms import SurveyValidator
from service_catalog.models import Operation, Instance


class Validator1(SurveyValidator):
    def validate_survey(self):
        if self.survey.get('ram') == 0 and self.survey.get('vcpu') == 0:
            self.fail("ram and vCPU are both equal to 0")
        if self.survey.get('vcpu') == 0:
            self.fail("vCPU is equal to 0", "vcpu")


class Validator2(SurveyValidator):
    def validate_survey(self):
        print("everything is good")


class ValidatorDay1(SurveyValidator):
    def validate_survey(self):
        assert self.survey.get("ram") == 1
        assert self.survey.get("vcpu") == 1
        assert self.survey["request_comment"] == "comment day1"
        assert self.user == User.objects.get(username="superuser")
        assert self.operation == Operation.objects.get(name="Operation 1 (Create)")
        assert self.instance.quota_scope == Scope.objects.get(name="Organization 1")
        assert self.instance.name == "instance test"
        assert self.instance.id == None
        self.fail("Everything is good, it's just a message to be sure that code was executed")


class ValidatorDay2(SurveyValidator):
    def validate_survey(self):
        assert self.survey.get("ram") == 1
        assert self.survey.get("vcpu") == 1
        assert self.survey["request_comment"] == "comment day2"
        assert self.user == User.objects.get(username="superuser")
        assert self.operation == Operation.objects.get(name="Operation 3 (Update)")
        assert self.instance.quota_scope == Scope.objects.get(name="Organization 1")
        assert self.instance.name == "Instance 1 - Org 1"
        assert self.instance.id != None
        assert self.instance == Instance.objects.get(name="Instance 1 - Org 1")
        self.fail("Everything is good, it's just a message to be sure that code was executed")
