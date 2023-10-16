from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views import View

from ug_scholar.library.utils_functions import log_user_action


class LoginView(View):
    '''Login view - /login/'''
    
    def get(self, request):
        # redirect to home when user uses the get method
        return redirect("dashboard:index")
    
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            log_user_action(user, "Logged in into the system")
            messages.info(request, f"Successfully logged in as {user.fullname}")
            return redirect("dashboard:index")
        else:
            messages.error(request, "Invalid email or password")
            return redirect("dashboard:index")
        
        
class LogoutView(View):
    '''Logout view - Logout the current user'''
    
    def get(self, request):
        user = request.user
        log_user_action(user, "Logged out from the system")
        logout(request)
        messages.info(request, "Successfully logged out")
        return redirect("dashboard:index")
    