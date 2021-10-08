import random

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from resource_tracker.models import ResourcePool, ResourceGroup


class BaseTestAPI(APITestCase):

    def setUp(self):
        super(BaseTestAPI, self).setUp()
        # ------------------------------
        # USERS
        # ------------------------------
        self.common_password = "p@ssw0rd"
        # staff user (default user for all tests)
        self.superuser = User.objects.create_superuser('admi1234', 'admin@hpe.com', self.common_password)
        self.client.login(username=self.superuser.username, password=self.common_password)
        # standard user
        self.standard_user = User.objects.create_user('stan1234', 'stan.1234@hpe.com', self.common_password)
        self.standard_user_2 = User.objects.create_user('other1234', 'other.guy@hpe.com', self.common_password)

        # resource pools
        self.rp_vcenter = ResourcePool.objects.create(name="vCenter")
        self.rp_vcenter_vcpu_attribute = self.rp_vcenter.add_attribute_definition(name='vCPU')
        self.rp_vcenter_memory_attribute = self.rp_vcenter.add_attribute_definition(name='Memory')

        self.rp_ocp_workers = ResourcePool.objects.create(name="Openshift workers VM")
        self.rp_ocp_workers_request_cpu_attribute = self.rp_ocp_workers.add_attribute_definition(name='requests.cpu')
        self.rp_ocp_workers_request_memory_attribute = self.rp_ocp_workers.add_attribute_definition(name='requests.memory')

        # resource groups
        self.rg_physical_servers = ResourceGroup.objects.create(name="Physical servers")
        self.rg_physical_servers_cpu_attribute = self.rg_physical_servers.add_attribute_definition(name="CPU")
        self.rg_physical_servers_memory_attribute = self.rg_physical_servers.add_attribute_definition(name="Memory")
        self.rg_physical_servers_description = self.rg_physical_servers.add_text_attribute_definition(name="Description")
        self.rg_physical_servers_text = self.rg_physical_servers.add_text_attribute_definition(name="Another text")

        self.rg_ocp_workers = ResourceGroup.objects.create(name="Worker VMs")
        self.rg_ocp_workers_vcpu_attribute = self.rg_ocp_workers.add_attribute_definition(name="vCPU")
        self.rg_ocp_workers_memory_attribute = self.rg_ocp_workers.add_attribute_definition(name="Memory")

        self.rg_ocp_projects = ResourceGroup.objects.create(name="Openshift projects")
        self.rg_ocp_projects_cpu_attribute = self.rg_ocp_projects.add_attribute_definition(name="requests.cpu")
        self.rg_ocp_projects_mem_attribute = self.rg_ocp_projects.add_attribute_definition(name="requests.memory")

        # attribute links
        self.rp_vcenter_vcpu_attribute.add_producers(self.rg_physical_servers_cpu_attribute)
        self.rp_vcenter_memory_attribute.add_producers(self.rg_physical_servers_memory_attribute)

        self.rp_vcenter_vcpu_attribute.add_consumers(self.rg_ocp_workers_vcpu_attribute)
        self.rp_vcenter_memory_attribute.add_consumers(self.rg_ocp_workers_memory_attribute)

        self.rp_ocp_workers_request_cpu_attribute.add_producers(self.rg_ocp_workers_vcpu_attribute)
        self.rp_ocp_workers_request_memory_attribute.add_producers(self.rg_ocp_workers_memory_attribute)

        self.rp_ocp_workers_request_cpu_attribute.add_consumers(self.rg_ocp_projects_cpu_attribute)
        self.rp_ocp_workers_request_memory_attribute.add_consumers(self.rg_ocp_projects_mem_attribute)

        # Instances
        cpu_list = [30, 40, 50, 100]
        memory_list = [100, 120, 150, 200]
        for i in range(4):
            server = self.rg_physical_servers.create_resource(name=f"server-{i}")
            server.set_attribute(self.rg_physical_servers_cpu_attribute, cpu_list[i])
            server.set_attribute(self.rg_physical_servers_memory_attribute, memory_list[i])

        for i in range(3):
            worker_node = self.rg_ocp_workers.create_resource(name=f"worker{i}")
            worker_node.set_attribute(self.rg_ocp_workers_vcpu_attribute, 16)
            worker_node.set_attribute(self.rg_ocp_workers_memory_attribute, 32)

        for i in range(5):
            new_ocp_project = self.rg_ocp_projects.create_resource(name=f"project-{i}")
            new_ocp_project.set_attribute(self.rg_ocp_projects_cpu_attribute, random.randint(8, 32))
            new_ocp_project.set_attribute(self.rg_ocp_projects_mem_attribute, random.randint(8, 32))
