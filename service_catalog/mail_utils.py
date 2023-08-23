import base64
import logging

from os import linesep

from django.conf import settings
from django.contrib.auth.models import User
from django.template.loader import get_template

from service_catalog import tasks
from service_catalog.models.request import RequestState

DEFAULT_FROM_EMAIL = f"{settings.SQUEST_EMAIL_HOST}"
EMAIL_TITLE_PREFIX = "[Squest]"

logger = logging.getLogger(__name__)


def _get_subject(target_object):
    return f"{EMAIL_TITLE_PREFIX} {target_object.__class__.__name__} #{target_object.id} - {target_object}"


def _get_headers(subject):
    email_id = str(base64.b64encode(subject.encode()))
    headers = dict()
    headers["Message-ID"] = email_id
    headers["In-Reply-To"] = email_id
    headers["References"] = email_id
    return headers


def _exclude_user_without_email(user_qs):
    if user_qs.filter(email='').exists():
        logger.warning(f'The following users have no email:\n'
                       f'{linesep.join(f" - {user.username}" for user in user_qs.filter(email=""))}')
    return user_qs.exclude(email='')


def _apply_when_filter_instance(user_qs, squest_object):
    user_emails = list()
    user_qs = _exclude_user_without_email(user_qs)
    if user_qs.filter(profile__instance_notification_enabled=False).exists():
        logger.warning(f'The following users have no instance notification enabled:\n'
                       f'{linesep.join(f" - {user.username}" for user in user_qs.filter(profile__instance_notification_enabled=False))}')
    for user in user_qs.exclude(profile__instance_notification_enabled=False):
        if user.profile.is_notification_authorized_for_instance(squest_object):
            user_emails.append(user.email)
    return user_emails


def _apply_when_filter_request(user_qs, squest_object):
    user_emails = list()
    user_qs = _exclude_user_without_email(user_qs)
    if user_qs.filter(profile__request_notification_enabled=False).exists():
        logger.warning(f'The following users have no request notification enabled:'
                       f'{linesep.join(user.username for user in user_qs.filter(profile__request_notification_enabled=False))}')
    for user in user_qs.exclude(profile__request_notification_enabled=False):
        if user.profile.is_notification_authorized_for_request(squest_object):
            user_emails.append(user.email)
    return user_emails


def _get_receivers_for_support_message(support_message):
    ## Apply when filter on all users
    receivers_raw = support_message.who_has_perm("service_catalog.view_supportmessage").exclude(
        id=support_message.sender.id)
    return _apply_when_filter_instance(receivers_raw, support_message.support.instance)


def _get_receivers_for_request_message(request_message):
    ## Apply when filter on all users
    receivers_raw = request_message.who_has_perm("service_catalog.view_requestmessage").exclude(
        id=request_message.sender.id)
    return _apply_when_filter_request(receivers_raw, request_message.request)


def _get_receivers_for_support(support):
    ## Apply when filter on all users

    receivers_raw = support.who_has_perm("service_catalog.view_support")
    return _apply_when_filter_instance(receivers_raw, support.instance)


def _get_receivers_for_request(squest_request):
    ## Apply when filter on all users
    customer_raw = squest_request.who_has_perm("service_catalog.view_request")
    admin_raw = squest_request.who_can_accept()
    return _apply_when_filter_request(customer_raw | admin_raw, squest_request)


def send_mail_request_update(target_request, user_applied_state=None, message=None, receiver_email_list=None,
                             plain_text=None):
    """
    Notify users that a request has been updated
    :param message: A message to add to the email
    :param user_applied_state: string email of the user who send the notification
    :type user_applied_state: User
    :param target_request:
    :type target_request: service_catalog.models.request.Request
    :param receiver_email_list: email diffusion list
    :type receiver_email_list: List
    :param plain_text: text displayed in the mail
    :type plain_text: String
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
    if plain_text is None:
        plain_text = f"Request state update: {target_request.state}"
        if target_request.state == RequestState.SUBMITTED:
            plain_text = f"Request update for service: {target_request.instance.name}"
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    if receiver_email_list is None:
        receiver_email_list = _get_receivers_for_request(target_request)
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
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
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
                           headers=_get_headers(subject))


def send_mail_support_is_closed(support):
    if not settings.SQUEST_EMAIL_NOTIFICATION_ENABLED:
        return
    subject = _get_subject(support)
    template_name = "service_catalog/mails/closed_support.html"
    plain_text = f"Support closed on Instance #{support.instance.id} (#{support.id})"
    context = {'support': support, 'current_site': settings.SQUEST_HOST}
    html_template = get_template(template_name)
    html_content = html_template.render(context)
    receiver_email_list = _get_receivers_for_support(support)
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
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
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
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
    receiver_email_list = _get_receivers_for_request(target_request)
    tasks.send_email.delay(subject, plain_text, html_content, DEFAULT_FROM_EMAIL,
                           bcc=receiver_email_list,
                           headers=_get_headers(subject))
