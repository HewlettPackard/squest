from rest_framework import authentication, exceptions

from profiles.models import Token


class TokenAuthentication(authentication.TokenAuthentication):
    """
    A custom authentication scheme which enforces Token expiration times.
    """
    model = Token
    keyword = 'Bearer'

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            token = model.objects.prefetch_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token")
        # Enforce the Token's expiration time, if one has been set.
        if token.is_expired():
            raise exceptions.AuthenticationFailed("Token expired")
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed("User inactive")
        return token.user, token
