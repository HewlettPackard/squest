# Generated by Django 3.2.13 on 2023-09-27 08:53

from django.db import migrations


def update_requests(apps, schema_editor):
    Request = apps.get_model('service_catalog', 'Request')
    for request in Request.objects.all():
        Request.objects.filter(pk=request.pk).update(created=request.date_submitted,
                                                     last_updated=request.date_submitted)
        from service_catalog.models import RequestState
        if request.state == RequestState.COMPLETE:
            Request.objects.filter(pk=request.pk).update(last_updated=request.date_complete)


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0027_alter_approvalworkflow_scopes'),
    ]

    operations = [
        migrations.RunPython(update_requests),
    ]
