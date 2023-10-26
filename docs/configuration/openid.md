# OpenID Connect authentication backend

## Default configuration

The configuration is loaded from environment variables file placed in the folder `docker/environment_variables`.

Retrieve environment variables from the [Squest configuration settings documentation](../configuration/squest_settings.md#openid-connect)

Configuration example:
```bash
SOCIAL_AUTH_OIDC_ENABLED=True
SOCIAL_AUTH_OIDC_BTN_TEXT="OpenID Login"
SOCIAL_AUTH_OIDC_OIDC_ENDPOINT="https://example.com/"
SOCIAL_AUTH_OIDC_KEY="client_id"
SOCIAL_AUTH_OIDC_SECRET="secret"
```