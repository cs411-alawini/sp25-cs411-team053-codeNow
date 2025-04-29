from django.urls import path, include
from django.contrib import admin
from . import views
urlpatterns = [
    #path('jobs/', views.get_jobs, name='get_jobs'),  # Fetch job listings
    #path('job/<int:job_id>/', views.get_job_detail, name='get_job_detail'),  # Single job detail
    #path('employers/', views.get_employers, name='get_employers'),  # Fetch all employers
    #path('employer/<int:employer_id>/', views.get_employer_detail, name='get_employer_detail'),  # Single employer detail
]


urlpatterns = [
    #path('api/create-job-posting/', views.create_job_posting, name='create_job_posting'),
    #path('api/deactivate-inactive-companies/', views.deactivate_inactive_companies, name='deactivate_inactive_companies'),
    #path('api/get-active-company-jobs/', views.get_active_company_jobs_above_average, name='get_active_company_jobs_above_average'),
    path('api/search_jobs/', views.search_jobs, name='search_jobs'),
]
#MAP URLS TO VIEWS


urlpatterns = [
    path('admin/',  admin.site.urls),
    path('api/',    include('app.urls')),  
]