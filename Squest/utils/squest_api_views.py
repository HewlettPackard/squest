from rest_framework.exceptions import APIException, PermissionDenied, NotAuthenticated
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveUpdateAPIView, ListAPIView, CreateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions, SAFE_METHODS
from rest_framework.renderers import BrowsableAPIRenderer


class SquestObjectPermissions(DjangoObjectPermissions):

    def has_permission(self, request, view):
        # Skip Class based permissions, otherwise we need to assign user permissions to all ours users.
        return True

    def has_object_permission(self, request, view, obj):
        # Override to raise 403 instead of 404
        # authentication checks have already executed via has_permission
        queryset = self._queryset(view)
        model_cls = queryset.model
        user = request.user

        perms = self.get_required_object_permissions(request.method, model_cls)

        if not user.has_perms(perms, obj):
            # If the user does not have permissions we need to determine if
            # they have read permissions to see 403, or not, and simply see
            # a 404 response.

            if request.method in SAFE_METHODS:
                # Read permissions already checked and failed, no need
                # to make another lookup.
                raise PermissionDenied

            read_perms = self.get_required_object_permissions('GET', model_cls)
            if not user.has_perms(read_perms, obj):
                raise PermissionDenied

            # Has read permissions.
            return False

        return True


class SquestObjectPermissionsDetails(SquestObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


class SquestObjectPermissionsListCreate(SquestObjectPermissions):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    perms_map = {
        'GET': ['%(app_label)s.list_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s']
    }


class SquestBrowsableAPIRenderer(BrowsableAPIRenderer):

    # Use check_object_permissions method even if object is None
    def show_form_for_method(self, view, method, request, obj):
        """
        Returns True if a form should be shown for this method.
        """
        if method not in view.allowed_methods:
            return  # Not a valid method

        try:
            view.check_object_permissions(request, obj)
        except APIException:
            return False  # Doesn't have permissions
        return True


class SquestGenericAPIView(GenericAPIView, SquestBrowsableAPIRenderer):
    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        if not request.user.is_authenticated:
            raise NotAuthenticated

        self.format_kwarg = self.get_format_suffix(**kwargs)

        # Perform content negotiation and store the accepted info on the request
        neg = self.perform_content_negotiation(request)
        request.accepted_renderer, request.accepted_media_type = neg

        # Determine the API version, if versioning is in use.
        version, scheme = self.determine_version(request, *args, **kwargs)
        request.version, request.versioning_scheme = version, scheme

        try:
            obj = self.get_object()
        except AssertionError:
            obj = None

        # Ensure that the incoming request is permitted
        self.perform_authentication(request)
        self.check_object_permissions(request, obj)
        self.check_throttles(request)


class SquestListCreateAPIView(ListCreateAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsListCreate]


class SquestListAPIView(ListAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsListCreate]


class SquestCreateAPIView(CreateAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsListCreate]


class SquestRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, SquestGenericAPIView,
                                         SquestBrowsableAPIRenderer):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsDetails]


class SquestRetrieveUpdateAPIView(RetrieveUpdateAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsDetails]


class SquestRetrieveAPIView(RetrieveAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsDetails]


class SquestDestroyAPIView(DestroyAPIView, SquestGenericAPIView, SquestBrowsableAPIRenderer):
    permission_classes = [IsAuthenticated, SquestObjectPermissionsDetails]
