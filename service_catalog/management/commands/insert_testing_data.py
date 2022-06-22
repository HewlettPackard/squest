import logging
import os
import random

from django.contrib.auth.models import User
from django.core.management import BaseCommand

from profiles.models import BillingGroup, Team
from resource_tracker.models import ResourceGroup, ResourcePool
from service_catalog.models import TowerServer, JobTemplate, Service, Operation, Instance, Request, ApprovalWorkflow, \
    ApprovalStep
from service_catalog.models.approval_step_type import ApprovalStepType
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
                users[username] = User.objects.create_user(username=username, password="admin", is_staff=True, is_superuser=True)
            team = Team.objects.create(name=username)
            team.add_user_in_role(users[username], "Admin")
            logger.info(f"Get or create '{users[username]}'")
        anthony_token = os.environ['AWX_TOKEN']
        tower, _ = TowerServer.objects.get_or_create(name=r'AWX HPE', host=r'awx.gre.hpecorp.net:8043',
                                                     token=anthony_token)
        logger.info('AWX added')
        print('Launch celery to sync: celery - A service_catalog worker - l info')
        tower.sync()

        billing_groups_name = ['5G', 'Assurance', 'Orchestration']
        billing_groups = []
        for billing_group in billing_groups_name:
            billing_groups.append(BillingGroup.objects.get_or_create(name=billing_group)[0])

        approval_workflow = ApprovalWorkflow.objects.create(name='testing AW')
        approval_step_3 = ApprovalStep.objects.create(
            name="Third",
            type=ApprovalStepType.ALL_OF_THEM,
            approval_workflow=approval_workflow
        )
        approval_step_3.teams.set(Team.objects.filter(id__lt=3))
        approval_step_2 = ApprovalStep.objects.create(
            name="Second",
            type=ApprovalStepType.ALL_OF_THEM,
            next=approval_step_3,
            approval_workflow=approval_workflow
        )
        approval_step_2.teams.set(Team.objects.filter(id__gt=4, id__lt=7))
        approval_step_1 = ApprovalStep.objects.create(
            name="First",
            type=ApprovalStepType.AT_LEAST_ONE,
            next=approval_step_2,
            approval_workflow=approval_workflow
        )
        approval_step_1.teams.set(Team.objects.filter(id__gt=2, id__lt=5))
        approval_workflow.entry_point = approval_step_1
        approval_workflow.save()
        job_templates = JobTemplate.objects.all()
        services = dict()
        services['vmware_service'], _ = Service.objects.get_or_create(name="VMWare")

        services['OCP_service'], _ = Service.objects.get_or_create(name="OCP")

        services['K8S_service'], _ = Service.objects.get_or_create(name="K8S")
        for service_name in services:
            service = services[service_name]
            Operation.objects.get_or_create(name=service.name,
                                            service=service,
                                            job_template=job_templates[1],
                                            approval_workflow=approval_workflow)
            Operation.objects.get_or_create(name="Delete my resource",
                                            type=OperationType.DELETE,
                                            service=service,
                                            job_template=job_templates[1])
            states = [RequestState.SUBMITTED, RequestState.FAILED, RequestState.ACCEPTED, RequestState.NEED_INFO,
                      RequestState.REJECTED, RequestState.CANCELED, RequestState.PROCESSING, RequestState.COMPLETE]
            for i in range(random.randint(1, 3)):
                for username in users:
                    if random.randint(0, 2) == 1:
                        continue
                    user = users[username]
                    new_instance = Instance.objects.create(service=service, name=f"Instance - {username} - {i}",
                                                           billing_group=random.choice(billing_groups), spoc=user)
                    # create the request
                    new_request, _ = Request.objects.get_or_create(instance=new_instance,
                                                                   operation=service.operations.filter(
                                                                       type=OperationType.CREATE)[0],
                                                                   state=random.choice(states),
                                                                   fill_in_survey=dict(),
                                                                   user=user)

        # create resource pools
        vcenter_pool = ResourcePool.objects.create(name="G5 vcenter")
        vcenter_pool.add_attribute_definition(name='vCPU')
        vcenter_pool.add_attribute_definition(name='Memory')
        ocp_pool = ResourcePool.objects.create(name="ocp4-02 projects")
        ocp_pool.add_attribute_definition(name='requests.cpu')
        ocp_pool.add_attribute_definition(name='requests.memory')
        # resource
        server_group = ResourceGroup.objects.create(name="Gen10")
        server_group_cpu_attribute = server_group.add_attribute_definition(name="CPU")
        server_group_memory_attribute = server_group.add_attribute_definition(name="Memory")
        ocp_worker_node_group = ResourceGroup.objects.create(name="OCP Worker node")
        ocp_worker_node_group_vcpu_attribute = ocp_worker_node_group.add_attribute_definition(name="vCPU")
        ocp_worker_node_group_memory_attribute = ocp_worker_node_group.add_attribute_definition(name="Memory")
        ocp_worker_node_group.add_text_attribute_definition(name="Comments")
        ocp_project_group = ResourceGroup.objects.create(name="OCP Project")
        ocp_project_group_cpu_att = ocp_project_group.add_attribute_definition(name="requests.cpu")
        ocp_project_group_mem_att = ocp_project_group.add_attribute_definition(name="requests.memory")
        # Links
        vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(server_group.attribute_definitions.get(name='CPU'))
        vcenter_pool.attribute_definitions.get(name='Memory') \
            .add_producers(server_group.attribute_definitions.get(name='Memory'))
        vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_consumers(ocp_worker_node_group.attribute_definitions.get(name='vCPU'))
        vcenter_pool.attribute_definitions.get(name='Memory') \
            .add_consumers(ocp_worker_node_group.attribute_definitions.get(name='Memory'))

        ocp_pool.attribute_definitions.get(name='requests.cpu') \
            .add_producers(ocp_worker_node_group.attribute_definitions.get(name='vCPU'))
        ocp_pool.attribute_definitions.get(name='requests.memory') \
            .add_producers(ocp_worker_node_group.attribute_definitions.get(name='Memory'))
        ocp_pool.attribute_definitions.get(name='requests.cpu') \
            .add_consumers(ocp_project_group.attribute_definitions.get(name='requests.cpu'))
        ocp_pool.attribute_definitions.get(name='requests.memory') \
            .add_consumers(ocp_project_group.attribute_definitions.get(name='requests.memory'))

        # Instances
        cpu_list = [30, 40, 50, 100]
        memory_list = [100, 120, 150, 200]
        for i in range(4):
            server = server_group.create_resource(name=f"server-{i}")
            server.set_attribute(server_group_cpu_attribute, cpu_list[i])
            server.set_attribute(server_group_memory_attribute, memory_list[i])
        for i in range(3):
            worker_node = ocp_worker_node_group.create_resource(name=f"worker{i}")
            worker_node.set_attribute(ocp_worker_node_group_vcpu_attribute, 16)
            worker_node.set_attribute(ocp_worker_node_group_memory_attribute, 32)
            worker_node.service_catalog_instance = Instance.objects.order_by("?").first()
        for i in range(5):
            new_ocp_project = ocp_project_group.create_resource(name=f"project-{i}")
            new_ocp_project.set_attribute(ocp_project_group_cpu_att, random.randint(8, 32))
            new_ocp_project.set_attribute(ocp_project_group_mem_att, random.randint(8, 32))
            new_ocp_project.service_catalog_instance = Instance.objects.order_by("?").first()
