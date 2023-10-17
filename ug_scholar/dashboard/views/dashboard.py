import json
from datetime import datetime, timedelta

from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views import View

from api.models import Author, Profile, Publication


class IndexView(View):
    '''Renders the dashboard page - Handles all the homepage statistics'''
    template_name = 'pages/index.html'
    
    def get(self, request):
        # authors
        total_authors = Author.objects.count()
        publishing_authors = Author.objects.filter(publications__isnull=False).distinct().count() #noqa
        
        # publications
        total_publications = Publication.objects.count()
        
        # !!!!!!!!!!!! publications breakdown
        # colleges and their publications
        college_publications = Profile.objects.values('college').annotate(total_publications=Count('author__publications')) #noqa
        
        # Calculate the total number of publications accross all colleges
        total_publications_across_colleges = college_publications.aggregate(
            total=Sum('total_publications')
        )['total'] or 1  # Ensure it's not zero
        
        # Calculate the 'percentages' field for each college
        for entry in college_publications:
            entry['percentages'] = (
                (entry['total_publications'] / total_publications_across_colleges) * 100
            )
   
        # !!!!!!!!!!! Citations breakdown
        # Query to get total citations for each college
        college_citations = Profile.objects.values('college').annotate(
            total_citations=Sum('author__publications__citations')
        ).order_by('college')

        # Calculate the total number of citations across all colleges
        total_citations_across_colleges = college_citations.aggregate(
            total=Sum('total_citations')
        )['total'] or 1  # Ensure it's not zero

        # Calculate the 'percentage' field for each college as a float
        for entry in college_citations:
            entry['percentage'] = (entry['total_citations'] / total_citations_across_colleges) * 100.0
            
        
        # !!!!!!!!!!! Top 3 schools/Faculties/intitutes
        # Query to get total publications for each school
        total_pubs_for_top_3_schools = 0
        school_publications = Profile.objects.values('school').annotate(
            total_publications=Count('author__publications')
        ).order_by('school')[:3]

        # Calculate the total number of publications across top 3 schools
        total_publications_across_schools = school_publications.aggregate(
            total=Sum('total_publications')
        )['total'] or 1  # Ensure it's not zero

        # Calculate the 'percentage' field for each school as a float
        for entry in school_publications:
            total_pubs_for_top_3_schools += entry['total_publications']
            entry['percentage'] = (entry['total_publications'] / total_publications_across_schools) * 100.0
        # serialize data and parse as data attribute to js for chart display
        schools_pub_data = [
            {
                'school': entry['school'],
                'total_publications': entry['total_publications'],
            }
            for entry in school_publications
        ]
            

        # !!!!!!!!!!!! 3 years performance   
        # Calculate the current year and the two previous years
        current_year = datetime.now().year
        last_three_years = [current_year - i for i in range(2, -1, -1)]
        
        # !!!!!!!! college breakdown info
        # Query to get unique colleges along with their information
        college_breakdown_info = Profile.objects.values('college').annotate(
            total_authors=Count('id'),
            authors_with_publications=Count('author__publications', distinct=True),
            total_publications=Count('author__publications'),
            total_citations=Sum('author__publications__citations'),
        ).order_by('college')

        # Calculate total_h_index and total_i10_index
        for college in college_breakdown_info:
            authors = Profile.objects.filter(college=college['college'])
            total_autors = authors.count()
            authors_with_publications = authors.filter(author__publications__isnull=False).distinct().count() #noqa
            total_h_index = sum(author.get_author_hindex() for author in authors)
            total_i10_index = sum(author.get_author_i10index() for author in authors)
            
            college['total_authors'] = total_autors
            college['authors_with_publications'] = authors_with_publications
            college['total_h_index'] = total_h_index
            college['total_i10_index'] = total_i10_index
        
        
        # !!!!!!!! departmental breakdown info
        # Query to get unique departments along with their information
        department_breakdown_info = Profile.objects.values('department').annotate(
            total_authors=Count('id'),
            authors_with_publications=Count('author__publications', distinct=True),
            total_publications=Count('author__publications'),
            total_citations=Sum('author__publications__citations'),
        ).order_by('department')[:10]

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

        # Query to get the total publications and citations for each of the last three years
        three_years_performance = Publication.objects.filter(
            year__in=last_three_years
        ).values('year').annotate(
            total_publications=Count('id'),
            total_citations=Sum('citations')
        ).order_by('year')  
        
        performance_data = [
        {
            'year': entry['year'],
            'total_publications': entry['total_publications'],
            'total_citations': entry['total_citations'],
        }
        for entry in three_years_performance
        ]
        
        # !!!!!!!!!!! 10 years performance
        # Query to get the total publications and citations for each of the last 10 years
        last_ten_years = [current_year - i for i in range(9, -1, -1)]
        ten_years_performance = Publication.objects.filter(
            year__in=last_ten_years
        ).values('year').annotate(
            total_publications=Count('id'),
            total_citations=Sum('citations')
        ).order_by('year')  
        
        ten_years_performance_data = [
        {
            'year': entry['year'],
            'total_publications': entry['total_publications'],
            'total_citations': entry['total_citations'],
        }
        for entry in ten_years_performance
        ]
        
        # Top 7 Journals
        # Query to get the top 7 unique journals with total publications and citations
        top_journals = Publication.objects.values('journal').annotate(
            total_publications=Count('id'),
            total_citations=Coalesce(Sum('citations'), 0)
        ).order_by('-total_publications')[:7]
        
        journals_data = [
        {
            'journal': entry['journal'],
            'total_publications': entry['total_publications'],
            'total_citations': entry['total_citations'],
        }
        for entry in top_journals
        ]
        
        # !!!!!!!!!!! Top 10s
        # Top 10 authors by publications count
        top_10_authors = Author.objects.annotate(
            total_publications=Count('publications')
        ).order_by('-total_publications')[:10]
        
        # Top 10 authors by citations count
        top_authors_by_citations = Author.objects.annotate(
            total_citations=Sum('publications__citations'),
            percentage = Sum('publications__citations')
        ).order_by('-total_citations')[:10]
        # add percentages - first ensure that total_citations is not zero
        total_citations = top_authors_by_citations.aggregate(
            total=Sum('total_citations')
        )['total'] or 1
        for author in top_authors_by_citations:
            if author.total_citations == None :
                author.percentage = 0
            else:
                author.percentage = (author.total_citations / total_citations) * 100.0
        
      
        # Top 10 publications by citations count
        top_10_publications = Publication.objects.order_by('-citations')[:10]
        
        # Citations and H-index, i10-index
        total_citations = Publication.objects.aggregate(Sum('citations'))['citations__sum'] #noqa
        total_hindex = 0
        total_i10index = 0
        for profile in Profile.objects.all():
            total_hindex += profile.get_author_hindex()
            total_i10index += profile.get_author_i10index()
      
        context = {
            'total_authors': total_authors,
            'publishing_authors': publishing_authors,
            # 
            'total_publications': total_publications,
            # 
            'total_citations': total_citations,
            'total_hindex': total_hindex,
            'total_i10index': total_i10index,
            # 
            'college_publications': college_publications,
            # 
            'college_citations': college_citations,
            # 
            'performance_json': json.dumps(performance_data),
            'ten_years_performance_json': json.dumps(ten_years_performance_data),
            # Top 10s
            'top_10_authors': top_10_authors,
            'top_10_publications': top_10_publications,
            # top 3 schools by publications
            'school_publications' : school_publications,
            # college breakdown info
            'college_breakdown_info': college_breakdown_info,
            # department breakdown info
            'department_breakdown_info': department_breakdown_info,
            # 
            'top_authors_by_citations': top_authors_by_citations,
            # 
            'total_pubs_for_top_3_schools': total_pubs_for_top_3_schools,
            # top 7 journals
            'top_journals_json': json.dumps(journals_data),
            'schools_publications_json': json.dumps(schools_pub_data),
            
        }
        return render(request, self.template_name, context)