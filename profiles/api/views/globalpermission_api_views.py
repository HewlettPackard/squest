from Squest.utils.squest_api_views import SquestRetrieveUpdateAPIView
from profiles.api.serializers import GlobalPermissionSerializer
from profiles.models import GlobalPermission


class GlobalPermissionDetails(SquestRetrieveUpdateAPIView):
    serializer_class = GlobalPermissionSerializer
    queryset = GlobalPermission.objects.all()

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = GlobalPermission.load().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)
