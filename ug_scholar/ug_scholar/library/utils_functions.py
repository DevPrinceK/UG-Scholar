import json
import re
from urllib.parse import parse_qsl, urlsplit

import pandas as pd
from serpapi import GoogleSearch

from accounts.models import UserLog


def get_author_ids(csv_file=None) -> list:
    '''extracts all author IDs and relevant data from the CSV and returns them as a list'''
    if csv_file == None:
        df = pd.read_csv("ug_scholar\library\one-100.csv")
    else:
        df = pd.read_csv(csv_file)
    scholar_info = df[['scholar', 'email', "college", 'school', 'department', 'rank']] #noqa
    scholar_info_dict = scholar_info.to_dict(orient="records")
    author_relevant_info = []

    # extract the author IDs using regex
    for record in scholar_info_dict:
        match = re.search(r'user=([\w-]+)', str(record["scholar"]))
        if match:
            author_id = match.group(1)
            author_relevant_info.append({
                "author_id": author_id,
                "email": record['email'],
                "college": record['college'],
                "school": record['school'],
                "department": record['department'],
                "rank": record['rank'],
            })
        else:
            pass
    print("Now Printing All Relevant Author Info")
    print(author_relevant_info)
    return author_relevant_info



def scrape_author_data(author_id: str = "Tpwr9vwAAAAJ") -> dict:
    '''scrapes individual author data from Google Scholar using the author ID'''
    # NEW KEYS - STUDENTS
    STUDENT_1 = "a9695dae3cd22abbc740192cdd99753943f351225bd1f5e73564ae5e43775a7a" #noqa
    STUDENT_2 = "6f6067a532c22da3bcba266193fc04877d8b0726fa7b7f84afd823853057da9b" #noqa
    STUDENT_3 = "" #noqa
    STUDENT_4 = "" #noqa
    STUDENT_5 = "" #noqa
    
    MINE = "3123fa10ceadfe468d745f03e0df1a305b676fd829965219ec62450692a4cb54" #noqa
    
    BECCA = "e90b4032276c7c0fd1a742f9c639cc98fcb71810327db1b0fe83a5b130a8e791" #noqa
    BERNICE = "6880fb5b314bbba29603f694bc4de1f39ead09655b10f41d45852cffa13e32c2" #noqa
    TAWIAH = "ded3dabcba3e4aee20e120d9b923f19e70c7a11aa4d0740ea712e737cc1e904f" #noqa
    STIGAR = "4f940edc13eccb5c0f58327859400c2daab057d5fb1aadfdd4cc1ad9d28cbf89" #noqa
    ERNEST = "7c6cd4ed1b4a2a61f435b25f44bda533e9814853ca5e53ca29f5940088354673" #noqa
    STEPH = "811d5d3af6e8f0ec4faaa72b09d57e2c3aa85d96aa4141aa720fcffa4e224746" #noqa
    
    params = {
        "api_key": BECCA,
        "engine": "google_scholar_author",
        "hl": "en",
        "author_id": author_id  # "Tpwr9vwAAAAJ" - default
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    author_results_data = {
        "author_data": {},
        "author_articles": []
    }

    if results.get("error") or results == None or results == {}:
        print(results["error"])
        return author_results_data
    
    author_results_data["author_data"]["name"] = results.get("author").get("name") if results.get("author") else None #noqa
    author_results_data["author_data"]["email"] = results.get("author").get("email") if results.get("author") else None   #noqa
    author_results_data["author_data"]["website"] = results.get("author").get("website") if results.get("author") else None  #noqa
    author_results_data["author_data"]["interests"] = results.get("author").get("interests") if results.get("author") else None  #noqa
    author_results_data["author_data"]["affiliations"] = results.get("author").get("affiliations") if results.get("author") else None  #noqa
    author_results_data["author_data"]["thumbnail"] = results.get("author").get("thumbnail") if results.get("author") else None  #noqa
    author_results_data["author_data"]["cited_by_table"] = results.get("cited_by", {}).get("table")  #noqa
    author_results_data["author_data"]["cited_by_graph"] = results.get("cited_by", {}).get("graph") #noqa
    author_results_data["author_data"]["public_access_link"] = results.get("public_access", {}).get("link") #noqa
    author_results_data["author_data"]["public_access_available"] = results.get("public_access", {}).get("available")  #noqa
    author_results_data["author_data"]["public_access_not_available"] = results.get("public_access", {}).get("not_available")  #noqa
    author_results_data["author_data"]["co_authors"] = results.get("co_authors")  #noqa

    # extracting all author articles
    while True:
        results = search.get_dict()

        for article in results.get("articles", []):

            print(f"Extracting article: {article.get('title')} ")

            author_results_data["author_articles"].append({
                "article_title": article.get("title"),
                "article_link": article.get("link"),
                "article_year": article.get("year"),
                "article_citation_id": article.get("citation_id"),
                "article_authors": article.get("authors"),
                "article_publication": article.get("publication"),
                "article_cited_by_value": article.get("cited_by", {}).get("value"),
                "article_cited_by_link": article.get("cited_by", {}).get("link"),
                "article_cited_by_cites_id": article.get("cited_by", {}).get("cites_id"),
            })

        if "next" in results.get("serpapi_pagination", []):
            search.params_dict.update(
                dict(parse_qsl(urlsplit(results.get("serpapi_pagination").get("next")).query)))
        else:
            break

    print(json.dumps(author_results_data, indent=2, ensure_ascii=False))
    print(f"Done. Extracted {len(author_results_data['author_articles'])-1} articles.") #noqa
    
    return author_results_data



def log_user_action(user, action):
    '''logs user actions'''
    UserLog.objects.create(user=user, action=action)
    return True