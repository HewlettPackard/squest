import logging

from celery import shared_task
from django.core import management
from django.core.mail import EmailMultiAlternatives

from .maintenance_jobs import cleanup_ghost_docs_images

logger = logging.getLogger(__name__)


@shared_task()
def sync_tower(tower_id, job_template_id=None):
    from service_catalog.models.tower_server import TowerServer
    if job_template_id is None:
        logger.info(f"[sync_tower] sync tower server with id: {tower_id}")
    else:
        logger.info(f"[sync_tower] sync one job template({job_template_id}) in tower server with id: {tower_id}")
    tower_server = TowerServer.objects.get(id=tower_id)
    tower_server.sync(job_template_id)


@shared_task()
def check_tower_job_status_task(request_id):
    from service_catalog.models.request import Request
    logger.info(f"[check_tower_job_status_task] check Tower job status for request id: {request_id}")
    target_request = Request.objects.get(id=request_id)
    target_request.check_job_status()


@shared_task()
def send_email(subject, plain_text, html_template, from_email, receivers, reply_to, headers=None):
    """
    Pass-through method so we use Celery async
    """
    msg = EmailMultiAlternatives(subject, plain_text, from_email, receivers, reply_to=reply_to, headers=headers)
    msg.attach_alternative(html_template, "text/html")
    msg.send()


@shared_task
def perform_backup():
    logger.info("Execute database backup")
    management.call_command('dbbackup', '--clean')
    logger.info("Database backup complete")
    logger.info("Execute media backup")
    management.call_command('mediabackup', '--clean')
    logger.info("Database media complete")


@shared_task
def task_cleanup_ghost_docs_images():
    cleanup_ghost_docs_images()


@shared_task
def billing_update_quota(billing_group_id):
    logger.info(f"[billing_update_quota] start: billing_group_id: {billing_group_id}")
    from profiles.models.billing_group import BillingGroup
    billing_group = BillingGroup.objects.get(id=billing_group_id)
    for binding in billing_group.quota_bindings.all():
        quota_binding_update_consumed(binding.id, None)
    logger.info(f"[billing_update_quota] end: billing_group_id: {billing_group_id}")


def update_consumed_with_resources(quota_binding_id, resources_to_add=None, resources_to_remove=None):
    from profiles.models.quota_binding import QuotaBinding
    quota_binding = QuotaBinding.objects.get(id=quota_binding_id)
    delta = 0
    if resources_to_add:
        for resource in resources_to_add:
            for attribute in resource.attributes.all():
                if attribute.attribute_type in quota_binding.quota.attribute_definitions.all():
                    delta += attribute.value
    if resources_to_remove:
        for resource in resources_to_remove:
            for attribute in resource.attributes.all():
                if attribute.attribute_type in quota_binding.quota.attribute_definitions.all():
                    delta -= attribute.value
    quota_binding.update_consumed(delta)


def update_quota_with_resources(billing_id_to_add, billing_id_to_remove, resources):
    from profiles.models import BillingGroup
    if billing_id_to_remove:
        billing_to_remove = BillingGroup.objects.get(id=billing_id_to_remove)
        for binding in billing_to_remove.quota_bindings.all():
            update_consumed_with_resources(quota_binding_id=binding.id, resources_to_remove=resources)
    if billing_id_to_add:
        billing_to_add = BillingGroup.objects.get(id=billing_id_to_add)
        for binding in billing_to_add.quota_bindings.all():
            update_consumed_with_resources(quota_binding_id=binding.id, resources_to_add=resources)


@shared_task
def instance_update_quota_on_billing_group_change(instance_id, billing_id_to_remove=None, billing_id_to_add=None):
    logger.info(f"[instance_update_quota_on_billing_group_change] start: instance_id: {instance_id}, billing_id_to_add: {billing_id_to_add}, "
                f"billing_id_to_remove: {billing_id_to_remove}")
    from service_catalog.models import Instance
    resources = Instance.objects.get(id=instance_id).resources.all()
    update_quota_with_resources(billing_id_to_add, billing_id_to_remove, resources)
    logger.info(f"[instance_update_quota_on_billing_group_change] end: instance_id: {instance_id}, billing_id_to_add: {billing_id_to_add}, "
                f"billing_id_to_remove: {billing_id_to_remove}")


@shared_task
def resource_update_quota_on_instance_change(resource_id, billing_id_to_remove=None, billing_id_to_add=None):
    logger.info(f"[resource_update_quota_on_instance_change] start: resource_id: {resource_id}, billing_id_to_add: {billing_id_to_add}, "
                f"billing_id_to_remove: {billing_id_to_remove}")
    from resource_tracker.models import Resource
    resources = [Resource.objects.get(id=resource_id)]
    update_quota_with_resources(billing_id_to_add=billing_id_to_add, billing_id_to_remove=billing_id_to_remove,
                                resources=resources)
    logger.info(f"[resource_update_quota_on_instance_change] end: resource_id: {resource_id}, billing_id_to_add: {billing_id_to_add}, "
                f"billing_id_to_remove: {billing_id_to_remove}")


@shared_task
def quota_update_consumed(quota_id):
    logger.info(f"[quota_update_consumed] start: resource_id: {quota_id}")
    from profiles.models.quota import Quota
    quota = Quota.objects.get(id=quota_id)
    for quota_binding in quota.quota_bindings.all():
        quota_binding.update_consumed()
    logger.info(f"[quota_update_consumed] start: resource_id: {quota_id}")


@shared_task
def quota_binding_update_consumed(quota_binding_id, delta=None):
    logger.info(f"[quota_binding_update_consumed] start: quota_binding_id: {quota_binding_id}, delta: {delta}")
    from profiles.models.quota_binding import QuotaBinding
    quota_binding = QuotaBinding.objects.get(id=quota_binding_id)
    quota_binding.update_consumed(delta)
    logger.info(f"[quota_binding_update_consumed] end: quota_binding_id: {quota_binding_id}, delta: {delta}")


@shared_task
def resource_attribute_update_consumed(resource_attribute_id, delta):
    logger.info(f"[resource_attribute_update_consumed] start: resource_attribute_id: {resource_attribute_id}, delta: "
                f"{delta}")
    from resource_tracker.models import ResourceAttribute
    resource_attribute = ResourceAttribute.objects.get(id=resource_attribute_id)
    for quota in resource_attribute.attribute_type.quota.all():
        for binding in quota.quota_bindings.filter(billing_group=resource_attribute.resource.service_catalog_instance.billing_group):
            binding.update_consumed(delta)
    logger.info(f"[resource_attribute_update_consumed] end: resource_attribute_id: {resource_attribute_id}, delta: "
                f"{delta}")
