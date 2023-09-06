from service_catalog.models import ApprovalState
from service_catalog.models.instance import InstanceState
from service_catalog.models.request import RequestState

map_dict_request_state = {
    RequestState.ACCEPTED: "primary",
    RequestState.NEED_INFO: "warning",
    RequestState.SUBMITTED: "info",
    RequestState.REJECTED: "dark",
    RequestState.PROCESSING: "orange",
    RequestState.COMPLETE: "success",
    RequestState.FAILED: "danger",
    RequestState.CANCELED: "secondary",
    RequestState.ARCHIVED: "black"
}

map_dict_instance_state = {
    InstanceState.PENDING: "secondary",
    InstanceState.PROVISIONING: "primary",
    InstanceState.PROVISION_FAILED: "warning",
    InstanceState.AVAILABLE: "success",
    InstanceState.DELETE_FAILED: "warning",
    InstanceState.DELETING: "primary",
    InstanceState.UPDATING: "primary",
    InstanceState.UPDATE_FAILED: "warning",
    InstanceState.DELETED: "danger",
    InstanceState.ARCHIVED: "dark",
    InstanceState.ABORTED: "gray_dark",
}

map_dict_step_state = {
    ApprovalState.APPROVED: "success",
    ApprovalState.REJECTED: "danger",
    ApprovalState.PENDING: "info",
}

map_class_to_color = {
    "blue": "#007bff",
    "indigo": "#6610f2",
    "purple": "#6f42c1",
    "pink": "#e83e8c",
    "red": "#dc3545",
    "orange": "#fd7e14",
    "yellow": "#ffc107",
    "green": "#28a745",
    "teal": "#20c997",
    "cyan": "#17a2b8",
    "white": "#fff",
    "gray": "#6c757d",
    "gray - dark": "#343a40",
    "primary": "#007bff",
    "secondary": "#6c757d",
    "success": "#28a745",
    "info": "#17a2b8",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

random_color = {
    "blue": "#007bff",
    "indigo": "#6610f2",
    "purple": "#6f42c1",
    "pink": "#e83e8c",
    "red": "#dc3545",
    "orange": "#fd7e14",
    "yellow": "#ffc107",
    "green": "#28a745",
    "teal": "#20c997",
    "cyan": "#17a2b8",
    "gray": "#6c757d",
    "primary": "#007bff",
    "secondary": "#6c757d",
    "success": "#28a745",
    "info": "#17a2b8",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "light": "#f8f9fa"
}
