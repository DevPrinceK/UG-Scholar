from django.urls import path
from . import views

app_name = "dashboard"

# dashboard
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]

# administrators
urlpatterns += [
    path('administrators/', views.AdministratorsView.as_view(), name='administrators'),
    path('create-administrator/', views.CreateUpdateAdministratorView.as_view(), name='create_administrator'),
]

# author and publications
urlpatterns += [
    path('authors/', views.AuthorsView.as_view(), name='authors'),
    path('create-author/', views.CreateUpdateAuthorView.as_view(), name='create_author'),
    path('publications/', views.PublicationsView.as_view(), name='publications'),
]

# breakdown
urlpatterns += [
    path('colleges/', views.CollegesView.as_view(), name='colleges'),
    path('faculties/', views.FacultiesView.as_view(), name='faculties'),
    path('departments/', views.DepartmentsView.as_view(), name='departments'),
]
