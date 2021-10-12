from django.db import models

from service_catalog.models import OperationType


class Service(models.Model):
    name = models.CharField(verbose_name="Service name", max_length=100)
    description = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='service_image', blank=True)
    billing_group_id = models.IntegerField(null=True, default=None)
    billing_group_is_shown = models.BooleanField(default=False)
    billing_group_is_selectable = models.BooleanField(default=False)
    billing_groups_are_restricted = models.BooleanField(default=True)
    enabled = models.BooleanField(default=True)

    def asert_create_operation_have_job_template(self):
        operation_create = self.operations.filter(type=OperationType.CREATE)
        if operation_create.count() == 1:
            if operation_create.first().job_template is not None:
                return True
        return False

    def __str__(self):
        return self.name

    def create_provisioning_operation(self, job_template):
        if self.operations.filter(type=OperationType.CREATE):
            raise Exception({"Provisionning operation": "A service can have only one 'CREATE' operation"})
        from service_catalog.models import Operation
        Operation.objects.create(name=self.name,
                                 service=self,
                                 job_template=job_template
                                 )
        self.save()
