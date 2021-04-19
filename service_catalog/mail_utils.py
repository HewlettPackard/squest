from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import get_template

from service_catalog import tasks
from service_catalog.models.request import RequestState

DEFAULT_FROM_EMAIL = "squest@{}".format(settings.SQUEST_HOST)


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


def send_mail_request_update(target_request, from_email=DEFAULT_FROM_EMAIL, message=None):
    """
    Notify users that a request has been updated
    :param message: A message to add to the email
    :param from_email: string email of the user who send the notification
    :param target_request:
    :type target_request: service_catalog.models.request.Request
    :return:
    """
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return

    subject = "Request #{request_id} " \
              "- {request_state} " \
              "- {operation_type} " \
              "- {operation_name} " \
              "- {instance_name}".format(request_id=target_request.id,
                                         request_state=target_request.state,
                                         operation_type=target_request.operation.type,
                                         operation_name=target_request.operation.name,
                                         instance_name=target_request.instance.name)

    if target_request.state == RequestState.SUBMITTED:
        template_name = "mails/request_submitted.html"
        plain_text = "Request update for service: {}".format(target_request.instance.name)
        context = {'request': target_request,
                   'current_site': settings.SQUEST_HOST}
    else:
        template_name = "mails/request_state_update.html"
        plain_text = "Request state update: {}".format(target_request.state)
        context = {'request': target_request,
                   'user_applied_state': from_email,
                   'current_site': settings.SQUEST_HOST,
                   'message': message}

    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_admin_emails()   # email sent to all admins
    receiver_email_list.append(target_request.user.email)   # email sent to the requester
    tasks.send_email.delay(subject, plain_text, html_content, from_email,
                           receivers=receiver_email_list,
                           reply_to=receiver_email_list)


def send_email_request_canceled(request_id, owner_email, from_email=DEFAULT_FROM_EMAIL):
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = "Request #{request_id} - CANCELLED".format(request_id=request_id)
    template_name = "mails/request_cancelled.html"
    plain_text = "Request #{request_id} - CANCELLED".format(request_id=request_id)
    context = {'request_id': request_id,
               'user_applied_state': from_email}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_admin_emails()  # email sent to all admins
    receiver_email_list.append(owner_email)  # email sent to the requester
    tasks.send_email.delay(subject, plain_text, html_content, from_email,
                           receivers=receiver_email_list,
                           reply_to=receiver_email_list)


def send_email_request_error(target_request, error_message):
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = "Request #{request_id} - ERROR".format(request_id=target_request.id)
    template_name = "mails/request_error.html"
    plain_text = "Request #{request_id} - CANCELLED".format(request_id=target_request.id)
    context = {'request': target_request,
               'user_applied_state': DEFAULT_FROM_EMAIL,
               'error_message': error_message}

    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_admin_emails()  # email sent to all admins
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           receivers=receiver_email_list,
                           reply_to=receiver_email_list)
