import base64

from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import get_template

from service_catalog import tasks
from service_catalog.models.request import RequestState

DEFAULT_FROM_EMAIL = f"squest@{settings.SQUEST_EMAIL_HOST}"
EMAIL_TITLE_PREFIX = "[Squest]"


def _get_subject(target_object):
    return f"{EMAIL_TITLE_PREFIX} {target_object.__class__.__name__} #{target_object.id} - {target_object}"


def _get_headers(subject):
    email_id = str(base64.b64encode(subject.encode()))
    headers = dict()
    headers["Message-ID"] = email_id
    headers["In-Reply-To"] = email_id
    headers["References"] = email_id
    return headers


def _get_admin_emails(service):
    """
    Return a list of admin (is_staff) email if notification is enabled and target service subscribed
    :return:
    """
    admins = User.objects.filter(is_staff=True)
    # create a list of email
    email_admins = list()
    for admin in admins:
        if admin.profile.notification_enabled:
            if service in admin.profile.subscribed_services_notification.all():
                email_admins.append(admin.email)
    return email_admins


def _get_receivers_for_request_message(request_message):
    receiver_email_list = _get_admin_emails(service=request_message.request.instance.service)
    if request_message.request.user.profile.notification_enabled and request_message.request.user.email:
        receiver_email_list.append(request_message.request.user.email)
    if request_message.sender.email in receiver_email_list:
        receiver_email_list.remove(request_message.sender.email)
    return receiver_email_list


def _get_receivers_for_support_message(support_message):
    receiver_email_list = _get_admin_emails(service=support_message.support.instance.service)
    if support_message.support.instance.spoc.profile.notification_enabled and support_message.support.instance.spoc.email:
        receiver_email_list.append(support_message.support.instance.spoc.email)
    if support_message.sender.email in receiver_email_list:
        receiver_email_list.remove(support_message.sender.email)
    return receiver_email_list


def send_mail_request_update(target_request, user_applied_state=None, message=None):
    """
    Notify users that a request has been updated
    :param message: A message to add to the email
    :param user_applied_state: string email of the user who send the notification
    :type user_applied_state: User
    :param target_request:
    :type target_request: service_catalog.models.request.Request
    :return:
    """
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return

    subject = _get_subject(target_request)
    template_name = "service_catalog/mails/request_state_update.html"

    context = {'request': target_request,
               'user_applied_state': user_applied_state,
               'current_site': settings.SQUEST_HOST,
               'message': message}
    plain_text = f"Request state update: {target_request.state}"
    if target_request.state == RequestState.SUBMITTED:
        plain_text = f"Request update for service: {target_request.instance.name}"
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_admin_emails(service=target_request.instance.service)  # email sent to all admins
    if target_request.user.profile.notification_enabled:
        receiver_email_list.append(target_request.user.email)  # email sent to the requester
    if len(receiver_email_list) > 0:
        tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                               receivers=receiver_email_list,
                               reply_to=receiver_email_list,
                               headers=_get_headers(subject))


def send_mail_new_support_message(message):
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = _get_subject(message.support)
    template_name = "service_catalog/mails/support.html"
    plain_text = f"New support message received on Instance #{message.support.instance.id} (#{message.support.id})"
    context = {'message': message, 'current_site': settings.SQUEST_HOST}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_receivers_for_support_message(message)
    if len(receiver_email_list) > 0:
        tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                               receivers=receiver_email_list,
                               reply_to=receiver_email_list,
                               headers=_get_headers(subject))


def send_mail_new_comment_on_request(message):
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = _get_subject(message.request)
    template_name = "service_catalog/mails/comment.html"
    plain_text = f"New comment received on Request #{message.request.id}"
    context = {'message': message, 'current_site': settings.SQUEST_HOST}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_receivers_for_request_message(message)
    if len(receiver_email_list) > 0:
        tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                               receivers=receiver_email_list,
                               reply_to=receiver_email_list,
                               headers=_get_headers(subject))


def send_email_request_canceled(target_request, user_applied_state=None, request_owner_user=None):
    """
    :param target_request: Request model
    :type target_request: service_catalog.models.request.Request
    :param user_applied_state: user who called this method
    :type user_applied_state: User
    :param request_owner_user: user owner of the Request
    :type request_owner_user: User
    :return:
    """
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = _get_subject(target_request)
    plain_text = f"Request #{target_request.id} - CANCELLED"
    template_name = "service_catalog/mails/request_cancelled.html"
    context = {'request_id': target_request.id,
               'user_applied_state': user_applied_state,
               'current_site': settings.SQUEST_HOST}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_admin_emails(service=target_request.instance.service)  # email sent to all admins
    if request_owner_user.profile.notification_enabled:
        receiver_email_list.append(request_owner_user.email)  # email sent to the requester
    if len(receiver_email_list) > 0:
        tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                               receivers=receiver_email_list,
                               reply_to=receiver_email_list,
                               headers=_get_headers(subject))
