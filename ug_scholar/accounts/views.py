from django.shortcuts import render
from django.views import View
    
class LoginView(View):
    '''Login view - /login/'''
    template_name = 'pages/login.html'
    
    def get(self, request):
        return render(request, self.template_name)
