from django.urls import path
from . import views

urlpatterns = [
    path('criteria/', views.audit_criteria_list, name='audit_criteria_list'),
    path('criteria/<str:criteria_id>/', views.audit_criteria_detail, name='audit_criteria_detail'),
    path('criteria/<str:criteria_id>/projects/', views.projects_by_criteria, name='projects_by_criteria'),
    path('criteria/<str:criteria_id>/guidance/', views.guidance_for_criteria, name='guidance_for_criteria'),
    path('criteria/<str:criteria_id>/evidence/', views.evidence_for_criteria, name='evidence_for_criteria'),
    path('criteria/<str:criteria_id>/minimum-standards/', views.minimum_standards_for_criteria, name='minimum_standards_for_criteria'),
    path('criteria/<str:criteria_id>/prerequisites/', views.prerequisites_for_criteria, name='prerequisites_for_criteria'),
    path('criteria/<str:criteria_id>/category-weighting/', views.category_weighting_for_criteria, name='category_weighting_for_criteria'),
    path('upload/', views.upload_data_and_files, name='upload_data_and_files'),
    path('process-criteria-data/', views.process_criteria_data, name='process_criteria_data'),
    path('task-status/<str:task_id>/', views.check_task_status, name='check_task_status'),
]
