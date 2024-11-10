from django.db import models

class Category(models.Model):
    category_number = models.CharField(max_length=10)
    category_name = models.CharField(max_length=255)
    summary = models.TextField()
    total_credits_available = models.IntegerField()

class AssessmentIssue(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    issue_number = models.CharField(max_length=10)
    issue_name = models.CharField(max_length=255)
    aim = models.TextField()

class AssessmentCriteria(models.Model):
    assessment_issue = models.ForeignKey(AssessmentIssue, on_delete=models.CASCADE)
    criteria_id = models.CharField(max_length=10)
    name = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=50)
