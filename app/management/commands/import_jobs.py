import csv
from django.core.management.base import BaseCommand
from app.models import Company, Location, Skill, JobPortal, JobPosting
from datetime import datetime
from tqdm import tqdm # for a progress bar so I can see the 

BATCH_SIZE = 100 # create a batch size for uploading to GCP

import re

def split_skills_by_capital(text):
    return re.findall(r'(?:[A-Z][a-z]+(?: [a-z]+)*)', text or '')


class Command(BaseCommand):
    help = "Import jobs from job_sample.csv into the database"

    def handle(self, *args, **kwargs):
        # Set to track job IDs processed in this run
        seen_job_ids = set()
        
        # Map each job_id to its list of skill names
        job_skills_map = {}
        job_posting_list = []

        with open('app/job_sample.csv', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            
            for i, row in tqdm(enumerate(reader), total=2000): #total set to 2000
                # Validate Job Id
                try:
                    current_job_id = int(row['Job Id']) 
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"Skipping row {i+1}: Invalid Job Id")) 
                    continue
                
                # Skip if already exists in DB or processed in this run
                if JobPosting.objects.filter(job_id=current_job_id).exists():
                    self.stdout.write(self.style.WARNING(f"Skipping row {i+1}: Job Id {current_job_id} already exists in DB"))
                    continue
                if current_job_id in seen_job_ids:
                    self.stdout.write(self.style.WARNING(f"Skipping duplicate Job Id {current_job_id} in CSV at row {i+1}"))
                    continue
                seen_job_ids.add(current_job_id)
                
                # Validate Job Posting Date
                job_posting_date = row.get('Job Posting Date', '').strip()
                if not job_posting_date:
                    self.stdout.write(self.style.WARNING(f"Skipping row {i+1}: Missing Job Posting Date"))
                    continue 
                try:
                    posting_date = datetime.strptime(job_posting_date, '%Y-%m-%d')
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"Skipping row {i+1}: Invalid Job Posting Date"))
                    continue  
                
                # Create new location or use existing one
                location, _ = Location.objects.get_or_create(
                    city=row['location'].strip(),
                    country=row['Country'].strip(),
                    latitude=float(row.get('latitude', 0.0)),
                    longitude=float(row.get('longitude', 0.0))
                )
                
                # Create new company or use existing one
                company, _ = Company.objects.get_or_create(
                    name=row['Company'].strip(),
                    defaults={
                        'size': row.get('Company Size', '').strip(),
                        'profile': row.get('Company Profile', '').strip(),
                        'contact_person': row.get('Contact Person', '').strip(),
                        'contact_info': row.get('Contact', '').strip()
                    }
                )
                
                # Create new job portal or use existing one
                portal = None
                if row.get('Job Portal'):
                    portal, _ = JobPortal.objects.get_or_create(name=row['Job Portal'].strip())
                # Create the Job Posting (unsaved for performance with batching)
                job_posting = JobPosting(
                    job_id=current_job_id,
                    title=row['Job Title'].strip(),
                    role=row['Role'].strip(),
                    description=row['Job Description'].strip(),
                    responsibilities=row.get('Responsibilities', '').strip(),
                    qualifications=row.get('Qualifications', '').strip(),
                    experience=row.get('Experience', '').strip(),
                    work_type=row.get('Work Type', '').strip(),
                    salary_range=row.get('Salary Range', '').strip(),
                    posting_date=posting_date,
                    preference=row.get('Preference', '').strip(),
                    benefits=row.get('Benefits', '').strip(),
                    company=company,
                    location=location,
                    job_portal=portal
                )
                job_posting_list.append(job_posting)
                
                skills = split_skills_by_capital(row.get('skills', ''))
                job_skills_map[current_job_id] = skills
                if i < 50:  # Only for first few entries
                    print(f"Parsed skills at row {i+1}: {skills}") 

                # Batch insert Job Postings
                if len(job_posting_list) >= BATCH_SIZE:
                    for job in job_posting_list:
                        job.save()

                        # Link skills right after saving the job
                        skills = job_skills_map.get(job.job_id, [])
                        for skill_name in skills:
                            skill_name = skill_name.strip()
                            if skill_name:
                                skill_obj, _ = Skill.objects.get_or_create(name=skill_name)
                                job.skills.add(skill_obj)

                    job_posting_list.clear()
            
            # Insert any remaining Job Postings
            if job_posting_list:
                for job in job_posting_list:
                    job.save()

                    skills = job_skills_map.get(job.job_id, [])
                    for skill_name in skills:
                        skill_name = skill_name.strip()
                        if skill_name:
                            skill_obj, _ = Skill.objects.get_or_create(name=skill_name)
                            job.skills.add(skill_obj)

