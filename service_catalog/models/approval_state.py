from django.db.models import IntegerChoices


class ApprovalState(IntegerChoices):
    PENDING = 1, 'PENDING'
    APPROVED = 2, 'APPROVED'
    REJECTED = 3, 'REJECTED'
