import logging
import os

from Squest import settings
from resource_tracker.models import ResourceGroup

import yaml
from django.core.management import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.default_data = None
        logger.debug("[export_resource_tracker_v1] Start")

    def handle(self, *args, **options):
        resource_tracker_v1_data = dict()
        resource_tracker_v1_data['resource_groups'] = list()
        for resource_group in ResourceGroup.objects.all():
            resource_group_data = {
                'name': resource_group.name,
                'attribute_definitions': list(),
                'tags': list(resource_group.tags.names()),
                'resources': list()

            }
            for attribute_definition in resource_group.attribute_definitions.all():
                if attribute_definition.consume_from is None:
                    resource_pool_attribute_data = {}
                else:
                    resource_pool_attribute_data = {
                        'yellow_threshold_percent_consumed': attribute_definition.consume_from.yellow_threshold_percent_consumed,
                        'red_threshold_percent_consumed': attribute_definition.consume_from.red_threshold_percent_consumed,
                        'over_commitment_producers': attribute_definition.consume_from.over_commitment_producers,
                        'over_commitment_consumers': attribute_definition.consume_from.over_commitment_consumers,
                        'producers': list()
                    }
                    for producer in attribute_definition.consume_from.producers.all():
                        producer_data = {
                            'name': producer.name,
                            'resource_group': {
                                'name': producer.resource_group.name
                            }
                        }
                        resource_pool_attribute_data['producers'].append(producer_data)
                attribute_definition_data = {
                    'name': attribute_definition.name,
                    'help_text': attribute_definition.help_text,
                    'consume_from': resource_pool_attribute_data
                }

                resource_group_data['attribute_definitions'].append(attribute_definition_data)
            for resource in resource_group.resources.all():
                resource_data = {
                    'name': resource.name,
                    'tags': list(resource.tags.names()),
                    'service_catalog_instance': {
                        'id': None if resource.service_catalog_instance is None else resource.service_catalog_instance.id},
                    'is_deleted_on_instance_deletion': resource.is_deleted_on_instance_deletion,
                    'attributes': list()
                }
                for attribute in resource.attributes.all():
                    attribute_data = {
                        'attribute_type': {
                            'name': attribute.attribute_type.name
                        },
                        'value': attribute.value
                    }
                    resource_data['attributes'].append(attribute_data)
                resource_group_data['resources'].append(resource_data)
            resource_tracker_v1_data['resource_groups'].append(resource_group_data)
        if not os.path.exists(f'{settings.MEDIA_ROOT}/tmp_files'):
            os.mkdir(f'{settings.MEDIA_ROOT}/tmp_files')
        with open(f'{settings.MEDIA_ROOT}/tmp_files/resource_tracker_v1.yaml', 'w') as file:
            yaml.dump(resource_tracker_v1_data, file)
        logger.debug(f"[export_resource_tracker_v1] File exported in {settings.MEDIA_ROOT}/tmp_files/resource_tracker_v1.yaml")
