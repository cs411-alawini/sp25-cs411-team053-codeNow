import csv
from django.core.management.base import BaseCommand
from app.models import Company, Location, Skill, JobPortal, JobPosting
from datetime import datetime
from tqdm import tqdm # for a progress bar so I can see the 

BATCH_SIZE = 100 # create a batch size for uploading to GCP

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
            
            for i, row in tqdm(enumerate(reader), total=2000): #total set to 1000 
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
                
                # Always create new Location (Allow duplicate location entries)
                location = Location.objects.create(
                    city=row['location'].strip(),
                    country=row['Country'].strip(),
                    latitude=float(row.get('latitude', 0.0)),
                    longitude=float(row.get('longitude', 0.0))
                )
                
                # Always create new Company (Allow duplicate company entries)
                company = Company.objects.create(
                    name=row['Company'].strip(),
                    size=row.get('Company Size', '').strip(),
                    profile=row.get('Company Profile', '').strip(),
                    contact_person=row.get('Contact Person', '').strip(),
                    contact_info=row.get('Contact', '').strip()
                )
                
                # Always create new Job Portal (Allow duplicate job portal entries)
                portal = None
                if row.get('Job Portal'):
                    portal = JobPortal.objects.create(name=row['Job Portal'].strip())
                
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
                
                # Store skills for this job
                skills = [s.strip() for s in row.get('skills', '').split(',') if s.strip()]
                job_skills_map[current_job_id] = skills

                # Batch insert Job Postings
                if len(job_posting_list) >= BATCH_SIZE:
                    JobPosting.objects.bulk_create(job_posting_list)
                    job_posting_list.clear()
            
            # Insert any remaining Job Postings
            if job_posting_list:
                JobPosting.objects.bulk_create(job_posting_list)
            
        
        # Second Pass: Assign Skills (Many-to-Many)
        for job_id, skill_names in tqdm(job_skills_map.items(), desc="Assigning Skills"):
            try:
                job = JobPosting.objects.get(job_id=job_id)
            except JobPosting.DoesNotExist:
                continue
            for skill_name in skill_names:
                skill_obj, _ = Skill.objects.get_or_create(name=skill_name)
                job.skills.add(skill_obj)
        

