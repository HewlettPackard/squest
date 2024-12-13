# Survey validators

Survey validators are Python modules that can be added as plugin. It allows users to implement their own validation
logic on a day1 or day2 operation against the full survey.

## Creating survey validator

Create a Python file in **SURVEY_VALIDATOR_PATH** (default is `plugins/survey_validators`).
Create Python class that inherit from SurveyValidator with a method `validate_survey`.

```python
# plugins/survey_validators/MySurveyValidator.py
from service_catalog.forms.form_utils import SurveyValidator

class MyCustomValidatorFoo(SurveyValidator):
    def validate_survey(self):
        # Implement your own logic here
        pass
```

## SurveyValidator attributes

### survey

This is a dict containing survey + request_comment. Keys are variable name.  
type: dict

```bash
>>> print(self.survey)
{
  "request_comment": "commentary sent by user"
  "ram_gb": 8,
  "vcpu": 4
}
```

### user

User requesting operation.  
type: django.contrib.auth.models.User

### operation

Operation requested.   
type: service_catalog.models.Operation

### instance

Instance targeted.  
type: service_catalog.models.Instance

!!!note
    For day 1 operation `self.instance` is a FakeInstance object that contains only **name** and **quota_scope** without `save` method.
    The real Instance object is created after validation.

## SurveyValidator method

### validate_survey(self)

Redefine it to implement your own logic.

### fail(self, message, field="\_\_all\_\_")

Raise an exception and display message on UI/API.

## Set validator to a form field

In Squest, edit an Operation to set validators. Multiples validators can be added, validators are executed in alphabetical order by script name and class name.

## Example

This validator will always fail if:

- ram and cpu are both equal 1
- It's not the weekend yet

```python
from service_catalog.forms.form_utils import SurveyValidator
import datetime

class ValidatorForVM(SurveyValidator):
    def validate_survey(self):
        if self.survey.get("ram") == 1 and  self.survey.get("vcpu") == 1:
            self.fail("Forbidden: you cannot use ram=1 and cpu=1")

        weekday = datetime.datetime.today().weekday()        
        if weekday < 5:            
            self.fail("Sorry it's not the weekend yet")
```