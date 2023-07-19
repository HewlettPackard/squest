from django.contrib.auth.models import User

from Squest.utils.squest_api_views import SquestRetrieveUpdateDestroyAPIView, SquestListCreateAPIView
from profiles.api.serializers.user_serializers import UserSerializer
from profiles.filters.user_filter import UserFilter


class UserDetails(SquestRetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class UserListCreate(SquestListCreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_class = UserFilter
