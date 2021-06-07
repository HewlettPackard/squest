import logging

import yaml
from django.contrib.auth.models import User
from django.core.management import BaseCommand

from resource_tracker.models import ResourceGroup, ResourcePool

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.default_data = None
        print("[insert_testing_data] Start")

    def handle(self, *args, **options):
        print("ok")
        # name = r'serverGroup1'
        # server_group = ResourceGroup.objects.create(name=name)
        # attribute = r'CPU'
        # server_group.add_attribute_definition(name=attribute)
        #
        # server1 = server_group.create_resource(name="server1")
        # server1.set_attribute('CPU', 80)
        #
        # server2 = server_group.create_resource(name="server2")
        # server2.set_attribute('CPU', 100)

        vcenter_pool = ResourcePool.objects.create(name="vcenter-pool")
        vcenter_pool.add_attribute_definition(name='vCPU')

        ocp_pool = ResourcePool.objects.create(name="openshift")
        ocp_pool.add_attribute_definition(name='vCPU')

