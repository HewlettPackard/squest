from django.contrib.auth import views as auth_views


class LoginView(auth_views.LoginView):
    template_name = 'registration/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.conf import settings
        context.update({
            'login_helper_text': settings.LOGIN_HELPER_TEXT,
        })
        return context
