from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.safestring import mark_safe

from service_catalog.forms import AnnouncementForm
from service_catalog.models.announcement import Announcement


@user_passes_test(lambda u: u.is_superuser)
def announcement_list(request):
    return render(request, 'service_catalog/settings/announcements/announcement-list.html',
                  {'announcements': Announcement.objects.all()})


@user_passes_test(lambda u: u.is_superuser)
def announcement_create(request):
    if request.method == 'POST':
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save()
            announcement.created_by = request.user
            announcement.save()
            return redirect('service_catalog:announcement_list')
    else:
        form = AnnouncementForm()
    breadcrumbs = [
        {'text': 'Announcement', 'url': reverse('service_catalog:announcement_list')},
        {'text': "Create a new announcement", 'url': ""}
    ]
    context = {'form': form, 'breadcrumbs': breadcrumbs, 'action': 'create'}
    return render(request, 'service_catalog/settings/announcements/announcement-create.html', context)


@user_passes_test(lambda u: u.is_superuser)
def announcement_edit(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    form = AnnouncementForm(request.POST or None, instance=announcement)
    if form.is_valid():
        announcement = form.save()
        announcement.created_by = request.user
        announcement.save()
        return redirect('service_catalog:announcement_list')
    breadcrumbs = [
        {'text': 'Announcement', 'url': reverse('service_catalog:announcement_list')},
        {'text': announcement.title, 'url': ""}
    ]
    context = {'form': form,
               'announcement': announcement,
               'breadcrumbs': breadcrumbs,
               'action': 'edit'
               }
    return render(request, 'service_catalog/settings/announcements/announcement-edit.html', context=context)


@user_passes_test(lambda u: u.is_superuser)
def announcement_delete(request, announcement_id):
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == "POST":
        announcement.delete()
        return redirect('service_catalog:announcement_list')
    breadcrumbs = [
        {'text': 'Announcement', 'url': reverse('service_catalog:announcement_list')},
        {'text': announcement.title, 'url': ""}
    ]
    template_form = {'confirm_text': mark_safe(f"Confirm deletion of <strong>{announcement.title}</strong>?"),
            'button_text': 'Delete',
            'details': {'warning_sentence': 'Warning: this announcement is displayed',
                        'details_list': None
                        } if announcement.date_start < timezone.now() < announcement.date_stop else None}
    context = {
        'breadcrumbs': breadcrumbs,
        'template_form': template_form
    }
    return render(request, "generics/confirm-delete-template.html", context=context)
