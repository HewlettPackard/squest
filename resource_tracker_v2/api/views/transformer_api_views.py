from Squest.utils.squest_api_views import SquestRetrieveUpdateDestroyAPIView, SquestListCreateAPIView
from resource_tracker_v2.api.serializers.transformer_serializer import TransformerSerializer
from resource_tracker_v2.filters.transformer_filter import TransformerFilter
from resource_tracker_v2.models import Transformer


class TransformerListCreate(SquestListCreateAPIView):
    serializer_class = TransformerSerializer
    filterset_class = TransformerFilter
    queryset = Transformer.objects.all()


class TransformerDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = TransformerSerializer
    queryset = Transformer.objects.all()
