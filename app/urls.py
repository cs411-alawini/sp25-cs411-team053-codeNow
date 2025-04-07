from django.urls import path, include
from . import views
urlpatterns = [
    #path('jobs/', views.get_jobs, name='get_jobs'),  # Fetch job listings
    #path('job/<int:job_id>/', views.get_job_detail, name='get_job_detail'),  # Single job detail
    #path('employers/', views.get_employers, name='get_employers'),  # Fetch all employers
    #path('employer/<int:employer_id>/', views.get_employer_detail, name='get_employer_detail'),  # Single employer detail
]

#MAP URLS TO VIEWS


urlpatterns = [
    # ... your other URL patterns ...
    path('', include('careercompass_backend.urls')),
]