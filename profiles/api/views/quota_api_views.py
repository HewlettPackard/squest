from Squest.utils.squest_api_views import SquestListCreateAPIView, SquestRetrieveUpdateDestroyAPIView
from profiles.api.serializers.quota_serializer import QuotaSerializer
from profiles.filters.quota import QuotaFilter
from profiles.models import Quota



class QuotaDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = QuotaSerializer
    queryset = Quota.objects.all()



class QuotaListCreate(SquestListCreateAPIView):
    serializer_class = QuotaSerializer
    queryset = Quota.objects.all()
    filterset_class = QuotaFilter
