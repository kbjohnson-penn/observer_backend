from django.db import models
import os

DEPARTMENT_CHOICES = [
    ('cardiology', 'Cardiology'),
    ('neurology', 'Neurology'),
    ('orthopedics', 'Orthopedics'),
    # Add more departments as needed
]

VISIT_TYPE_CHOICES = [
    ('VAT', 'Video + Audio + Transcript'),
    ('V', 'Video Only'),
    ('A', 'Audio Only'),
    ('T', 'Transcript Only'),
    ('OTH', 'Others'),
]

class Department(models.Model):
    department_name = models.CharField(max_length=200, choices=DEPARTMENT_CHOICES)

    def __str__(self):
        return self.department_name.capitalize()

class Encounter(models.Model):
    case_id = models.CharField(max_length=200, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    visit_type = models.CharField(max_length=10, choices=VISIT_TYPE_CHOICES, default='VAT')
    audio = models.FileField(upload_to='audio/', blank=True, null=True)
    video = models.FileField(upload_to='video/', blank=True, null=True)
    transcript = models.FileField(upload_to='transcript/', blank=True, null=True)
    other_files = models.FileField(upload_to='other_files/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        try:
            existing = Encounter.objects.get(case_id=self.case_id)
            self.pk = existing.pk  # set the primary key to the existing object to update it
        except Encounter.DoesNotExist:
            pass  # if the Encounter does not exist, do nothing and proceed with the save

        for field_name in ['audio', 'video', 'transcript', 'other_files']:
            field = getattr(self, field_name)
            if field:
                filename = self.case_id + os.path.splitext(field.name)[1]
                field.save(filename, field.file, save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.case_id