from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('authors/', views.AuthorsView.as_view(), name='authors'),
    path('publications/', views.PublicationsView.as_view(), name='publications'),
    path('colleges/', views.CollegesView.as_view(), name='colleges'),
    path('faculties/', views.FacultiesView.as_view(), name='faculties'),
    path('departments/', views.DepartmentsView.as_view(), name='departments'),
    path('login/', views.LoginView.as_view(), name='login'),
]