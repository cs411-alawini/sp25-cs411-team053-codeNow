from rest_framework import serializers
from .models import Skill, JobPosting, JobPortal

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class JobPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = ['job_id', 'title', 'company', 'posting_date']

class JobPortalSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPortal
        fields = ['id', 'name']