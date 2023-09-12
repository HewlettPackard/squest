from django.db.models import IntegerChoices


class RequestState(IntegerChoices):
    SUBMITTED = 1, "SUBMITTED"
    NEED_INFO = 2, "NEED_INFO"
    REJECTED = 3, "REJECTED"
    ACCEPTED = 4, "ACCEPTED"
    CANCELED = 5, "CANCELED"
    PROCESSING = 6, "PROCESSING"
    COMPLETE = 7, "COMPLETE"
    FAILED = 8, "FAILED"
    ARCHIVED = 9, "ARCHIVED"
