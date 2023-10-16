import json

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Author, Profile, Publication
from ug_scholar.library.utils_functions import (get_author_ids,
                                                scrape_author_data)


class OverviewAPI(APIView):
    '''Gives the overview of the UG Scholar API'''
    def get(self, request, *args, **kwargs):
        return Response({
            "message": "Welcome to the UG Scholar API",
            "status": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)
 
 
class UpdatedDBAPIView(APIView):
    '''Used to updated data in database'''
     
    def post(self, request, *args, **kwargs):
        profiles = Profile.objects.all()
        scholar_ids = []
        # get all scholar ids from db
        for profile in profiles:
            scholar_ids.append(profile.scholar_id)
            
        # scrape author data for each author(id)
        for scholar_id in scholar_ids:
            scraped = scrape_author_data(scholar_id)
            author_data = scraped["author_data"]
            # check if profile exists  - if not create profile
            profile = Profile.objects.filter(scholar_id=scholar_id).first()
            if profile is None:
                # skip if profile is none
                continue
            author = Author.objects.filter(profile=profile).first()
            # update profile before proceeding
            profile.name = author_data['name']
            profile.affiliation = author_data['affiliations']
            profile.thumbnail = author_data['thumbnail']
            profile.interests = json.dumps(author_data['interests'])
            profile.statistics = json.dumps(author_data['cited_by_table'])
            profile.rank = author_data['rank']
            profile.email = author_data['email']
            profile.college = author_data['college']
            profile.school = author_data['school']
            profile.department = author_data['department']
            profile.save()
            if author is None:
                # create a new author is profile exists but is not tired to an author
                author = Author.objects.create(profile=profile)
                author.save()
            # get all authors articles/publications
            author_articles = scraped["author_articles"]
            # create publications
            for article in author_articles:
                publication = Publication.objects.filter(citation_id=article['article_citation_id']).first()  # noqa
                # Handle null citation values
                citation_value = article['article_cited_by_value']
                article_year = article['article_year']
                if citation_value is None or citation_value == "":
                    citation_value = 0
                else:
                    # make sure citation value is an integer
                    citation_value = int(citation_value)
                if article_year is None or article_year == "":
                    article_year = 1900
                else:
                    # make sure article year is a number
                    article_year = int(article_year)
                    
                if publication is None:
                    # create new publication
                    publication = Publication.objects.create(
                        title=article['article_title'],
                        year=article_year,
                        link=article['article_link'],
                        citation_id=article['article_citation_id'],
                        authors=article['article_authors'],
                        journal=article['article_publication'],
                        citations=citation_value,
                    )
                    publication.save()
                else:
                    # publication exists - update publication
                    publication.title = article['article_title']
                    publication.year = article_year
                    publication.link=article['article_link'],
                    publication.citation_id = article['article_citation_id']
                    publication.authors = article['article_authors']
                    publication.journal = article['article_publication']
                    publication.citations = citation_value
                    publication.save()
                # add publication to author if not already added
                if publication not in author.publications.all():
                    author.publications.add(publication)
                    author.save()
                else:
                    # remove the old publication and add the new one
                    author.publications.remove(publication)
                    author.publications.add(publication)
                    author.save()             
        return Response({
            "message": "Database populated successfully",
            "status": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)
            
        
        
        
class PopulateDBAPIView(APIView):
    '''Used to scrape data and populate the db'''
    def post(self, request, *args, **kwargs):
        infos = get_author_ids()
        
        for info in infos:
            scraped = scrape_author_data(info['author_id'])
            author_data = scraped["author_data"]
            # check if profile exists  - if not create profile
            profile = Profile.objects.filter(scholar_id=info['author_id']).first()  # noqa
            if profile is None:
                profile = Profile.objects.create(
                    name=author_data['name'],
                    scholar_id=info['author_id'],
                    affiliation=author_data['affiliations'],
                    thumbnail=author_data['thumbnail'],
                    interests=json.dumps(author_data['interests']),
                    statistics=json.dumps(author_data['cited_by_table']),
                    rank=info['rank'],
                    email=info['email'],
                    college=info['college'],
                    school=info['school'],
                    department=info['department'],
                )
                profile.save()
           
            # check if author exists. if not create author
            author = Author.objects.filter(profile=profile).first()
            if author is None:
                author = Author.objects.create(profile=profile)
                author.save()
            # get all authors articles/publications
            author_articles = scraped["author_articles"]
            
            # create publications
            for article in author_articles:
                publication = Publication.objects.filter(citation_id=article['article_citation_id']).first()  # noqa
                # Handle null citation values
                citation_value = article['article_cited_by_value']
                article_year = article['article_year']
                if citation_value is None or citation_value == "":
                    citation_value = 0
                else:
                    # make sure citation value is an integer
                    citation_value = int(citation_value)
                if article_year is None or article_year == "":
                    article_year = 1900
                else:
                    # make sure article year is a number
                    article_year = int(article_year)
                    
                if publication is None:
                    # create new publication
                    publication = Publication.objects.create(
                        title=article['article_title'],
                        year=article_year,
                        link=article['article_link'],
                        citation_id=article['article_citation_id'],
                        authors=article['article_authors'],
                        journal=article['article_publication'],
                        citations=citation_value,
                    )
                    publication.save()
                else:
                    # update publication
                    publication.title = article['article_title']
                    publication.year = article_year
                    publication.link=article['article_link'],
                    publication.citation_id = article['article_citation_id']
                    publication.authors = article['article_authors']
                    publication.journal = article['article_publication']
                    publication.citations = citation_value
                    publication.save()
                # add publication to author if not already added
                if publication not in author.publications.all():
                    author.publications.add(publication)
                    author.save()
                else:
                    # remove the old publication and add the new one
                    author.publications.remove(publication)
                    author.publications.add(publication)
                    author.save()             
        return Response({
            "message": "Database populated successfully",
            "status": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)