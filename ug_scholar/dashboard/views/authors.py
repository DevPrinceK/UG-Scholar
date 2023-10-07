from django.shortcuts import render
from django.views import View

from api.models import Author, Profile

    
class AuthorsView(View):
    '''Renders the authors profiles page - profiles page'''
    template_name = 'pages/authors.html'
    
    def get(self, request):
        authors = Profile.objects.all()
        
        context = {
            'authors': authors,
        }
        return render(request, self.template_name, context)