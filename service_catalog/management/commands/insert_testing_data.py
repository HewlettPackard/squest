import logging
import random

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
        # create resource pools
        print("Create vCenter resource pool")
        vcenter_pool = ResourcePool.objects.create(name="vCenter")
        vcenter_pool.add_attribute_definition(name='vCPU')
        vcenter_pool.add_attribute_definition(name='Memory')

        print("Create Openshift resource pool")
        ocp_pool = ResourcePool.objects.create(name="Openshift projects")
        ocp_pool.add_attribute_definition(name='requests.cpu')
        ocp_pool.add_attribute_definition(name='requests.memory')

        # resources
        print("Create physical server resource pool")
        server_group = ResourceGroup.objects.create(name="Physical servers")
        server_group_cpu_attribute = server_group.add_attribute_definition(name="CPU")
        server_group_memory_attribute = server_group.add_attribute_definition(name="Memory")

        print("Create Openshift masters resource pool")
        ocp_master_node_group = ResourceGroup.objects.create(name="Openshift masters")
        ocp_master_node_group_vcpu_attribute = ocp_master_node_group.add_attribute_definition(name="vCPU")
        ocp_master_node_group_memory_attribute = ocp_master_node_group.add_attribute_definition(name="Memory")

        print("Create Openshift workers resource pool")
        ocp_worker_node_group = ResourceGroup.objects.create(name="Openshift workers")
        ocp_worker_node_group_vcpu_attribute = ocp_worker_node_group.add_attribute_definition(name="vCPU")
        ocp_worker_node_group_memory_attribute = ocp_worker_node_group.add_attribute_definition(name="Memory")

        print("Create Openshift projects resource pool")
        ocp_project_group = ResourceGroup.objects.create(name="Openshift Project")
        ocp_project_group_cpu_att = ocp_project_group.add_attribute_definition(name="requests.cpu")
        ocp_project_group_mem_att = ocp_project_group.add_attribute_definition(name="requests.memory")

        # Links
        print("Physical server resources produce into vCenter pool")
        vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(server_group.attribute_definitions.get(name='CPU'))
        vcenter_pool.attribute_definitions.get(name='Memory') \
            .add_producers(server_group.attribute_definitions.get(name='Memory'))

        print("Openshift master resources consume from vCenter pool")
        vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_consumers(ocp_master_node_group.attribute_definitions.get(name='vCPU'))
        vcenter_pool.attribute_definitions.get(name='Memory') \
            .add_consumers(ocp_master_node_group.attribute_definitions.get(name='Memory'))

        print("Openshift worker resources consume from vCenter pool")
        vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_consumers(ocp_worker_node_group.attribute_definitions.get(name='vCPU'))
        vcenter_pool.attribute_definitions.get(name='Memory') \
            .add_consumers(ocp_worker_node_group.attribute_definitions.get(name='Memory'))

        print("Openshift worker resources produce to Openshift project pool")
        ocp_pool.attribute_definitions.get(name='requests.cpu') \
            .add_producers(ocp_worker_node_group.attribute_definitions.get(name='vCPU'))
        ocp_pool.attribute_definitions.get(name='requests.memory') \
            .add_producers(ocp_worker_node_group.attribute_definitions.get(name='Memory'))

        print("Openshift project resources consume from Openshift project pool")
        ocp_pool.attribute_definitions.get(name='requests.cpu') \
            .add_consumers(ocp_project_group.attribute_definitions.get(name='requests.cpu'))
        ocp_pool.attribute_definitions.get(name='requests.memory') \
            .add_consumers(ocp_project_group.attribute_definitions.get(name='requests.memory'))

        # Instances
        print("Create instances in each resource group")
        cpu_list = [30, 40, 50, 100]
        memory_list = [100, 120, 150, 200]
        for i in range(4):
            server = server_group.create_resource(name=f"server-{i}")
            server.set_attribute(server_group_cpu_attribute, cpu_list[i])
            server.set_attribute(server_group_memory_attribute, memory_list[i])

        for i in range(3):
            master_node = ocp_master_node_group.create_resource(name=f"master{i}")
            master_node.set_attribute(ocp_master_node_group_vcpu_attribute, 8)
            master_node.set_attribute(ocp_master_node_group_memory_attribute, 16)

        for i in range(3):
            worker_node = ocp_worker_node_group.create_resource(name=f"worker{i}")
            worker_node.set_attribute(ocp_worker_node_group_vcpu_attribute, 16)
            worker_node.set_attribute(ocp_worker_node_group_memory_attribute, 32)

        for i in range(5):
            new_ocp_project = ocp_project_group.create_resource(name=f"project-{i}")
            new_ocp_project.set_attribute(ocp_project_group_cpu_att, random.randint(8, 32))
            new_ocp_project.set_attribute(ocp_project_group_mem_att, random.randint(8, 32))
