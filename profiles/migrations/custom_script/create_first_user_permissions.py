default_user_permissions = [
    # Lists
    'service_catalog.list_instance',
    'service_catalog.list_request',
    'service_catalog.list_support',
    'profiles.list_organization',
    'profiles.list_team',
    # Custom link
    'service_catalog.view_customlink',
    # Doc
    'service_catalog.list_doc',
    'service_catalog.view_doc',
    # Portfolio
    'service_catalog.list_portfolio',
    'service_catalog.view_portfolio',
    # Service
    'service_catalog.list_service',
    'service_catalog.view_service',
    # Operation
    'service_catalog.list_operation',
    'service_catalog.view_operation',
    'service_catalog.request_on_service',
    # Request notification
    'profiles.list_requestnotification',
    'profiles.add_requestnotification',
    'profiles.view_requestnotification',
    'profiles.change_requestnotification',
    'profiles.delete_requestnotification',
    # Instance notification
    'profiles.list_instancenotification',
    'profiles.add_instancenotification',
    'profiles.view_instancenotification',
    'profiles.change_instancenotification',
    'profiles.delete_instancenotification',
]


def insert_default_user_permissions(apps, schema_editor):
    GlobalPermission = apps.get_model('profiles', 'GlobalPermission')
    Permission = apps.get_model('auth', 'Permission')
    global_permission, created = GlobalPermission.objects.get_or_create(name="GlobalPermission")
    codenames = list(
        map(lambda user_permissions: user_permissions.split('.')[1], default_user_permissions))
    app_labels = list(
        map(lambda user_permissions: user_permissions.split('.')[0], default_user_permissions))
    global_permission.user_permissions.add(
        *Permission.objects.filter(
            codename__in=codenames,
            content_type__app_label__in=app_labels
        )
    )
