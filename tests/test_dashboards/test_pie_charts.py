from django.contrib.auth.models import User

from profiles.models import BillingGroup
from resource_tracker.models import ResourcePool, ResourceGroup
from service_catalog.models import Request, Service, Instance, JobTemplate, TowerServer
from service_catalog.models.operations import Operation
from service_catalog.models.request import RequestState
from service_catalog.views import create_pie_chart_instance_by_service_type, create_pie_chart_request_by_state, \
    create_pie_chart_instance_by_billing_groups, create_pie_chart_resource_pool_consumption_by_billing_groups
from tests.base import BaseTest


class TestPieChart(BaseTest):

    def setUp(self):
        super(TestPieChart, self).setUp()
        # Billing Groups
        self.billing_groups = {'5G': None, 'Assurance': None, 'Orchestration': None, "SharedInfra": None}
        for billing_group in self.billing_groups:
            self.billing_groups[billing_group] = BillingGroup.objects.create(name=billing_group)

        # Users
        user1 = User.objects.create_user('OrchestrationGuy', 'OrchestrationGuy@hpe.com', self.common_password)
        user2 = User.objects.create_user('AssuranceGuy', 'AssuranceGuy@hpe.com', self.common_password)
        user3 = User.objects.create_user('SharedInfraGuy', 'SharedInfraGuy@hpe.com', self.common_password)

        # Add users in Billing Groups
        self.billing_groups['Orchestration'].user_set.add(user1)
        self.billing_groups['Assurance'].user_set.add(user2)
        self.billing_groups['SharedInfra'].user_set.add(user3)

        # Tower server + Job template
        tower_server = TowerServer.objects.create(name="Tower test", host="awx.hpe.com", token="TOKEN")
        job_template = JobTemplate.objects.create(name='Job template', tower_id=1, tower_server=tower_server)

        # Services + Operation
        self.services = dict()
        self.services['vmware_service'], _ = Service.objects.get_or_create(name="VMWare")
        Operation.objects.create(name=self.services['vmware_service'].name,
                                 service=self.services['vmware_service'],
                                 job_template=job_template)
        self.services['OCP_service'], _ = Service.objects.get_or_create(name="OCP")
        Operation.objects.create(name=self.services['OCP_service'].name,
                                 service=self.services['OCP_service'],
                                 job_template=job_template)
        self.services['K8S_service'], _ = Service.objects.get_or_create(name="K8S")
        Operation.objects.create(name=self.services['K8S_service'].name,
                                 service=self.services['K8S_service'],
                                 job_template=job_template)

        # Instance + Request
        instances = list()
        service = self.services['vmware_service']
        billing_group = self.billing_groups['Orchestration']
        name = "my VM"
        user = user1
        state = RequestState.ACCEPTED
        for i in range(7):
            instance = Instance.objects.create(service=None, name=name,
                                               billing_group=billing_group)
            Request.objects.create(instance=instance, state=state, user=user,
                                   operation=service.operations.first())
            instances.append(instance)
        service = self.services['OCP_service']
        billing_group = self.billing_groups['Assurance']
        name = "my OCP"
        user = user2
        state = RequestState.FAILED
        for i in range(5):
            instance = Instance.objects.create(service=service, name=name,
                                               billing_group=billing_group)
            Request.objects.create(instance=instance, state=state, user=user,
                                   operation=service.operations.first())
            instances.append(instance)

        service = self.services['K8S_service']
        billing_group = self.billing_groups['SharedInfra']
        name = "my K8S"
        user = user3
        state = RequestState.COMPLETE
        for i in range(3):
            instance = Instance.objects.create(service=service, name=name,
                                               billing_group=billing_group)
            Request.objects.create(instance=instance, state=state, user=user,
                                   operation=service.operations.first())
            instances.append(instance)

        # Resource Group
        # create resource pools
        self.vcenter_pool = ResourcePool.objects.create(name="G5 vcenter")
        self.vcenter_vcpu = self.vcenter_pool.add_attribute_definition(name='vCPU')
        self.vcenter_memory = self.vcenter_pool.add_attribute_definition(name='Memory')

        # resource
        server_group = ResourceGroup.objects.create(name="Gen10")
        server_group_cpu_attribute = server_group.add_attribute_definition(name="CPU")
        server_group_memory_attribute = server_group.add_attribute_definition(name="Memory")
        ocp_worker_node_group = ResourceGroup.objects.create(name="OCP Worker node")
        ocp_worker_node_group_vcpu_attribute = ocp_worker_node_group.add_attribute_definition(name="vCPU")
        ocp_worker_node_group_memory_attribute = ocp_worker_node_group.add_attribute_definition(name="Memory")

        # Links
        self.vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_producers(server_group.attribute_definitions.get(name='CPU'))
        self.vcenter_pool.attribute_definitions.get(name='Memory') \
            .add_producers(server_group.attribute_definitions.get(name='Memory'))
        self.vcenter_pool.attribute_definitions.get(name='vCPU') \
            .add_consumers(ocp_worker_node_group.attribute_definitions.get(name='vCPU'))
        self.vcenter_pool.attribute_definitions.get(name='Memory') \
            .add_consumers(ocp_worker_node_group.attribute_definitions.get(name='Memory'))

        # Instances
        cpu_list = [30, 40, 50, 100]
        memory_list = [100, 120, 150, 200]
        for i in range(4):
            server = server_group.create_resource(name=f"server-{i}")
            server.set_attribute(server_group_cpu_attribute, cpu_list[i])
            server.set_attribute(server_group_memory_attribute, memory_list[i])
        for i, instance in enumerate(instances):
            worker_node = ocp_worker_node_group.create_resource(name=f"worker{i}")
            worker_node.set_attribute(ocp_worker_node_group_vcpu_attribute, 16)
            worker_node.set_attribute(ocp_worker_node_group_memory_attribute, 32)
            worker_node.service_catalog_instance = instance
            worker_node.save()

    def test_create_pie_chart_instance_by_service_type(self):
        # This test may fail if we add Meta: ordering. Please update expected data
        data = create_pie_chart_instance_by_service_type()
        expected_data = {'title': 'Instance by service type', 'id': 'pie-chart-service',
                         'data': {'labels': ['No service', 'OCP', 'K8S'],
                                  'datasets': [{'data': [7, 5, 3]}]}}
        self.assertEqual(data.get('title'), expected_data.get('title'))
        self.assertEqual(data.get('id'), expected_data.get('id'))
        self.assertListEqual(data.get('data').get('labels'), expected_data.get('data').get('labels'))
        self.assertListEqual(data.get('data').get('datasets')[0].get('data'),
                             expected_data.get('data').get('datasets')[0].get('data'))

    def test_create_pie_chart_request_by_state(self):
        # This test may fail if we add Meta: ordering. Please update expected data

        data = create_pie_chart_request_by_state()
        expected_data = {'title': 'Request by state', 'id': 'pie-chart-state',
                         'data': {'labels': ['ACCEPTED', 'FAILED', 'COMPLETE'], 'datasets': [
                             {'data': [7, 5, 3]}]}}

        self.assertEqual(data.get('title'), expected_data.get('title'))
        self.assertEqual(data.get('id'), expected_data.get('id'))
        self.assertListEqual(data.get('data').get('labels'), expected_data.get('data').get('labels'))
        self.assertListEqual(data.get('data').get('datasets')[0].get('data'),
                             expected_data.get('data').get('datasets')[0].get('data'))

    def test_create_pie_chart_instance_by_billing_groups(self):
        # This test may fail if we add Meta: ordering. Please update expected data
        data = create_pie_chart_instance_by_billing_groups()
        expected_data = {'title': 'Instance by billing', 'id': 'pie-chart-instance-billing',
                         'data': {'labels': ['Orchestration', 'Assurance', 'SharedInfra'], 'datasets': [
                             {'data': [7, 5, 3]}]}}

        self.assertEqual(data.get('title'), expected_data.get('title'))
        self.assertEqual(data.get('id'), expected_data.get('id'))
        self.assertListEqual(data.get('data').get('labels'), expected_data.get('data').get('labels'))
        self.assertListEqual(data.get('data').get('datasets')[0].get('data'),
                             expected_data.get('data').get('datasets')[0].get('data'))

    def test_create_pie_chart_resource_pool_consumption_by_billing_groups(self):
        print(BillingGroup.objects.all())

        data = create_pie_chart_resource_pool_consumption_by_billing_groups()
        from pprint import pprint
        pprint(data)
        expected_data = {
            self.vcenter_pool: {
                self.vcenter_vcpu: {
                    'data': {
                        'datasets': [{'data': [80, 112, 48]}],
                        'labels': ['Assurance', 'Orchestration', 'SharedInfra']},
                    'id': f"pie-chart-{self.vcenter_pool.id}-{self.vcenter_vcpu.id}",
                    'title': f"{self.vcenter_vcpu}"},
                self.vcenter_memory: {
                    'data': {
                        'datasets': [{'data': [160, 224, 96]}],
                        'labels': ['Assurance', 'Orchestration', 'SharedInfra']},
                    'id': f"pie-chart-{self.vcenter_pool.id}-{self.vcenter_memory.id}",
                    'title': f"{self.vcenter_memory}"},
            }
        }
        # CPU
        self.assertListEqual(
            data.get(self.vcenter_pool).get(self.vcenter_vcpu).get('data').get('datasets')[0].get('data'),
            expected_data.get(self.vcenter_pool).get(self.vcenter_vcpu).get('data').get('datasets')[0].get('data')
        )
        self.assertListEqual(
            data.get(self.vcenter_pool).get(self.vcenter_vcpu).get('data').get('labels'),
            expected_data.get(self.vcenter_pool).get(self.vcenter_vcpu).get('data').get('labels')
        )
        self.assertEqual(
            data.get(self.vcenter_pool).get(self.vcenter_vcpu).get('id'),
            expected_data.get(self.vcenter_pool).get(self.vcenter_vcpu).get('id')
        )

        self.assertEqual(
            data.get(self.vcenter_pool).get(self.vcenter_vcpu).get('title'),
            expected_data.get(self.vcenter_pool).get(self.vcenter_vcpu).get('title')
        )
        # Memory
        self.assertListEqual(
            data.get(self.vcenter_pool).get(self.vcenter_memory).get('data').get('datasets')[0].get('data'),
            expected_data.get(self.vcenter_pool).get(self.vcenter_memory).get('data').get('datasets')[0].get('data')
        )
        self.assertListEqual(
            data.get(self.vcenter_pool).get(self.vcenter_memory).get('data').get('labels'),
            expected_data.get(self.vcenter_pool).get(self.vcenter_memory).get('data').get('labels')
        )
        self.assertEqual(
            data.get(self.vcenter_pool).get(self.vcenter_memory).get('id'),
            expected_data.get(self.vcenter_pool).get(self.vcenter_memory).get('id')
        )

        self.assertEqual(
            data.get(self.vcenter_pool).get(self.vcenter_memory).get('title'),
            expected_data.get(self.vcenter_pool).get(self.vcenter_memory).get('title')
        )