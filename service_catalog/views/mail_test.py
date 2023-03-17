from django.shortcuts import render

from Squest import settings
from service_catalog.models import Instance, Request, RequestMessage


def mail_test(request):
    """
    view used to dev the mail template
    """
    message = RequestMessage(content="test")
    context = {
        'request': Request.objects.get(id=1),
        'current_site': settings.SQUEST_HOST,
        'message': message,
        'user_applied_state': {
            'username': "nico"
        }
    }
    return render(request, "service_catalog/mails/request_state_update.html", context)

    # test request canceled
    # context = {
    #     'request_id': 2,
    #     'current_site': settings.SQUEST_HOST,
    #     'user_applied_state': {
    #         'username': "nico"
    #     }
    # }
    # return render(request, "service_catalog/mails/request_cancelled.html", context)

    # comment
    # message = {
    #     "request": {
    #         "id": 12
    #     },
    #     "content": "message",
    #     "sender": {"username": "test@hpe.com"}
    # }
    # context = {
    #     'request': Request.objects.get(id=1),
    #     'current_site': settings.SQUEST_HOST,
    #     'message': message,
    # }
    # return render(request, "service_catalog/mails/comment.html", context)

    # # support
    # message = {
    #     "request": {
    #         "id": 12
    #     },
    #     "support": {
    #         "title": "need help",
    #         "instance": {
    #             "id": 15,
    #             "name": "instance name"
    #         }
    #     },
    #     "content": "message",
    #     "sender": {"username": "test@hpe.com"}
    # }
    # context = {
    #     'request': Request.objects.get(id=1),
    #     'current_site': settings.SQUEST_HOST,
    #     'message': message,
    # }
    # return render(request, "service_catalog/mails/support.html", context)

    # support closed
    # support = {
    #     "title": "need help",
    #     "instance": {
    #         "id": 15,
    #         "name": "instance name"
    #     }
    # }
    # context = {
    #     'request': Request.objects.get(id=1),
    #     'current_site': settings.SQUEST_HOST,
    #     'support': support,
    # }
    # return render(request, "service_catalog/mails/closed_support.html", context)
