from django.shortcuts import render
from django.views import View
from django.db.models import Sum, Count

from api.models import Profile

    
class CollegesView(View):
    '''Renders the colleges page - List of colleges and their statistics'''
    template_name = 'pages/colleges.html'
    
    def get(self, request):
        return render(request, self.template_name)
 
    
class FacultiesView(View):
    '''Renders the faculties page - List of faculties and their statistics'''
    template_name = 'pages/faculties.html'
    
    def get(self, request):
        return render(request, self.template_name)
  
    
class DepartmentsView(View):
    '''Renders the departments page - List of departments and their statistics'''
    template_name = 'pages/departments.html'
    
    def get(self, request):
         # !!!!!!!! departmental breakdown info
        # Query to get unique departments along with their information
        department_breakdown_info = Profile.objects.values('department').annotate(
            total_authors=Count('id'),
            authors_with_publications=Count('author__publications', distinct=True),
            total_publications=Count('author__publications'),
            total_citations=Sum('author__publications__citations'),
        ).order_by('department')

        # Calculate total_h_index and total_i10_index
        for department in department_breakdown_info:
            authors = Profile.objects.filter(department=department['department'])
            total_autors = authors.count()
            authors_with_publications = authors.filter(author__publications__isnull=False).distinct().count() #noqa
            total_h_index = sum(author.get_author_hindex() for author in authors)
            total_i10_index = sum(author.get_author_i10index() for author in authors)
            
            department['total_authors'] = total_autors
            department['authors_with_publications'] = authors_with_publications
            department['total_h_index'] = total_h_index
            department['total_i10_index'] = total_i10_index
        
        context = {
            'department_breakdown_info': department_breakdown_info,
        }
        return render(request, self.template_name, context)
  
