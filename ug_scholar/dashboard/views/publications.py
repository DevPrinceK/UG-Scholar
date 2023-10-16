from django.shortcuts import render
from django.views import View

from api.models import Publication


class PublicationsView(View):
    template_name = 'pages/publications.html'
    
    def get(self, request):
        publications = Publication.objects.all()
        
        context = {
            'publications': publications,
        }
        return render(request, self.template_name, context)
