from django.contrib.auth.models import User, Permission

from profiles.models import Team, Organization, GlobalPermission, Role
from django.test.testcases import TransactionTestCase

from service_catalog.models import Instance, Request, Operation, Service, JobTemplate, TowerServer


class TestModelScopeGetQuerysetRequest(TransactionTestCase):

    def assertQuerysetEqualID(self, qs1, qs2):
        self.assertEqual(qs1.model, qs2.model)
        return self.assertListEqual(list(qs1.values_list("id", flat=True)), list(qs2.values_list("id", flat=True)))

    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@hpe.com', "password")
        self.user2 = User.objects.create_user('user2', 'user2@hpe.com', "password")
        super(TestModelScopeGetQuerysetRequest, self).setUp()

        self.role_view_request = Role.objects.create(name="View global instances")
        self.permission = "service_catalog.view_request"
        app_label, codename = self.permission.split('.')
        self.role_view_request.permissions.add(
            Permission.objects.get(content_type__app_label=app_label, content_type__model="request",
                                   codename=codename))
        self.global_perm = GlobalPermission.load()

        survey = {
            "name": "test-survey",
            "description": "test-survey-description",
            "spec": []
        }

        service = Service.objects.create(name="Service #1")
        tower = TowerServer.objects.create(name="Tower #1", host="localhost", token="xxx")

        job_template = JobTemplate.objects.create(name="Job Template #1", survey=survey,
                                                  tower_id=1,
                                                  tower_server=tower,
                                                  )

        self.operation = Operation.objects.create(name="Operation #1", service=service, job_template=job_template)

    def test_get_queryset_request_with_global_permission_role(self):
        org1 = Organization.objects.create(name="Organization #1")

        # Add instance1 in org1
        instance1 = Instance.objects.create(name="Instance #1")
        instance1.scopes.add(org1)
        Request.objects.create(instance=instance1, operation=self.operation)

        # user1 and user2 can't see any instances (no role for them)
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 0)
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # Assign view_instance to user1 in GlobalPerm
        self.global_perm.add_user_in_role(self.user1, self.role_view_request)

        # user1 can see all instances and user2 can't see anything
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 1)
        self.assertQuerysetEqualID(
            Request.get_queryset_for_user(self.user1, self.permission),
            Request.objects.all()
        )
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance2 in team1
        team1org1 = Team.objects.create(name="Team #1", org=org1)
        instance2team1org1 = Instance.objects.create(name="Instance #2")
        instance2team1org1.scopes.add(team1org1)
        Request.objects.create(instance=instance2team1org1, operation=self.operation)

        # user1 can see two instances and user2 can't see anything
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 2)
        self.assertQuerysetEqualID(
            Request.get_queryset_for_user(self.user1, self.permission),
            Request.objects.all()
        )
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance3 without scopes
        instance3 = Instance.objects.create(name="Instance #3")
        Request.objects.create(instance=instance3, operation=self.operation)

        # user1 can see three instances and user2 can't see anything
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 3)
        self.assertQuerysetEqualID(
            Request.get_queryset_for_user(self.user1, self.permission),
            Request.objects.all()
        )
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

    def test_get_queryset_request_with_organization_role(self):
        org1 = Organization.objects.create(name="Organization #1")

        # Add instance1 in org1
        instance1 = Instance.objects.create(name="Instance #1")
        instance1.scopes.add(org1)
        request1 = Request.objects.create(instance=instance1, operation=self.operation)

        # user1 and user2 can't see any instances
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 0)
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

        org1.add_user_in_role(self.user1, self.role_view_request)

        # user1 can see it and user2 can't see anything
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 1)
        self.assertQuerysetEqualID(
            Request.get_queryset_for_user(self.user1, self.permission),
            Request.objects.filter(instance__in=org1.scope_instances.all())
        )
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance2 in team2
        team1 = Team.objects.create(name="Team #1", org=org1)
        instance2 = Instance.objects.create(name="Instance #2")
        instance2.scopes.add(team1)
        request2 = Request.objects.create(instance=instance2, operation=self.operation)

        # user1 can see two instances and user2 can't see anything
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 2)
        self.assertQuerysetEqualID(
            Request.get_queryset_for_user(self.user1, self.permission),
            Request.objects.filter(instance__in=org1.scope_instances.all()) | Request.objects.filter(instance__in=team1.scope_instances.all())
        )
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance3 in team 2 org 2
        org2 = Organization.objects.create(name="Organization #2")
        team2 = Team.objects.create(name="Team #2", org=org2)
        instance3 = Instance.objects.create(name="Instance #3")
        instance3.scopes.add(team2)
        Request.objects.create(instance=instance3, operation=self.operation)

        # user1 can see two instances and user2 can't see anything (instance 3 isn't visible for them)
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 2)
        self.assertQuerysetEqualID(
            Request.get_queryset_for_user(self.user1, self.permission),
            Request.objects.filter(instance__in=org1.scope_instances.all()) | Request.objects.filter(instance__in=team1.scope_instances.all())
        )
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

    def test_get_queryset_request_with_team_role(self):
        org1 = Organization.objects.create(name="Organization #1")

        # Add instance1 in org1
        instance1 = Instance.objects.create(name="Instance #1")
        instance1.scopes.add(org1)
        Request.objects.create(instance=instance1, operation=self.operation)

        # user1 and user2 can't see any instances
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 0)
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance2 in team2
        team1 = Team.objects.create(name="Team #1", org=org1)
        instance2 = Instance.objects.create(name="Instance #2")
        instance2.scopes.add(team1)
        Request.objects.create(instance=instance2, operation=self.operation)

        # Assign view instance to user1 in team1 only
        org1.add_user_in_role(self.user1, Role.objects.create(name="Empty role"))
        team1.add_user_in_role(self.user1, self.role_view_request)

        # user1 can see instance2 only and user2 can't see anything
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 1)
        self.assertQuerysetEqualID(
            Request.get_queryset_for_user(self.user1, self.permission),
            Request.objects.filter(instance__in=team1.scope_instances.all())
        )
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)

        # instance3 in team2 in org1
        team2 = Team.objects.create(name="Team #1", org=org1)
        instance3 = Instance.objects.create(name="Instance #3")
        instance3.scopes.add(team2)
        Request.objects.create(instance=instance3, operation=self.operation)

        # user1 can see instance2 only and user2 can't see anything
        self.assertEqual(Request.get_queryset_for_user(self.user1, self.permission).count(), 1)
        self.assertQuerysetEqualID(
            Request.get_queryset_for_user(self.user1, self.permission),
            Request.objects.filter(instance__in=team1.scope_instances.all())
        )
        self.assertEqual(Request.get_queryset_for_user(self.user2, self.permission).count(), 0)
