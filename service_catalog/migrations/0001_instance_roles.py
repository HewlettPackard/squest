from django.db import migrations
from profiles.migrations import _rbac as rbac


class Migration(migrations.Migration):

    dependencies = [
        ('service_catalog', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(rbac.create_roles),
    ]
