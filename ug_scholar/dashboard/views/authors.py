from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.utils.html import strip_tags
from accounts.models import User

from api.models import Author, Profile
from dashboard.forms import AuthorProfileForm
from ug_scholar.library.constants import UG

from django.utils.decorators import method_decorator

from ug_scholar.library.decorators import AdministratorsOnly

    
class AuthorsView(View):
    '''Renders the authors profiles page - profiles page'''
    template_name = 'pages/authors.html'
    
    def get(self, request):
        ug = UG()
        authors = Profile.objects.all()
        
        
        schools = ug.get_schools()
        departments = ug.get_departments()
        colleges = ug.get_colleges()
        
        print("Priting Colleges")
        print(colleges)
        
        
        context = {
            'authors': authors,
            'colleges': colleges,
            'schools': schools,
            'departments': departments,
        }
        return render(request, self.template_name, context)
    
    
class CreateUpdateAuthorView(View):
    '''Renders the create/update author page'''
    
    def get(self, request):
        return redirect('dashboard:authors')    
    
    @method_decorator(AdministratorsOnly)
    def post(self, request):
        scholar_id = request.POST.get('scholar_id')
        profile = Profile.objects.filter(scholar_id=scholar_id).first()
        if profile is not None:
            messages.info(request, "Author Profile Already Exists")
            return redirect('dashboard:authors')
        print("Now Printing Scholar ID")
        print(scholar_id)
        form = AuthorProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()
            author = Author.objects.create(profile=profile)
            author.save()
            messages.success(request, "Author Profile Created Successfully")
            return redirect('dashboard:authors')
        else:
            for field, error in form.errors.items():
                message = f"{field.title()}: {strip_tags(error)}"
                messages.info(request, message)
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
