import logging
import os
import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from profiles.models import Organization, Role
from resource_tracker_v2.models import AttributeDefinition, Resource, ResourceGroup, Transformer
from service_catalog.models import AnsibleController, JobTemplate, Service, Operation, Instance, Request
from service_catalog.models.operations import OperationType
from service_catalog.models.request import RequestState

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def __init__(self):
        super().__init__()
        self.default_data = None
        print("[insert_testing_data] Start")

    def handle(self, *args, **options):
        users_name = ['Elias', 'Nicolas', 'Anthony', 'Mathijs', 'Jeff', 'Mark']
        users = {}
        for username in users_name:
            try:
                users[username] = User.objects.get(username=username, password="admin")
            except User.DoesNotExist:
                users[username] = User.objects.create_user(username=username, password="admin", is_staff=False,
                                                           is_superuser=False)
            # team = Team.objects.create(name=username)
            # team.add_user_in_role(users[username], "Admin")
            logger.info(f"Get or create '{users[username]}'")
        awx_token = os.environ['AWX_TOKEN']
        awx_host = os.environ['AWX_HOST']
        tower, _ = AnsibleController.objects.get_or_create(name=r'AWX HPE', host=awx_host,
                                                           token=awx_token)
        logger.info('AWX added')
        print('Launch celery to sync: celery - A service_catalog worker - l info')
        tower.sync()

        organization_name = ['5G', 'Assurance', 'Orchestration']
        organization = []
        for billing_group in organization_name:
            organization.append(Organization.objects.get_or_create(name=billing_group)[0])

        Organization.objects.get(name="Orchestration").add_user_in_role(User.objects.get(username="Anthony"),
                                                                        Role.objects.get(name="Organization member"))
        Organization.objects.get(name="Orchestration").add_user_in_role(User.objects.get(username="Anthony"),
                                                                        Role.objects.get(name="Instance viewer"))

        job_templates = JobTemplate.objects.all()
        services = dict()
        services['vmware_service'], _ = Service.objects.get_or_create(name="VMWare")

        services['OCP_service'], _ = Service.objects.get_or_create(name="OCP")

        services['K8S_service'], _ = Service.objects.get_or_create(name="K8S")
        for service_name in services:
            service = services[service_name]
            Operation.objects.get_or_create(name=service.name,
                                            service=service,
                                            job_template=job_templates.get(name="Demo Job Template"))
            Operation.objects.get_or_create(name="Delete my resource",
                                            type=OperationType.DELETE,
                                            service=service,
                                            job_template=job_templates.get(name="Demo Job Template"))
            states = [RequestState.SUBMITTED, RequestState.FAILED, RequestState.ACCEPTED, RequestState.NEED_INFO,
                      RequestState.REJECTED, RequestState.CANCELED, RequestState.PROCESSING, RequestState.COMPLETE]
            for i in range(random.randint(1, 3)):
                for username in users:
                    if random.randint(0, 2) == 1:
                        continue
                    user = users[username]
                    new_instance = Instance.objects.create(service=service, name=f"Instance - {username} - {i}",
                                                           requester=user, quota_scope=random.choice(organization))
                    # create the request
                    new_request, _ = Request.objects.get_or_create(instance=new_instance,
                                                                   operation=service.operations.filter(
                                                                       type=OperationType.CREATE)[0],
                                                                   state=random.choice(states),
                                                                   fill_in_survey=dict(),
                                                                   user=user)

        # ----------------------
        # resource tracker v2
        # ----------------------
        # layer 1: vcenter
        core_attribute = AttributeDefinition.objects.create(name="core")
        memory_attribute = AttributeDefinition.objects.create(name="memory")
        disk = AttributeDefinition.objects.create(name="disk")
        cluster = ResourceGroup.objects.create(name="cluster")
        # cluster --> core
        Transformer.objects.create(resource_group=cluster,
                                   attribute_definition=core_attribute)
        # cluster --> memory
        Transformer.objects.create(resource_group=cluster,
                                   attribute_definition=memory_attribute)
        # cluster --> 3par
        Transformer.objects.create(resource_group=cluster,
                                   attribute_definition=disk)

        server1 = Resource.objects.create(name="server1", resource_group=cluster)
        server1.set_attribute(core_attribute, 10)
        server1.set_attribute(memory_attribute, 50)

        server2 = Resource.objects.create(name="server2", resource_group=cluster)
        server2.set_attribute(core_attribute, 30)
        server2.set_attribute(memory_attribute, 10)

        # layer 2 VM (workers)
        single_vms = ResourceGroup.objects.create(name="single_vms")
        vcpu_attribute = AttributeDefinition.objects.create(name="vcpu")
        v_memory_attribute = AttributeDefinition.objects.create(name="vmemory")
        # vcpu --> core
        Transformer.objects.create(resource_group=single_vms,
                                   attribute_definition=vcpu_attribute,
                                   consume_from_resource_group=cluster,
                                   consume_from_attribute_definition=core_attribute)
        # vvmemory --> memory
        Transformer.objects.create(resource_group=single_vms,
                                   attribute_definition=v_memory_attribute,
                                   consume_from_resource_group=cluster,
                                   consume_from_attribute_definition=memory_attribute)
        # add resources
        vm1 = Resource.objects.create(name="vm1", resource_group=single_vms)
        vm1.set_attribute(vcpu_attribute, 5)
        vm1.set_attribute(v_memory_attribute, 4)
        vm2 = Resource.objects.create(name="vm2", resource_group=single_vms)
        vm2.set_attribute(vcpu_attribute, 15)
        vm2.set_attribute(v_memory_attribute, 8)

        # layer 3: ocp project
        ocp_projects = ResourceGroup.objects.create(name="ocp_projects")
        request_cpu = AttributeDefinition.objects.create(name="request.cpu")
        request_memory = AttributeDefinition.objects.create(name="request.memory")
        # request.cpu --> vcpu
        Transformer.objects.create(resource_group=ocp_projects,
                                   attribute_definition=request_cpu,
                                   consume_from_resource_group=single_vms,
                                   consume_from_attribute_definition=vcpu_attribute)
        # request.memory --> v-memory
        Transformer.objects.create(resource_group=ocp_projects,
                                   attribute_definition=request_memory,
                                   consume_from_resource_group=single_vms,
                                   consume_from_attribute_definition=v_memory_attribute)
        project1 = Resource.objects.create(name="project1", resource_group=ocp_projects)
        project1.set_attribute(request_cpu, 10)
        project1.set_attribute(request_memory, 10)
