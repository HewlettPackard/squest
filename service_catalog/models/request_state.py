from django.db.models import IntegerChoices


class RequestState(IntegerChoices):
    SUBMITTED = 1, "SUBMITTED"
    NEED_INFO = 2, "NEED_INFO"
    REJECTED = 3, "REJECTED"
    CANCELED = 4, "CANCELED"
    ACCEPTED = 5, "ACCEPTED"
    PROCESSING = 6, "PROCESSING"
    COMPLETE = 7, "COMPLETE"
    FAILED = 8, "FAILED"
    ARCHIVED = 9, "ARCHIVED"
