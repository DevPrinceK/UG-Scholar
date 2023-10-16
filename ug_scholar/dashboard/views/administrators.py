from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from accounts.models import User
from ug_scholar.library.decorators import AdministratorsOnly
from ug_scholar.library.utils_functions import log_user_action


class AdministratorsView(View):
    '''Renders the administrators page'''
    template_name = 'pages/administrators.html'
    
    @method_decorator(AdministratorsOnly)
    def get(self, request):
        user = request.user
        administrators = User.objects.all()
        log_user_action(user, "Viewed administrators page")
        context = {
            'administrators': administrators
        }
        return render(request, self.template_name, context)
    
  
class CreateUpdateAdministratorView(View):
    '''Renders the create/update administrators page'''
    
    @method_decorator(AdministratorsOnly)
    def get(self, request):
        user = request.user
        log_user_action(user, "Tried to access admin creation form via get request")
        return redirect('dashboard:administrators')    
    
    @method_decorator(AdministratorsOnly)
    def post(self, request):
        user = request.user
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        fullname = request.POST.get('fullname')
        
        admin = User.objects.filter(email=email).first()
        if password != password2:
            log_user_action(user, "Tried to create admin account with mismatching passwords")
            messages.info(request, "Passwords Do Not Match")
            return redirect('dashboard:administrators')
        
        if admin is not None:
            log_user_action(user, "Tried to create admin account with an already existing email")
            messages.info(request, "Email is Already Associated with an Account")
            return redirect('dashboard:administrators')
        try:
            new_admin = User.objects.create_user(email=email, password=password, fullname=fullname)
            new_admin.is_staff = True
            new_admin.save()
        except Exception as e:
            log_user_action(user, f"Tried to create admin account but error occured: {str(e)}")
            messages.info(request, "Error Creating Administrator Account")
            return redirect('dashboard:administrators')
        else:
            log_user_action(user, f"Created admin account: {new_admin.fullname} successfully")
            messages.success(request, "Administrator Account Created Successfully")
        return redirect('dashboard:administrators')

