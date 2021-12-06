from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from profiles.models import UserRoleBinding, TeamRoleBinding, Team


@login_required
def ajax_get_users_with_role(request):
    role_id = request.GET.get('role_id')
    content_type_id = request.GET.get('content_type_id')
    object_id = request.GET.get('object_id')
    bindings = UserRoleBinding.objects.filter(role__id=role_id, content_type__id=content_type_id, object_id=object_id)
    selected = [binding.user.id for binding in bindings]
    return render(request, 'profiles/role/users-dropdown-list.html',
                  {'users': User.objects.all(), 'selected': selected})

@login_required
def ajax_get_teams_with_role(request):
    role_id = request.GET.get('role_id')
    content_type_id = request.GET.get('content_type_id')
    object_id = request.GET.get('object_id')
    bindings = TeamRoleBinding.objects.filter(role__id=role_id, content_type__id=content_type_id, object_id=object_id)
    selected = [binding.user.id for binding in bindings]
    return render(request, 'profiles/role/teams-dropdown-list.html',
                  {'teams': Team.objects.all(), 'selected': selected})
