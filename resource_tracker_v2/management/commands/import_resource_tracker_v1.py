import logging
import os.path

import yaml

from Squest import settings
from resource_tracker_v2.models import ResourceGroup, AttributeDefinition, Transformer, Resource
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


def import_v1():
    with open(f'{settings.MEDIA_ROOT}/tmp_files/resource_tracker_v1.yaml', 'r') as file:
        data = yaml.safe_load(file)
    # First Loop to create Resources Groups, Attributes, Resources and Transformers
    for resource_group in data['resource_groups']:
        logger.debug(f"[import_resource_tracker_v1] Create {resource_group['name']} ResourceGroup")
        resource_group_v2 = ResourceGroup.objects.create(name=resource_group['name'])
        if resource_group['tags']:
            logger.debug(f"[import_resource_tracker_v1] Add tags in {resource_group['name']} ResourceGroup")
            resource_group_v2.tags.add(*resource_group['tags'])
        for attribute_definition in resource_group['attribute_definitions']:
            logger.debug(f"[import_resource_tracker_v1] Create {attribute_definition['name']} AttributeDefinition")
            attribute_v2, created = AttributeDefinition.objects.get_or_create(name=attribute_definition['name'])
            if created:
                attribute_v2.description = attribute_definition['help_text']
                attribute_v2.save()
            logger.debug(
                f"[import_resource_tracker_v1] Create {attribute_definition['name']} Transformer in {resource_group['name']} ResourceGroup")
            Transformer.objects.create(resource_group=resource_group_v2, attribute_definition=attribute_v2)
        for resource in resource_group['resources']:
            logger.debug(f"[import_resource_tracker_v1] Create {resource['name']} Resource")
            resource_v2 = Resource.objects.create(
                name=resource['name'],
                resource_group=resource_group_v2,
                service_catalog_instance_id=resource['service_catalog_instance']['id'],
                is_deleted_on_instance_deletion=resource['is_deleted_on_instance_deletion'])
            if resource['tags']:
                logger.debug(f"Add tags in {resource['name']} Resource")
                resource_v2.tags.add(*resource['tags'])
            for attribute in resource['attributes']:
                logger.debug(
                    f"[import_resource_tracker_v1] Set value of {attribute['attribute_type']['name']} Attribute in {resource['name']} Resource")
                resource_v2.set_attribute(AttributeDefinition.objects.get(name=attribute['attribute_type']['name']),
                                          attribute['value'])

    # Second Loop to create link with Transformers
    for resource_group in data['resource_groups']:
        resource_group_v2 = ResourceGroup.objects.get(name=resource_group['name'])
        for attribute_definition in resource_group['attribute_definitions']:
            resource_pool_attribute = attribute_definition['consume_from']
            logger.debug(
                f"[import_resource_tracker_v1] Change {attribute_definition['name']} Transformer in {resource_group['name']} ResourceGroup")
            if resource_pool_attribute:
                attribute_v2 = AttributeDefinition.objects.get(name=attribute_definition['name'])
                transformer = Transformer.objects.get(resource_group=resource_group_v2,
                                                      attribute_definition=attribute_v2)
                if resource_pool_attribute['producers']:
                    transformer.consume_from_resource_group = ResourceGroup.objects.get(
                        name=resource_pool_attribute['producers'][0]['resource_group']['name'])
                    transformer.consume_from_attribute_definition = AttributeDefinition.objects.get(
                        name=resource_pool_attribute['producers'][0]['name'])
                transformer.factor = resource_pool_attribute['over_commitment_producers'] * resource_pool_attribute[
                    'over_commitment_consumers']
                transformer.yellow_threshold_percent_consumed = resource_pool_attribute[
                    'yellow_threshold_percent_consumed']
                transformer.red_threshold_percent_consumed = resource_pool_attribute[
                    'red_threshold_percent_consumed']
                transformer.save()
    logger.debug("[import_resource_tracker_v1] Migration done")


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.default_data = None
        logger.debug("[import_resource_tracker_v1] Start")

    def handle(self, *args, **options):
        if os.path.exists(f'{settings.MEDIA_ROOT}/tmp_files/resource_tracker_v1.yaml'):
            import_v1()
        else:
            logger.debug(
                f"[import_resource_tracker_v1] No migration file ({settings.MEDIA_ROOT}/tmp_files/resource_tracker_v1.yaml)")
