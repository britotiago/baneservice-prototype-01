from django.contrib import admin
from .models import Category, AssessmentIssue, AssessmentCriteria

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_number', 'category_name', 'summary', 'total_credits_available']

class AssessmentIssueAdmin(admin.ModelAdmin):
    list_display = ['issue_number', 'issue_name', 'aim', 'category']
    list_filter = ['category']  # Adding a filter by category
    search_fields = ['issue_name', 'issue_number']  # Enabling search by issue name and number

class AssessmentCriteriaAdmin(admin.ModelAdmin):
    list_display = ['criteria_id', 'name', 'description', 'type', 'assessment_issue']
    list_filter = ['assessment_issue', 'type']  # Adding filters
    search_fields = ['name', 'criteria_id']  # Enabling search by criteria name and ID

admin.site.register(Category, CategoryAdmin)
admin.site.register(AssessmentIssue, AssessmentIssueAdmin)
admin.site.register(AssessmentCriteria, AssessmentCriteriaAdmin)
