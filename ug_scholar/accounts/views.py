from django.shortcuts import redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
    
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
            messages.info(request, f"Successfully logged in as {user.fullname}")
            return redirect("dashboard:index")
        else:
            messages.error(request, "Invalid email or password")
            return redirect("dashboard:index")
        
        
class LogoutView(View):
    '''Logout view - Logout the current user'''
    
    def get(self, request):
        logout(request)
        messages.info(request, "Successfully logged out")
        return redirect("dashboard:index")
    