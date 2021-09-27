from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import get_template

from service_catalog import tasks
from service_catalog.models.request import RequestState

DEFAULT_FROM_EMAIL = f"squest@{settings.SQUEST_EMAIL_HOST}"


def _get_admin_emails():
    """
    Return a list of admin (is_staff) email
    :return:
    """
    admins = User.objects.filter(is_staff=True)
    # create a list of email
    email_admins = list()
    for admin in admins:
        email_admins.append(admin.email)
    return email_admins


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

    subject = f"Request #{target_request.id} - {target_request.state} - {target_request.operation.type} " \
              f"- {target_request.operation.name} - {target_request.instance.name}"

    if target_request.state == RequestState.SUBMITTED:
        template_name = "service_catalog/mails/request_submitted.html"
        plain_text = f"Request update for service: {target_request.instance.name}"
        context = {'request': target_request,
                   'user_applied_state': user_applied_state,
                   'current_site': settings.SQUEST_HOST}
    else:
        template_name = "service_catalog/mails/request_state_update.html"
        plain_text = f"Request state update: {target_request.state}"
        context = {'request': target_request,
                   'user_applied_state': user_applied_state,
                   'current_site': settings.SQUEST_HOST,
                   'message': message}

    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_admin_emails()   # email sent to all admins
    receiver_email_list.append(target_request.user.email)   # email sent to the requester
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           receivers=receiver_email_list,
                           reply_to=receiver_email_list)


def send_email_request_canceled(request_id, user_applied_state=None, request_owner_user=None):
    """

    :param request_id: id of the Request
    :param user_applied_state: user who called this method
    :type user_applied_state: User
    :param request_owner_user: user owner of the Request
    :type request_owner_user: User
    :return:
    """
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = f"Request #{request_id} - CANCELLED"
    plain_text = f"Request #{request_id} - CANCELLED"
    template_name = "service_catalog/mails/request_cancelled.html"
    context = {'request_id': request_id,
               'user_applied_state': user_applied_state,
               'current_site': settings.SQUEST_HOST}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_admin_emails()  # email sent to all admins
    receiver_email_list.append(request_owner_user.email)  # email sent to the requester
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           receivers=receiver_email_list,
                           reply_to=receiver_email_list)


def send_email_request_error(target_request, error_message):
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = f"Request #{target_request.id} - ERROR"
    plain_text = f"Request #{target_request.id} - CANCELLED"
    template_name = "service_catalog/mails/request_error.html"
    context = {'request': target_request,
               'user_applied_state': DEFAULT_FROM_EMAIL,
               'error_message': error_message,
               'current_site': settings.SQUEST_HOST}

    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_admin_emails()  # email sent to all admins
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           receivers=receiver_email_list,
                           reply_to=receiver_email_list)
