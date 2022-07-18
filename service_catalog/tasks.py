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
def send_email(subject, plain_text, html_template, from_email, receivers=None, bcc=None, reply_to=None, headers=None):
    """
    Pass-through method so we use Celery async
    """
    if not receivers and not bcc and not reply_to:
        logger.info(f"[send_email] no receivers for the email. Email not sent.")
        return
    logger.info(f"[send_email] celery task executed - subject: '{subject}',"
                f" from_email: '{from_email}',"
                f" receivers: '{receivers}',"
                f" reply_to: '{reply_to}',"
                f" bcc: '{bcc}'")
    msg = EmailMultiAlternatives(subject, plain_text, from_email, to=receivers,
                                 bcc=bcc,
                                 reply_to=reply_to,
                                 headers=headers)
    msg.attach_alternative(html_template, "text/html")
    msg.send()
    logger.info(f"[send_email] email sent")


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
def async_billing_group_quota_bindings_update_consumed(billing_group_id):
    logger.info(f"[async_billing_group_quota_bindings_update_consumed] start: billing_group_id: {billing_group_id}")
    from profiles.models.billing_group import BillingGroup
    billing_group = BillingGroup.objects.get(id=billing_group_id)
    billing_group.quota_bindings_update_consumed()
    logger.info(f"[async_billing_group_quota_bindings_update_consumed] end: billing_group_id: {billing_group_id}")


@shared_task
def async_quota_bindings_add_instance(instance_id, billing_id):
    logger.info(f"[async_quota_bindings_add_instance] start: instance_id: {instance_id}, billing_id: {billing_id}")
    from service_catalog.models import Instance
    from profiles.models import BillingGroup
    instance = Instance.objects.get(id=instance_id)
    billing = BillingGroup.objects.get(id=billing_id)
    billing.quota_bindings_add_instance(instance)
    logger.info(f"[async_quota_bindings_add_instance] end: instance_id: {instance_id}, billing_id: {billing_id}")


@shared_task
def async_quota_bindings_remove_instance(instance_id, billing_id):
    logger.info(f"[async_quota_bindings_remove_instance] start: instance_id: {instance_id}, billing_id: {billing_id}")
    from service_catalog.models import Instance
    from profiles.models import BillingGroup
    instance = Instance.objects.get(id=instance_id)
    billing = BillingGroup.objects.get(id=billing_id)
    billing.quota_bindings_remove_instance(instance)
    logger.info(f"[async_quota_bindings_remove_instance] end: instance_id: {instance_id}, billing_id: {billing_id}")


@shared_task
def async_quota_bindings_remove_resource(resource_id, billing_id):
    logger.info(f"[async_quota_bindings_remove_resource] start: resource_id: {resource_id}, billing_id: {billing_id}")
    from profiles.models import BillingGroup
    from resource_tracker.models import Resource
    resource = Resource.objects.get(id=resource_id)
    billing = BillingGroup.objects.get(id=billing_id)
    billing.quota_bindings_remove_resource(resource)
    logger.info(f"[async_quota_bindings_remove_resource] end: resource_id: {resource_id}, billing_id: {billing_id}")


@shared_task
def async_quota_bindings_add_resource(resource_id, billing_id):
    logger.info(f"[async_quota_bindings_add_resource] start: resource_id: {resource_id}, billing_id: {billing_id}")
    from resource_tracker.models import Resource
    from profiles.models import BillingGroup
    resource = Resource.objects.get(id=resource_id)
    billing = BillingGroup.objects.get(id=billing_id)
    billing.quota_bindings_add_resource(resource)
    logger.info(f"[async_quota_bindings_add_resource] end: resource_id: {resource_id}, billing_id: {billing_id}")


@shared_task
def async_quota_bindings_update_consumed(quota_id):
    logger.info(f"[async_quota_bindings_update_consumed] start: resource_id: {quota_id}")
    from profiles.models.quota import Quota
    quota = Quota.objects.get(id=quota_id)
    quota.quota_bindings_update_consumed()
    logger.info(f"[async_quota_bindings_update_consumed] start: resource_id: {quota_id}")


@shared_task
def async_quota_binding_calculate_consumed(quota_binding_id, delta=None):
    logger.info(f"[async_quota_binding_calculate_consumed] start: quota_binding_id: {quota_binding_id}, delta: {delta}")
    from profiles.models.quota_binding import QuotaBinding
    quota_binding = QuotaBinding.objects.get(id=quota_binding_id)
    quota_binding.calculate_consumed(delta)
    logger.info(f"[async_quota_binding_calculate_consumed] end: quota_binding_id: {quota_binding_id}, delta: {delta}")


@shared_task
def async_resource_attribute_quota_bindings_update_consumed(resource_attribute_id, delta):
    logger.info(
        f"[async_resource_attribute_quota_bindings_update_consumed] start: resource_attribute_id: {resource_attribute_id}, delta: "
        f"{delta}")
    from resource_tracker.models import ResourceAttribute
    resource_attribute = ResourceAttribute.objects.get(id=resource_attribute_id)
    resource_attribute.quota_bindings_update_consumed(delta)
    logger.info(
        f"[async_resource_attribute_quota_bindings_update_consumed] end: resource_attribute_id: {resource_attribute_id}, delta: "
        f"{delta}")


@shared_task
def async_update_all_consumed_and_produced(resource_pool_id):
    logger.info(f"[async_update_all_consumed_and_produced] start: resource_pool_id: {resource_pool_id}")
    from resource_tracker.models import ResourcePool
    resource_pool = ResourcePool.objects.get(id=resource_pool_id)
    resource_pool.update_all_consumed_and_produced()
    logger.info(f"[async_update_all_consumed_and_produced] end: resource_pool_id: {resource_pool_id}")


@shared_task
def async_recalculate_total_resources(resource_group_id):
    logger.info(f"[async_recalculate_total_resources] start: resource_group_id: {resource_group_id}")
    from resource_tracker.models import ResourceGroup
    resource_group = ResourceGroup.objects.get(id=resource_group_id)
    resource_group.recalculate_total_resources()
    logger.info(f"[async_recalculate_total_resources] end: resource_group_id: {resource_group_id}")
