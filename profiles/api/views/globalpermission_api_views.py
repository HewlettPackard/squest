from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAdminUser
from profiles.api.serializers import GlobalPermissionSerializer
from profiles.models import GlobalPermission


class GlobalPermissionDetails(RetrieveUpdateAPIView):
    serializer_class = GlobalPermissionSerializer
    permission_classes = [IsAdminUser]
    queryset = GlobalPermission.objects.all()

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = GlobalPermission.load().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)


