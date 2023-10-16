from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from accounts.models import User
from django.utils.decorators import method_decorator

from ug_scholar.library.decorators import AdministratorsOnly


class AdministratorsView(View):
    '''Renders the administrators page'''
    template_name = 'pages/administrators.html'
    
    @method_decorator(AdministratorsOnly)
    def get(self, request):
        administrators = User.objects.all()
        context = {
            'administrators': administrators
        }
        return render(request, self.template_name, context)
    
  
class CreateUpdateAdministratorView(View):
    '''Renders the create/update administrators page'''
    
    @method_decorator(AdministratorsOnly)
    def get(self, request):
        return redirect('dashboard:administrators')    
    
    @method_decorator(AdministratorsOnly)
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        fullname = request.POST.get('fullname')
        
        admin = User.objects.filter(email=email).first()
        if password != password2:
            messages.info(request, "Passwords Do Not Match")
            return redirect('dashboard:administrators')
        
        if admin is not None:
            messages.info(request, "Email is Already Associated with an Account")
            return redirect('dashboard:administrators')
        try:
            new_admin = User.objects.create_user(email=email, password=password, fullname=fullname)
            new_admin.is_staff = True
            new_admin.save()
        except Exception as e:
            messages.info(request, "Error Creating Administrator Account")
            return redirect('dashboard:administrators')
        else:
            messages.success(request, "Administrator Account Created Successfully")
        return redirect('dashboard:administrators')

