from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from rest_framework import serializers
from Squest.utils.plugin_controller import PluginController


class TestSSHPublicKeyValidator(TestCase):
    def test_with_wrong_ssh_key(self):
        public_ssh_key = "aaaa bbbb cccc"
        loaded_module = PluginController.get_ui_field_validator_def("is_public_ssh_key")
        with self.assertRaises(ValidationError):
            loaded_module(public_ssh_key)
        loaded_module = PluginController.get_api_field_validator_def("is_public_ssh_key")
        with self.assertRaises(serializers.ValidationError):
            loaded_module(public_ssh_key)

    def test_with_rsa(self):
        public_ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDeJvMJmt63nSi7sO6tKGHxnmvOckWaypcZKaPl5KLDCL5RsiaZMi/NrniiLsgv8FX5txQmsU2e1W7Ozh6VBGVErwV7S/GCkcYqO91lhZ+jVA7QHsK7hQWubq5zJzBm+p2HFSQk3ch0tXxhMbGivL1AkqziABgKLzhFeLIWzG3OCy8kj/F9b8doRiQ2FkMCT3sCGEts7nXQJ/0WyMj0FwyNr/R93+P/57M2QG49Wr7iFInzr6+BDcClmGMNHXNepvLQFHuW4suVU3Q7UaHFp9b1kDGbcbiw/w4JEutxuKv+DLOfm4pd8YhQsB8begILTwi5PJpvqfCSuE1jMN054t7xVssJU1Po5jMcSWfN8Q+/l7SSFgkCRH4Ul7LF+bMM8z3FejMp96CFmFagIePzqpnwjy4NLSEeESQhVCosPXpwCuwvZuebEgeptV8mK3TnVUksZmwnQrqwDqa6s9nZCjf/UZ03b73eFPcRwO0dgC2aWXvjzCB9SimdIBaMYMjtnuZJxADrb1AG9MTaBIj4bvn3phsx8OyZpc0c7mdyp1Quh5jBOwNJX7wU716o5lu5cMHTE29VFMIGz3yT+/ETxpC3/9CWuKLQoJFcV9PNzBScIIB2m7A+zkaEFbCDoCJqX8R5fs6Vsnq3vyEDu2VCGw3NUW+lQ+Di4y4+pAkhTaI4Mw== squest@fake"
        loaded_module = PluginController.get_api_field_validator_def("is_public_ssh_key")
        try:
            loaded_module(public_ssh_key)
        except ValidationError:
            self.fail("UI validator fail")
        loaded_module = PluginController.get_api_field_validator_def("is_public_ssh_key")
        try:
            loaded_module(public_ssh_key)
        except serializers.ValidationError:
            self.fail("API validator fail")

    def test_with_ed25519(self):
        public_ssh_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPYqhDwOvBaWrGC257fdxfy1iMM6ZY2VwgmP+XlRRMT8 squest@fake"
        loaded_module = PluginController.get_api_field_validator_def("is_public_ssh_key")
        try:
            loaded_module(public_ssh_key)
        except ValidationError:
            self.fail("UI validator fail")
        loaded_module = PluginController.get_api_field_validator_def("is_public_ssh_key")
        try:
            loaded_module(public_ssh_key)
        except serializers.ValidationError:
            self.fail("API validator fail")


