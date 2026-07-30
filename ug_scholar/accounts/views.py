from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View

from ug_scholar.library.utils_functions import log_user_action


class LoginView(View):
    '''Login view - /login/'''
    
    def get(self, request):
        # redirect to home when user uses the get method
        return redirect("dashboard:index")
    
    
    def post(self, request):
        email = (request.POST.get('email') or "").strip().lower()
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            request.session.set_expiry(settings.SESSION_COOKIE_AGE)
            log_user_action(user, "Logged in into the system")
            messages.info(request, f"Successfully logged in as {user.fullname}")
            next_url = (request.POST.get("next") or "").strip()
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("dashboard:index")
        else:
            messages.error(request, "Invalid email or password")
            return redirect("dashboard:index")
        
        
class LogoutView(View):
    '''Logout view - Logout the current user'''
    
    def get(self, request):
        return redirect("dashboard:index")

    def post(self, request):
        if request.user.is_authenticated:
            log_user_action(request.user, "Logged out from the system")
            logout(request)
            messages.info(request, "Successfully logged out")
        return redirect("dashboard:index")
