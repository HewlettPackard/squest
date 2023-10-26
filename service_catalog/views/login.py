from django.contrib.auth import views as auth_views


class LoginView(auth_views.LoginView):
    template_name = 'registration/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.conf import settings
        context.update({
            'login_helper_text': settings.LOGIN_HELPER_TEXT,
            'openid_active': settings.SOCIAL_AUTH_OIDC_ENABLED,
            'openid_btn_text': settings.SOCIAL_AUTH_OIDC_BTN_TEXT,
            'password_enabled': settings.PASSWORD_ENABLED
        })
        return context
