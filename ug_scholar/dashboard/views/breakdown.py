import json

from django.db.models import Count, Sum
from django.shortcuts import render
from django.views import View

from api.models import Profile


class CollegesView(View):
    '''Renders the colleges page - List of colleges and their statistics'''
    template_name = 'pages/colleges.html'
    
    def get(self, request):
         # !!!!!!!! college breakdown info
        # Query to get unique colleges along with their information
        college_breakdown_info = Profile.objects.values('college').annotate(
            total_authors=Count('id'),
            authors_with_publications=Count('author__publications', distinct=True),
            total_publications=Count('author__publications'),
            total_citations=Sum('author__publications__citations'),
        ).order_by('college')
        
         # Convert the queryset to a list of dictionaries
        college_breakdown_info_list = list(college_breakdown_info)

        # Calculate total_h_index and total_i10_index
        for college in college_breakdown_info_list:
            authors = Profile.objects.filter(college=college['college'])
            total_autors = authors.count()
            authors_with_publications = authors.filter(author__publications__isnull=False).distinct().count()
            total_h_index = sum(author.get_author_hindex() for author in authors)
            total_i10_index = sum(author.get_author_i10index() for author in authors)

            college['total_authors'] = total_autors
            college['authors_with_publications'] = authors_with_publications
            college['total_h_index'] = total_h_index
            college['total_i10_index'] = total_i10_index

        context = {
            'college_breakdown_info': college_breakdown_info_list,
            'college_breakdown_json': json.dumps(college_breakdown_info_list),
        }
        return render(request, self.template_name, context)
 
    
class CollegeDetailsView(View):
    '''Renders details page for colleges'''
    template_name = 'pages/college-details.html'
    
    def get(self, request):
        college_name = request.GET.get("college")
        authors = Profile.objects.filter(college=college_name)
        total_h_index = 0
        total_i_index = 0
        total_authors = authors.count()
        total_pubs = 0
        for author in authors:
            total_h_index += author.get_author_hindex()
            total_i_index += author.get_author_i10index()
            total_pubs += author.get_author_publications()
        # compute the college indexes
        college_indexes = [
            {
                "name":"H-INDEX",
                "index":total_h_index,
            },
            {
                "name":"I-INDEX",
                "index":total_i_index,
            }
        ]
        # compute author and pub stats for college
        college_auth_pub = [
            {
                "name":"Total Authors",
                "index":total_authors,
            },
            {
                "name": "Total Publications",
                "index": total_pubs,
            }
        ]
        
        context = {
            "college_name": college_name,
            "authors": authors,
            "college_indexes_json": json.dumps(college_indexes),
            "college_auth_pub_json": json.dumps(college_auth_pub),
        }
        return render(request, self.template_name, context)
        
    
    
class DepartmentDetailsView(View):
    '''Renders details page for colleges'''
    template_name = 'pages/department-details.html'
    
    def get(self, request):
        department_name = request.GET.get("department")
        authors = Profile.objects.filter(department=department_name.strip())
        total_h_index = 0
        total_i_index = 0
        total_authors = authors.count()
        total_pubs = 0
        for author in authors:
            total_h_index += author.get_author_hindex()
            total_i_index += author.get_author_i10index()
            total_pubs += author.get_author_publications()
        # compute the department indexes
        department_indexes = [
            {
                "name":"H-INDEX",
                "index":total_h_index,
            },
            {
                "name":"I-INDEX",
                "index":total_i_index,
            }
        ]
        # compute author and pub stats for department
        department_auth_pub = [
            {
                "name":"Total Authors",
                "index":total_authors,
            },
            {
                "name": "Total Publications",
                "index": total_pubs,
            }
        ]
        
        context = {
            "department_name": department_name,
            "authors": authors,
            "department_indexes_json": json.dumps(department_indexes),
            "department_auth_pub_json": json.dumps(department_auth_pub),
            "department_h_index": total_h_index,
            "department_i_index": total_i_index,
            "department_total_authors": total_authors,
            "department_total_publications": total_pubs,
        }
        return render(request, self.template_name, context)
        
    
class FacultiesView(View):
    '''Renders the faculties page - List of faculties and their statistics'''
    template_name = 'pages/faculties.html'
    
    def get(self, request):
        # !!!!!!!! school breakdown info
        # Query to get unique schools along with their information
        school_breakdown_info = Profile.objects.values('school').annotate(
            total_authors=Count('id'),
            authors_with_publications=Count('author__publications', distinct=True),
            total_publications=Count('author__publications'),
            total_citations=Sum('author__publications__citations'),
        ).order_by('school')

        # Calculate total_h_index and total_i10_index
        for school in school_breakdown_info:
            authors = Profile.objects.filter(school=school['school'])
            total_autors = authors.count()
            authors_with_publications = authors.filter(author__publications__isnull=False).distinct().count() #noqa
            total_h_index = sum(author.get_author_hindex() for author in authors)
            total_i10_index = sum(author.get_author_i10index() for author in authors)
            
            school['total_authors'] = total_autors
            school['authors_with_publications'] = authors_with_publications
            school['total_h_index'] = total_h_index
            school['total_i10_index'] = total_i10_index
            
        context = {
            'school_breakdown_info': school_breakdown_info,
        }
        return render(request, self.template_name, context)
    

class FacultyDetailsView(View):
    '''Renders details page for faculties - institutions and centers'''
    template_name = 'pages/faculty-details.html'
    
    def get(self, request):
        institution_name = request.GET.get("institution")
        authors = Profile.objects.filter(school=institution_name.strip())
        total_h_index = 0
        total_i_index = 0
        total_authors = authors.count()
        total_pubs = 0
        for author in authors:
            total_h_index += author.get_author_hindex()
            total_i_index += author.get_author_i10index()
            total_pubs += author.get_author_publications()
        # compute the institution indexes
        institution_indexes = [
            {
                "name":"H-INDEX",
                "index":total_h_index,
            },
            {
                "name":"I-INDEX",
                "index":total_i_index,
            }
        ]
        # compute author and pub stats for institution
        institution_auth_pub = [
            {
                "name":"Total Authors",
                "index":total_authors,
            },
            {
                "name": "Total Publications",
                "index": total_pubs,
            }
        ]
        
        context = {
            "institution_name": institution_name,
            "authors": authors,
            "institution_indexes_json": json.dumps(institution_indexes),
            "institution_auth_pub_json": json.dumps(institution_auth_pub),
            "institution_h_index": total_h_index,
            "institution_i_index": total_i_index,
            "institution_total_authors": total_authors,
            "institution_total_publications": total_pubs,
        }
        return render(request, self.template_name, context)
        

  
    
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
  
