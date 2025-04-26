from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta

from rest_framework import generics
from .models import Skill
from .models import JobPosting
from .serializers import SkillSerializer, JobPostingSerializer

class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

class RecentJobPostingsView(generics.ListAPIView):
    serializer_class = JobPostingSerializer

    def get_queryset(self):
        one_month_ago = timezone.now().date() - timedelta(days=1)
        return JobPosting.objects.filter(posting_date__gte=one_month_ago).order_by('-posting_date')[:5]
