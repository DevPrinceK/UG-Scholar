from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import View

from accounts.models import User
from api.models import Author, Profile
from dashboard.forms import AuthorProfileForm
from ug_scholar.library.constants import UG
from ug_scholar.library.decorators import AdministratorsOnly
from ug_scholar.library.utils_functions import log_user_action


class AuthorsView(View):
    '''Renders the authors profiles page - profiles page'''
    template_name = 'pages/authors.html'
    
    def get(self, request):
        ug = UG()
        authors = Profile.objects.all()
        
        schools = ug.get_schools()
        departments = ug.get_departments()
        colleges = ug.get_colleges()
      
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
        user = request.user
        log_user_action(user, "Tried to access author form using get request")
        return redirect('dashboard:authors')    
    
    @method_decorator(AdministratorsOnly)
    def post(self, request):
        user = request.user
        scholar_id = request.POST.get('scholar_id')
        profile = Profile.objects.filter(scholar_id=scholar_id).first()
        if profile is not None:
            log_user_action(user, "Tried to create author profile with an already existing scholar id")
            messages.info(request, "Author Profile Already Exists")
            return redirect('dashboard:authors')
        form = AuthorProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()
            author = Author.objects.create(profile=profile)
            author.save()
            log_user_action(user, f"Created author profile: {profile.name} successfully")
            messages.success(request, "Author Profile Created Successfully")
            return redirect('dashboard:authors')
        else:
            for field, error in form.errors.items():
                message = f"{field.title()}: {strip_tags(error)}"
                log_user_action(user, f"Tried to create author profile but error occured: {message}")
                messages.info(request, message)
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
