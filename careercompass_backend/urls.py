"""
URL configuration for careercompass_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/skills/', views.list_skills, name='skill-list'),
    path('api/jobportals/', views.list_jobportals, name='jobportal-list'),
    path('api/recent-job-postings/', views.recent_job_postings, name='recent-job-postings'),
    path('api/jobposting/create/', views.create_job_posting),
    path('api/search_jobs/', views.search_jobs, name='search-jobs'), 
    path('api/jobposting/<int:id>/', views.job_posting_detail),
    path('api/company/<int:company_id>/jobs/',
         views.get_company_jobs,         name='company-jobs'),
]