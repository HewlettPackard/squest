import logging

from django.db.models import CharField, IntegerField, JSONField, ForeignKey, CASCADE, BooleanField
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.urls import reverse

from Squest.utils.squest_model import SquestModel
from . import BootstrapType, ExceptionServiceCatalog, AnsibleController

logger = logging.getLogger(__name__)


class JobTemplate(SquestModel):
    class Meta:
        unique_together = ('remote_id', 'ansible_controller',)
        default_permissions = ('add', 'change', 'delete', 'view', 'list')

    name = CharField(max_length=100)
    remote_id = IntegerField()
    survey = JSONField(default=dict)
    ansible_controller = ForeignKey(AnsibleController, on_delete=CASCADE)
    remote_job_template_data = JSONField(default=dict)
    is_compliant = BooleanField(default=False)

    @property
    def remote_url(self):
        return f"{self.ansible_controller.url}/#/templates/job_template/{self.remote_id}"

    def __str__(self):
        return f"{self.name} ({self.ansible_controller.name})"

    def execute(self, extra_vars, inventory_override=None, credentials_override=None, tags_override=None,
                skip_tags_override=None, limit_override=None, verbosity_override=None, job_type_override=None,
                diff_mode_override=None):
        job_template = self.ansible_controller.get_remote_instance().get_job_template_by_id(self.remote_id)
        if job_template is None:
            raise ExceptionServiceCatalog.JobTemplateNotFound(ansible_controller_name=self.ansible_controller.name,
                                                              job_template_id=self.remote_id)

        try:
            credentials_override_to_list = list(map(int, credentials_override))
        except TypeError:
            credentials_override_to_list = None
        if inventory_override is not None:
            inventory_override = int(inventory_override)
        if verbosity_override is not None:
            verbosity_override = int(verbosity_override)
        parameters = {
            "extra_vars": extra_vars,
            "inventory": inventory_override,
            "credentials": credentials_override_to_list,
            "job_tags": tags_override,
            "skip_tags": skip_tags_override,
            "limit": limit_override,
            "verbosity": verbosity_override,
            "job_type": job_type_override,
            "diff_mode": diff_mode_override,
        }
        logger.info(f"[job-template-execute] Execute job template with parameter: {parameters}")
        job_run = job_template.launch(**parameters)
        return job_run.id

    def check_is_compliant(self):
        return self.is_ask_variables_on_launch_compliant()

    def get_compliancy_details(self):
        return [
            dict(
                name='Variables/Prompt on launch',
                description='By default, recent version of Ansible Controller/AWX drop extra variables that are not declared in the '
                            'survey. To be able to receive Squest extra vars you need to enable "Prompt on Launch" in '
                            'the "Variables" section of you job template. This correspond to the flag '
                            '"ask_variables_on_launch" of the job_template model on the Ansible Controller/AWX API.',
                state=self.is_ask_variables_on_launch_compliant(),
                type=BootstrapType.SUCCESS if self.is_ask_variables_on_launch_compliant() else BootstrapType.WARNING,
            )
        ]

    # Compliance checks
    def is_ask_variables_on_launch_compliant(self):
        return self.remote_job_template_data['ask_variables_on_launch']

    def has_a_survey(self):
        if self.survey is not None and "spec" in self.survey:
            return True
        return False

    def get_absolute_url(self):
        return reverse('service_catalog:jobtemplate_details', args=[self.ansible_controller.id, self.pk])


@receiver(pre_delete, sender=JobTemplate)
def job_template_delete(sender, instance, using, **kwargs):
    from . import Service, OperationType
    Service.objects.filter(operation__job_template=instance, operation__type__exact=OperationType.CREATE).update(
        **{"enabled": False})
