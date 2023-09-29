from Squest.utils.squest_api_views import SquestRetrieveUpdateAPIView
from profiles.api.serializers import GlobalScopeSerializer
from profiles.models import GlobalScope


class GlobalScopeDetails(SquestRetrieveUpdateAPIView):
    serializer_class = GlobalScopeSerializer
    queryset = GlobalScope.objects.all()

    def dispatch(self, request, *args, **kwargs):
        self.kwargs['pk'] = GlobalScope.load().id
        kwargs['pk'] = self.kwargs.get('pk')
        return super().dispatch(request, *args, **kwargs)
