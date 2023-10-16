from django.urls import path

from . import views

app_name = 'api'
urlpatterns = [
    path('', views.OverviewAPI.as_view(), name='overview'),
    path('populate-db/', views.PopulateDBAPIView.as_view(), name='populate-db'),
]