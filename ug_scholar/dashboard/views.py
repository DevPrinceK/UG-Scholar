from django.shortcuts import render
from django.views import View

class IndexView(View):
    template_name = 'pages/index.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
class AuthorsView(View):
    template_name = 'pages/authors.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
class PublicationsView(View):
    template_name = 'pages/publications.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
class CollegesView(View):
    template_name = 'pages/colleges.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
class FacultiesView(View):
    template_name = 'pages/faculties.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
class DepartmentsView(View):
    template_name = 'pages/departments.html'
    
    def get(self, request):
        return render(request, self.template_name)
    
class LoginView(View):
    template_name = 'pages/login.html'
    
    def get(self, request):
        return render(request, self.template_name)
