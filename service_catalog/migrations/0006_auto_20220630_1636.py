# Generated by Django 3.2.12 on 2022-06-30 14:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_quota_quotabinding'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('service_catalog', '0005_auto_20220404_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovalStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('ALL_OF_THEM', 'All of them'), ('AT_LEAST_ONE', 'At least one')], max_length=12)),
                ('position', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='towersurveyfield',
            name='validators',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Field validators'),
        ),
        migrations.AlterField(
            model_name='supportmessage',
            name='support',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='messages', related_query_name='message', to='service_catalog.support'),
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=500)),
                ('image', models.ImageField(blank=True, upload_to='portfolio_image')),
                ('parent_portfolio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='portfolio_list', related_query_name='portfolio_list', to='service_catalog.portfolio')),
            ],
        ),
        migrations.CreateModel(
            name='ApprovalWorkflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('entry_point', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_workflow_entry', to='service_catalog.approvalstep')),
            ],
        ),
        migrations.AddField(
            model_name='approvalstep',
            name='approval_workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_step_list', to='service_catalog.approvalworkflow'),
        ),
        migrations.AddField(
            model_name='approvalstep',
            name='next',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='previous', to='service_catalog.approvalstep'),
        ),
        migrations.AddField(
            model_name='approvalstep',
            name='teams',
            field=models.ManyToManyField(related_name='approval_steps', related_query_name='approval_step', to='profiles.Team'),
        ),
        migrations.AddField(
            model_name='operation',
            name='approval_workflow',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='operation', related_query_name='operation', to='service_catalog.approvalworkflow'),
        ),
        migrations.AddField(
            model_name='request',
            name='approval_step',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requests', related_query_name='request', to='service_catalog.approvalstep'),
        ),
        migrations.AddField(
            model_name='service',
            name='parent_portfolio',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='service_list', related_query_name='service_list', to='service_catalog.portfolio'),
        ),
        migrations.CreateModel(
            name='ApprovalStepState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=10, verbose_name='Approval state')),
                ('approval_step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_step_states', related_query_name='approval_step_state', to='service_catalog.approvalstep')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_step_states', related_query_name='approval_step_state', to='service_catalog.request')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approval_step_states', related_query_name='approval_step_state', to='profiles.team')),
                ('updated_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approval_step_states', related_query_name='approval_step_state', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('request', 'approval_step', 'team')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='approvalstep',
            unique_together={('id', 'approval_workflow'), ('name', 'approval_workflow')},
        ),
    ]