from django.db import models

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=1000)
    size = models.CharField(max_length=100)
    profile = models.TextField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    contact_info = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
    
class Location(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"{self.city}, {self.country}"
    
class Skill(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name

class JobPortal(models.Model):
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name

    
class JobPosting(models.Model):
    job_id = models.BigIntegerField(unique=True)
    title = models.CharField(max_length=1000)
    role = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    qualifications = models.CharField(max_length=255, blank=True)
    experience = models.CharField(max_length=255, blank=True)
    work_type = models.CharField(max_length=50)
    salary_range = models.CharField(max_length=100)
    posting_date = models.DateField()
    preference = models.CharField(max_length=50, blank=True)
    benefits = models.TextField(blank=True)
    skills = models.ManyToManyField(Skill, related_name='job_postings')
    job_portal = models.ForeignKey(JobPortal, on_delete=models.SET_NULL, null=True, blank=True)



    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
