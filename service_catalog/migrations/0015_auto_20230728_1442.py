# Generated by Django 3.2.13 on 2023-07-28 12:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('profiles', '0017_auto_20230724_2058'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('service_catalog', '0014_auto_20230622_1722'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovalStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('position', models.IntegerField(blank=True, default=0, null=True)),
            ],
            options={
                'permissions': [('approve_approvalstep', 'Can approve an approval step')],
            },
        ),
        migrations.CreateModel(
            name='ApprovalStepState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10, verbose_name='Approval state')),
                ('date_updated', models.DateTimeField(blank=True, null=True)),
                ('fill_in_survey', models.JSONField(blank=True, default=dict)),
                ('approval_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_step_states', related_query_name='approval_step_state', to='service_catalog.approvalstep')),
            ],
        ),
        migrations.CreateModel(
            name='ApprovalWorkflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view', 'list'),
            },
        ),
        migrations.CreateModel(
            name='ApprovalWorkflowState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_workflow', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_workflow_states', related_query_name='approval_workflow_state', to='service_catalog.approvalworkflow')),
                ('current_step', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_approval_workflow_states', related_query_name='current_approval_workflow_state', to='service_catalog.approvalstepstate')),
            ],
            options={
                'abstract': False,
                'default_permissions': ('add', 'change', 'delete', 'view', 'list'),
            },
        ),
        migrations.AlterModelOptions(
            name='announcement',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list'), 'ordering': ['-date_created']},
        ),
        migrations.AlterModelOptions(
            name='credential',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='customlink',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list'), 'permissions': [('view_admin_customlink', 'Can view admin custom link')]},
        ),
        migrations.AlterModelOptions(
            name='doc',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='globalhook',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='instance',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list'), 'permissions': [('archive_instance', 'Can archive instance'), ('unarchive_instance', 'Can unarchive instance'), ('request_on_instance', 'Can request a day2 operation on instance'), ('admin_request_on_instance', 'Can request an admin day2 operation on instance'), ('view_admin_spec_instance', 'Can view admin spec on instance'), ('change_admin_spec_instance', 'Can change admin spec on instance')]},
        ),
        migrations.AlterModelOptions(
            name='inventory',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='jobtemplate',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='operation',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='portfolio',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='request',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list'), 'permissions': [('accept_request', 'Can accept request'), ('cancel_request', 'Can cancel request'), ('reject_request', 'Can reject request'), ('archive_request', 'Can archive request'), ('unarchive_request', 'Can unarchive request'), ('re_submit_request', 'Can re-submit request'), ('process_request', 'Can process request'), ('need_info_request', 'Can ask info request')]},
        ),
        migrations.AlterModelOptions(
            name='requestmessage',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list'), 'permissions': [('request_on_service', 'Can request operation on service'), ('admin_request_on_service', 'Can request an admin operation on service')]},
        ),
        migrations.AlterModelOptions(
            name='support',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='supportmessage',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.AlterModelOptions(
            name='towerserver',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list'), 'permissions': [('sync_towerserver', 'Can sync AAP/AWX')]},
        ),
        migrations.AlterModelOptions(
            name='towersurveyfield',
            options={'default_permissions': ('add', 'change', 'delete', 'view', 'list')},
        ),
        migrations.RenameField(
            model_name='towersurveyfield',
            old_name='enabled',
            new_name='is_customer_field',
        ),
        migrations.AlterField(
            model_name='customlink',
            name='is_admin_only',
            field=models.BooleanField(default=False, help_text='If "is admin only" then permission service_catalog.view_admin_custom_link is required to see it in your instances'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='quota_scope',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='quota_instances', related_query_name='quota_instance', to='profiles.scope'),
        ),
        migrations.AlterField(
            model_name='instance',
            name='requester',
            field=models.ForeignKey(help_text='Initial requester', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Requester'),
        ),
        migrations.AlterField(
            model_name='operation',
            name='is_admin_operation',
            field=models.BooleanField(blank=True, default=False, help_text='Create operations are protected by "service_catalog.admin_request_on_service", others by "service_catalog.admin_request_on_instance".', verbose_name='Admin operation'),
        ),
        migrations.DeleteModel(
            name='ServiceStateHook',
        ),
        migrations.AddField(
            model_name='approvalworkflow',
            name='operation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_workflows', related_query_name='approval_workflow', to='service_catalog.operation'),
        ),
        migrations.AddField(
            model_name='approvalworkflow',
            name='scopes',
            field=models.ManyToManyField(blank=True, related_name='approval_workflows', to='profiles.Scope', verbose_name='Restricted scopes'),
        ),
        migrations.AddField(
            model_name='approvalstepstate',
            name='approval_workflow_state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_step_states', related_query_name='approval_step_state', to='service_catalog.approvalworkflowstate'),
        ),
        migrations.AddField(
            model_name='approvalstepstate',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_step_states', related_query_name='approval_step_state', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='approvalstep',
            name='approval_workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_steps', to='service_catalog.approvalworkflow'),
        ),
        migrations.AddField(
            model_name='approvalstep',
            name='editable_fields',
            field=models.ManyToManyField(blank=True, help_text='Fields allowed to be filled', related_name='approval_steps_as_write_field', to='service_catalog.TowerSurveyField'),
        ),
        migrations.AddField(
            model_name='approvalstep',
            name='next',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='previous', to='service_catalog.approvalstep'),
        ),
        migrations.AddField(
            model_name='approvalstep',
            name='permission',
            field=models.ForeignKey(limit_choices_to={'content_type__app_label': 'service_catalog', 'content_type__model': 'approvalstep'}, on_delete=django.db.models.deletion.PROTECT, related_name='previous', to='auth.permission'),
        ),
        migrations.AddField(
            model_name='approvalstep',
            name='readable_fields',
            field=models.ManyToManyField(blank=True, help_text='Read only field', related_name='approval_steps_as_read_field', to='service_catalog.TowerSurveyField'),
        ),
        migrations.AddField(
            model_name='request',
            name='approval_workflow_state',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='service_catalog.approvalworkflowstate'),
        ),
        migrations.AlterUniqueTogether(
            name='approvalstepstate',
            unique_together={('approval_workflow_state', 'approval_step')},
        ),
        migrations.AlterUniqueTogether(
            name='approvalstep',
            unique_together={('name', 'approval_workflow'), ('id', 'approval_workflow')},
        ),
    ]
