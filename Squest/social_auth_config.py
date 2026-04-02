import os

print("Social Auth config loaded")

# -----------------------------------------
# Social Auth - General
# -----------------------------------------
SOCIAL_AUTH_OIDC_BTN_TEXT = os.environ.get("SOCIAL_AUTH_OIDC_BTN_TEXT", "Github enterprise")
# backend url. E.g: google-oauth2, github-enterprise, github, oidc
SOCIAL_AUTH_SELECTED_BACKEND = "github-enterprise"  # this is the name of the backend loaded by django url

# -----------------------------------------
# Social Auth - GitHub Enterprise
# -----------------------------------------
# callback: http://192.168.83.128:8000/accounts/complete/github-enterprise
SOCIAL_AUTH_GITHUB_ENTERPRISE_URL = os.environ.get("SOCIAL_AUTH_GITHUB_ENTERPRISE_URL")
SOCIAL_AUTH_GITHUB_ENTERPRISE_API_URL = os.environ.get("SOCIAL_AUTH_GITHUB_ENTERPRISE_API_URL")
SOCIAL_AUTH_GITHUB_ENTERPRISE_KEY = os.environ.get("SOCIAL_AUTH_GITHUB_ENTERPRISE_KEY")
SOCIAL_AUTH_GITHUB_ENTERPRISE_SECRET = os.environ.get("SOCIAL_AUTH_GITHUB_ENTERPRISE_SECRET")
SOCIAL_AUTH_GITHUB_ENTERPRISE_SCOPE = ["user:email"]

# -----------------------------------------
# Social Auth - OIDC / Okta (commented out, kept for reference)
# -----------------------------------------
# callback: http://192.168.83.128:8000/accounts/complete/oidc
# SOCIAL_AUTH_OIDC_OIDC_ENDPOINT = os.environ.get("SOCIAL_AUTH_OIDC_ENDPOINT")
# SOCIAL_AUTH_OIDC_KEY = os.environ.get("SOCIAL_AUTH_OIDC_KEY")
# SOCIAL_AUTH_OIDC_SECRET = os.environ.get("SOCIAL_AUTH_OIDC_SECRET")

# -----------------------------------------
# Social Auth - Pipeline
# -----------------------------------------
SOCIAL_AUTH_PIPELINE = (
    "social_core.pipeline.social_auth.social_details",
    "social_core.pipeline.social_auth.social_uid",
    "social_core.pipeline.social_auth.auth_allowed",
    "social_core.pipeline.social_auth.social_user",
    "Squest.social_auth_config.set_username_from_email",  # pipeline example used to map the oauth email to django username
    "social_core.pipeline.user.get_username",
    "social_core.pipeline.user.create_user",
    "social_core.pipeline.social_auth.associate_user",
    "social_core.pipeline.social_auth.load_extra_data",
    "social_core.pipeline.user.user_details",
)

# -----------------------------------------
# Social Auth - Django integration
# -----------------------------------------
AUTHENTICATION_BACKENDS = (
    # default django must be kept to allow admin login and permissions system to work, it must be before the social auth backends
    "django.contrib.auth.backends.ModelBackend",

    # python social auth backend. Keep only one uncommented
    # "social_core.backends.open_id_connect.OpenIdConnectAuth",
    # "social_core.backends.google.GoogleOAuth2",
    # "social_core.backends.twitter.TwitterOAuth",
    "social_core.backends.github_enterprise.GithubEnterpriseOAuth2",

    # this one is mandatory to use the permissions system of Squest with social auth, it must be after the social auth backends
    "Squest.utils.squest_rbac.SquestRBACBackend",
)

# -----------------------------------------
# Social Auth - Custom pipeline example
# -----------------------------------------
def set_username_from_email(strategy, details, backend, user=None, *args, **kwargs):
    """
    Custom social auth pipeline step that uses the user's email as their username.
    Must be placed before 'social_core.pipeline.user.get_username' in the pipeline.
    """
    email = details.get("email")
    if email:
        details["username"] = email
