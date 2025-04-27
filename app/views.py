# app/views.py

import json
import random
from datetime import timedelta

from django.db import connection, DatabaseError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from rest_framework import generics

from .models import Skill, JobPortal, JobPosting
from .serializers import (
    SkillSerializer,
    JobPortalSerializer,
    JobPostingSerializer,
)


geolocator = Nominatim(user_agent="careercompass")


class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer


class JobPortalListView(generics.ListAPIView):
    queryset = JobPortal.objects.all()
    serializer_class = JobPortalSerializer


class RecentJobPostingsView(generics.ListAPIView):
    serializer_class = JobPostingSerializer

    def get_queryset(self):
        cutoff = timezone.now().date() - timedelta(days=30)
        return (
            JobPosting.objects
            .filter(posting_date__gte=cutoff)
            .order_by('-posting_date')[:5]
        )


def _generate_unique_job_id():
    min_id, max_id = 10**15, 10**16 - 1
    with connection.cursor() as cur:
        while True:
            candidate = random.randint(min_id, max_id)
            cur.execute(
                "SELECT 1 FROM app_jobposting WHERE job_id = %s LIMIT 1",
                [candidate],
            )
            if cur.fetchone() is None:
                return candidate


def _get_or_create_company_id(name):
    with connection.cursor() as cur:
        cur.execute("SELECT id FROM app_company WHERE name = %s", [name])
        row = cur.fetchone()
        if row:
            return row[0]
        cur.execute(
            "INSERT INTO app_company (name, size, profile, contact_person, contact_info) "
            "VALUES (%s, '', '', '', '')",
            [name],
        )
        return cur.lastrowid


def _get_or_create_location_id(city, country):
    with connection.cursor() as cur:
        cur.execute(
            "SELECT id FROM app_location WHERE city = %s AND country = %s",
            [city, country],
        )
        row = cur.fetchone()
        if row:
            return row[0]

        try:
            loc = geolocator.geocode(f"{city}, {country}", timeout=5)
            lat, lon = (loc.latitude, loc.longitude) if loc else (None, None)
        except (GeocoderTimedOut, GeocoderServiceError):
            lat = lon = None

        cur.execute(
            "INSERT INTO app_location (city, country, latitude, longitude) "
            "VALUES (%s, %s, %s, %s)",
            [city, country, lat, lon],
        )
        return cur.lastrowid


@csrf_exempt
def create_job_posting(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # required fields
    for field in ('company_name', 'city', 'country', 'title', 'work_type', 'salary_range'):
        if not data.get(field):
            return JsonResponse({'error': f'Missing field: {field}'}, status=400)

    company_id = _get_or_create_company_id(data['company_name'].strip())
    location_id = _get_or_create_location_id(
        data['city'].strip(),
        data['country'].strip(),
    )
    job_id = _generate_unique_job_id()

    params = [
        job_id,
        data['title'],
        data.get('role', ''),
        data.get('description', ''),
        data.get('responsibilities', ''),
        data.get('qualifications', ''),
        data.get('experience', ''),
        data['work_type'],
        data['salary_range'],
        data.get('preference', ''),
        data.get('benefits', ''),
        company_id,
        location_id,
        data.get('job_portal_id'),
    ]

    try:
        with connection.cursor() as cur:
            cur.execute("""
                INSERT INTO app_jobposting
                (job_id, title, role, description, responsibilities,
                 qualifications, experience, work_type, salary_range,
                 posting_date, preference, benefits,
                 company_id, location_id, job_portal_id)
                VALUES (
                  %s, %s, %s, %s, %s,
                  %s, %s, %s, %s,
                  CURDATE(), %s, %s,
                  %s, %s, %s
                )
            """, params)
            new_pk = cur.lastrowid

            for skill_id in data.get('skills', []):
                cur.execute(
                    "INSERT INTO app_jobposting_skills (jobposting_id, skill_id) VALUES (%s, %s)",
                    [new_pk, skill_id],
                )
    except DatabaseError:
        return JsonResponse({'error': 'Database error on insert'}, status=400)

    return JsonResponse({'created_id': new_pk, 'job_id': job_id}, status=201)
