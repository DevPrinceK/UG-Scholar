import csv
import os
import json
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import View

from api.models import Author, Profile, Publication
from dashboard.forms import AuthorProfileForm
from dashboard.views import publications
from dashboard.views.publications import PublicationsView
from ug_scholar.library.constants import UG, SampleAuthorData
from ug_scholar.library.decorators import AdministratorsOnly
from ug_scholar.library.utils_functions import get_author_ids, log_user_action, scrape_author_data


class AuthorsView(View):
    '''Renders the authors profiles page - profiles page'''
    template_name = 'pages/authors.html'

    def get(self, request):
        ug = UG()
        authors = Profile.objects.all()

        schools = ug.get_schools()
        departments = ug.get_departments()
        colleges = ug.get_colleges()
        ranks = ug.get_ranks()

        context = {
            'authors': authors,
            'colleges': colleges,
            'schools': schools,
            'departments': departments,
            'ranks': ranks,
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
            log_user_action(user, "Tried to create author profile with an already existing scholar id") #noqa
            messages.info(request, "Author Profile Already Exists")
            return redirect('dashboard:authors')
        # author does not exist, create new author profile
        print(f"Scrapping author data for profile: {scholar_id}")
        try:
            scraped = scrape_author_data(scholar_id)
        except Exception as e:
            messages.info(request, f"Error occured: {e}")
            return redirect('dashboard:authors')
        author_data = scraped["author_data"]
        form = AuthorProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            if author_data is not None or author_data != {}:
                profile.name = author_data['name']
                profile.affiliation = author_data['affiliations']
                profile.thumbnail = author_data['thumbnail']
                profile.interests = json.dumps(author_data['interests'])
                profile.statistics = json.dumps(author_data['cited_by_table'])
            profile.save()
            author = Author.objects.create(profile=profile)
            author.save()
            log_user_action(user, f"Created author profile: {profile.name} successfully") #noqa
            messages.success(request, "Author Profile Created Successfully")
            return redirect('dashboard:authors')
        else:
            for field, error in form.errors.items():
                message = f"{field.title()}: {strip_tags(error)}"
                log_user_action(user, f"Tried to create author profile but error occured: {message}") #noqa
                messages.info(request, message)
                return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


class BulkUploadAuthorView(View):
    '''Used to implement bulk upload of author profiles: POST request'''

    def get(self, request):
        user = request.user
        log_user_action(user, "Tried to access bulk upload author form using get request")  # noqa
        return redirect('dashboard:authors')

    def post(self, request):
        updated_authors = 0
        updated_publications = 0
        csv_file = request.FILES.get('csv_file')
        try:
            infos = get_author_ids(csv_file)
        except Exception as e:
            messages.info(request, f"Error occured: {e}")
            return redirect('dashboard:authors')

        for info in infos:
            old_profile = Profile.objects.filter(scholar_id=info['author_id']).first()  # noqa
            if old_profile is not None:
                print(f"Skipping Profile: {old_profile.name}")
                print("+==================================================+")
                print("+==================================================+")
                continue
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
                print(f"Created profile: {profile.name}")
            
            # check if author exists. if not create author
            author = Author.objects.filter(profile=profile).first()
            if author is None:
                author = Author.objects.create(profile=profile)
                author.save()
            # get all authors articles/publications
            author_articles = scraped["author_articles"]

            print(f"Updating author: {author.profile.name}")
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
                    publication.link = article['article_link'],
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
                # update the count of updated publications and authors
                updated_publications += 1
            updated_authors += 1
        messages.success(request, f"Updated {updated_authors} authors with {updated_publications} publications")  # noqa
        log_user_action(request.user, "Updated the system using bulk author upload successfully")  # noqa
        return redirect('dashboard:authors')


class DownloadSampleBulkFileView(View):
    '''Used to download a sample csv file for bulk upload'''

    def get(self, request):
        sample_data = SampleAuthorData().get_author_sample_data()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bulk_author_upload_sample.csv"'

        writer = csv.writer(response)
        writer.writerow(['scholar', 'email', "college", 'school', 'department', 'rank']) # noqa
        
        for data in sample_data:
            writer.writerow([data['scholar'], data['email'], data['college'], data['school'], data['department'], data['rank']])
            
        return response
