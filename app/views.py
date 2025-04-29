# app/views.py

import json
import random
import logging
logger = logging.getLogger(__name__)
from datetime import timedelta

from django.db import connection, DatabaseError
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from rest_framework import generics

from .models import Skill, JobPortal, JobPosting
from .serializers import (
    SkillSerializer,
    JobPortalSerializer,
)


geolocator = Nominatim(user_agent="careercompass")

@csrf_exempt
def list_skills(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    with connection.cursor() as cur:
        cur.execute("SELECT id, name FROM app_skill")
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]
        data = [dict(zip(cols, r)) for r in rows]

    return JsonResponse(data, safe=False, status=200)


@csrf_exempt
def list_jobportals(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    with connection.cursor() as cur:
        cur.execute("SELECT id, name FROM app_jobportal")
        rows = cur.fetchall()
        cols = [c[0] for c in cur.description]
        data = [dict(zip(cols, r)) for r in rows]

    return JsonResponse(data, safe=False, status=200)


@csrf_exempt
def recent_job_postings(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    cutoff_date = timezone.now().date() - timedelta(days=30)

    try:
        with connection.cursor() as cur:
            query = """
                SELECT
                  jp.id,
                  jp.job_id,
                  jp.title,
                  jp.role,
                  jp.work_type,
                  jp.salary_range,
                  jp.posting_date,
                  c.id   AS company_id,
                  c.name AS company_name
                FROM app_jobposting jp
                  JOIN app_company c
                    ON jp.company_id = c.id
                WHERE posting_date >= %s
                ORDER BY posting_date DESC
                LIMIT 5
            """
            cur.execute(query, [cutoff_date])
            results = cur.fetchall()
            columns = [col[0] for col in cur.description]
            job_list = [dict(zip(columns, row)) for row in results]

    except DatabaseError:
        return JsonResponse({'error': 'Database error during query'}, status=400)

    return JsonResponse(job_list, safe = False, status=200)


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
def deactivate_inactive_companies(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        with connection.cursor() as cur:
            cur.execute("START TRANSACTION;")

            cur.execute("""
                UPDATE app_company
                JOIN (
                    SELECT c.id
                    FROM app_company c
                    LEFT JOIN app_jobposting jp ON c.id = jp.company_id
                    WHERE jp.id IS NULL
                ) AS SubqueryTable
                ON app_company.id = SubqueryTable.id
                SET app_company.profile = 'Inactive';
            """)

            cur.execute("""
                DELETE FROM app_jobposting
                WHERE company_id IN (
                    SELECT id FROM app_company WHERE profile = 'Inactive'
                );
            """)

            cur.execute("COMMIT;")

    except DatabaseError:
        cur.execute("ROLLBACK;")
        return JsonResponse({'error': 'Database error during deactivation'}, status=400)

    return JsonResponse({'status': 'Inactive companies deactivated and jobs deleted'}, status=200)


@csrf_exempt
def get_active_company_jobs_above_average(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        company_id = data.get('company_id')
        if not company_id:
            return JsonResponse({'error': 'Missing company_id'}, status=400)

        with connection.cursor() as cur:
            cur.callproc('GetActiveCompanyJobsAboveAverage', [company_id])
            results = cur.fetchall()
            columns = [col[0] for col in cur.description]
            job_list = [dict(zip(columns, row)) for row in results]

    except DatabaseError:
        return JsonResponse({'error': 'Database error during procedure call'}, status=400)

    return JsonResponse({'jobs': job_list}, status=200)


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
    except DatabaseError as e:
        logger.error("Job insert failed: %s", e)

        return JsonResponse({'error': 'Database error on insert'}, status=400)

    return JsonResponse({'created_id': new_pk, 'job_id': job_id}, status=201)


@csrf_exempt
def search_jobs(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    keyword = request.GET.get('keyword', '').strip()
    if not keyword:
        return JsonResponse({'error': 'Missing keyword'}, status=400)

    pattern = f"%{keyword}%"
    with connection.cursor() as cur:
        cur.execute("""
            SELECT jp.id,
                jp.title,
                jp.company_id,
                c.name   AS company_name
            FROM app_jobposting jp
            JOIN app_company  c ON jp.company_id = c.id
            WHERE jp.title LIKE %s
        """, [pattern])
        rows    = cur.fetchall()
        cols    = [col[0] for col in cur.description]
        results = [dict(zip(cols, row)) for row in rows]

    return JsonResponse(results, safe=False)


@csrf_exempt
def get_job_detail(request, pk):
    if request.method != 'GET':
        return JsonResponse({'error':'Method not allowed'}, status=405)

    try:
        with connection.cursor() as cur:
            # fetch main job row + company + location + portal
            cur.execute("""
                SELECT
                  jp.id,
                  jp.job_id,
                  jp.title,
                  jp.role,
                  jp.description,
                  jp.responsibilities,
                  jp.qualifications,
                  jp.experience,
                  jp.work_type,
                  jp.salary_range,
                  jp.posting_date,
                  jp.preference,
                  jp.benefits,
                  c.id   AS company_id,
                  c.name AS company_name,
                  l.city AS location_city,
                  l.country AS location_country,
                  jp.job_portal_id
                FROM app_jobposting jp
                JOIN app_company  c ON jp.company_id = c.id
                JOIN app_location l ON jp.location_id = l.id
                WHERE jp.id = %s
            """, [pk])
            row = cur.fetchone()
            if not row:
                return JsonResponse({'error':'Not found'}, status=404)

            cols = [c[0] for c in cur.description]
            job = dict(zip(cols, row))

            # fetch skills
            cur.execute("""
                SELECT s.id, s.name
                  FROM app_skill s
                  JOIN app_jobposting_skills js
                    ON s.id = js.skill_id
                 WHERE js.jobposting_id = %s
            """, [pk])
            job['skills'] = [
                {'id': r[0], 'name': r[1]} for r in cur.fetchall()
            ]

    except DatabaseError:
        return JsonResponse({'error':'Database error'}, status=500)

    return JsonResponse(job, status=200)

@csrf_exempt
def get_company_jobs(request, company_id):
    if request.method != 'GET':
        return JsonResponse({'error':'Method not allowed'}, status=405)

    try:
        with connection.cursor() as cur:
            cur.execute("""
                SELECT id, job_id, title, posting_date
                  FROM app_jobposting
                 WHERE company_id = %s
                 ORDER BY posting_date DESC
                 LIMIT 10
            """, [company_id])
            cols = [c[0] for c in cur.description]
            jobs = [dict(zip(cols, row)) for row in cur.fetchall()]
    except DatabaseError:
        return JsonResponse({'error':'Database error'}, status=500)

    return JsonResponse(jobs, safe=False, status=200)

