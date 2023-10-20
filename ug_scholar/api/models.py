import json

from django.db import models


class Publication(models.Model):
    '''Publication model - stores publication/article details'''
    title = models.CharField(max_length=500)
    link = models.CharField(max_length=500, blank=True, null=True)
    year = models.IntegerField()
    citation_id = models.CharField(max_length=100, blank=True, null=True)
    authors = models.CharField(max_length=500, blank=True, null=True)
    journal = models.CharField(max_length=500, blank=True, null=True)
    citations = models.IntegerField(unique=False)
    
    def get_author_name(self) -> str:
        author = Author.objects.filter(publications=self).first()
        if author:
            return author.profile.name or author.profile.scholar_id
        else:
            return "Anonymous"

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'publication'
        verbose_name_plural = 'publications'
        ordering = ['-year']


class Profile(models.Model):
    '''Profile model - stores profile details of authors/scholars'''
    name = models.CharField(max_length=200, blank=True, null=True)
    scholar_id = models.CharField(max_length=50)
    affiliation = models.CharField(max_length=200, blank=True, null=True)
    thumbnail = models.CharField(max_length=200, blank=True, null=True)
    interests = models.CharField(max_length=3000, blank=True, null=True)
    statistics = models.CharField(max_length=3000, blank=True, null=True)
    rank = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    college = models.CharField(max_length=200,  blank=True, null=True)
    school = models.CharField(max_length=200, blank=True, null=True)
    department = models.CharField(max_length=200, blank=True, null=True)
    
    def get_author_hindex(self) -> int:
        try:
            if self.statistics:
                stats = json.loads(self.statistics)
                if stats is None:
                    return 0
                citations = stats[0]['citations']['all']
                h_index = stats[1]['h_index']['all']
                print("Citations and hindex", citations, h_index)
                papers = list(range(1, h_index + 1))
                papers.reverse()
            
                for i, paper in enumerate(papers):
                    if paper <= citations:
                        return paper
            
            return 0  # If no h-index is found
        except (KeyError, json.JSONDecodeError, IndexError) as e:
            print("Error in h-index", e)
            return 0  
    
    def get_author_i10index(self) -> int:
        try:
            if self.statistics:
                stats = json.loads(self.statistics)
                if stats is None:
                    return 0
                i10_index = stats[2]['i10_index']['all']
                return i10_index
            else:
                return 0  # Handle the case where statistics is None
        except (KeyError, json.JSONDecodeError, IndexError):
            return 0 
    
    def get_author_publications(self) -> int:
        '''Returns all publications of an author'''
        author = Author.objects.filter(profile=self).first()
        return author.publications.count()
    
    def get_author_citations(self) -> int:
        '''Returns all author citations from all author publications'''
        author = Author.objects.filter(profile=self).first()
        publications = author.publications.all()
        citations = publications.aggregate(models.Sum('citations'))['citations__sum'] #noqa
        return citations
    
    def abbreviate_college(self) -> str:
        '''Abbreviates the name of the college'''
        if self.name:
            college_names = self.college.split()
            if len(college_names) > 1:
                initials = [name[0] for name in college_names[:-1]]
                return initials.upper()
            else:
                return college_names[0].upper()
        else:
            return self.scholar_id
        
    def abbreviate_school(self) -> str:
        '''Abbreviates the name of the school'''
        if self.name:
            school_names = self.school.split()
            if len(school_names) > 1:
                initials = [name[0] for name in school_names[:-1]]
                return initials.upper()
            else:
                return school_names[0].upper()
        else:
            return self.scholar_id
        
    def abbreviate_department(self) -> str:
        '''Abbreviates the name of the department'''
        if self.name:
            department_names = self.department.split()
            if len(department_names) > 1:
                initials = "".join([name[0] for name in department_names])
                return initials.upper()
            else:
                return department_names[0][0].upper() + department_names[-1][0].upper()
        else:
            return self.scholar_id
        
        
    def __str__(self):
        return self.name or self.scholar_id

    class Meta:
        db_table = 'profile'
        verbose_name_plural = 'profiles'
        ordering = ['name']


class Author(models.Model):
    '''Author model - stores author details'''
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    publications = models.ManyToManyField(Publication, related_name="publications") #noqa

    def __str__(self):
        return self.profile.name or self.profile.scholar_id

    class Meta:
        db_table = 'author'
        verbose_name_plural = 'authors'
        ordering = ['profile__name']
