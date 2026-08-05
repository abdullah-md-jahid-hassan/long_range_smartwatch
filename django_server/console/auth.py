from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy


class StaffAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise ValidationError("This account does not have console access.", code="not_staff")


class ConsoleLoginView(LoginView):
    template_name = "console/login.html"
    authentication_form = StaffAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return str(reverse_lazy("console:dashboard"))
