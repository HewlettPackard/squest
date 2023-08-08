from django.core.exceptions import ValidationError
from django.db.models import CharField, BooleanField, JSONField
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from towerlib import Tower

from Squest.utils.squest_model import SquestModel


class AnsibleController(SquestModel):
    class Meta:
        permissions = [
            ("sync_ansiblecontroller", "Can sync Ansible controller"),
        ]
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    name = CharField(max_length=100, )
    host = CharField(max_length=200, unique=True)
    token = CharField(max_length=200)
    secure = BooleanField(default=True)
    ssl_verify = BooleanField(default=False)
    extra_vars = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.name} ({self.host})"

    def clean(self):
        if self.extra_vars is None:
            raise ValidationError({'extra_vars': _("Please enter a valid JSON. Empty value is {} for JSON.")})

    def sync(self, job_template_id=None):
        """
        Sync all job templates
        :return:
        """
        from .job_templates import JobTemplate as JobTemplateLocal
        remote_instance = self.get_remote_instance()

        # sync job template
        if job_template_id is None:
            job_template_id_in_remote = []
            for job_template_from_remote in remote_instance.job_templates:
                job_template_id_in_remote.append(job_template_from_remote.id)
                self._update_job_template_from_remote(job_template_from_remote)
            JobTemplateLocal.objects.filter(ansible_controller=self).exclude(
                remote_id__in=job_template_id_in_remote).delete()
        else:
            job_template = JobTemplateLocal.objects.get(id=job_template_id)
            self._update_job_template_from_remote(remote_instance.get_job_template_by_id(job_template.remote_id))

        # sync inventories
        inventory_ids_in_remote = []
        for inventory_from_remote in remote_instance.inventories:
            inventory_ids_in_remote.append(inventory_from_remote.id)
            self._update_inventory_from_remote(inventory_from_remote)
        # delete inventories that do not exist anymore in Ansible controller
        from .inventory import Inventory as InventoryLocal
        InventoryLocal.objects.filter(ansible_controller=self).exclude(
            remote_id__in=inventory_ids_in_remote).delete()

        # sync credentials
        credentials_ids_in_remote = []
        for credential_from_remote in remote_instance.credentials:
            credentials_ids_in_remote.append(credential_from_remote.id)
            self._update_credential_from_remote(credential_from_remote)
        # delete inventories that do not exist anymore in Ansible controller
        from .credential import Credential as CredentialLocal
        CredentialLocal.objects.filter(ansible_controller=self).exclude(
            remote_id__in=credentials_ids_in_remote).delete()

    @property
    def url(self):
        protocol = "https" if self.secure else "http"
        return f"{protocol}://{self.host}"

    def get_remote_instance(self):
        return Tower(self.host, None, None, secure=self.secure, ssl_verify=self.ssl_verify, token=self.token)

    def _update_job_template_from_remote(self, job_template_from_remote):
        from .job_templates import JobTemplate as JobTemplateLocal
        job_template, _ = JobTemplateLocal.objects.get_or_create(remote_id=job_template_from_remote.id,
                                                                 ansible_controller=self,
                                                                 defaults={'name': job_template_from_remote.name})
        # update data
        job_template.name = job_template_from_remote.name
        job_template.remote_job_template_data = job_template_from_remote._data
        job_template.survey = job_template_from_remote.survey_spec
        job_template.is_compliant = job_template.check_is_compliant()
        job_template.save()
        # update all operation that uses this template
        from service_catalog.models import Operation
        Operation.update_survey_after_job_template_update(job_template)

    def _update_inventory_from_remote(self, inventory_from_remote):
        from .inventory import Inventory as InventoryLocal
        inventory, _ = InventoryLocal.objects.get_or_create(remote_id=inventory_from_remote.id,
                                                            ansible_controller=self,
                                                            defaults={'name': inventory_from_remote.name})
        # update data
        inventory.name = inventory_from_remote.name
        inventory.save()

    def _update_credential_from_remote(self, credential_from_remote):
        from .credential import Credential as CredentialLocal
        credential, _ = CredentialLocal.objects.get_or_create(remote_id=credential_from_remote.id,
                                                              ansible_controller=self,
                                                              defaults={'name': credential_from_remote.name})
        # update data
        credential.name = credential_from_remote.name
        credential.save()

    def get_absolute_url(self):
        return reverse_lazy('service_catalog:ansiblecontroller_details', args=[self.pk])
