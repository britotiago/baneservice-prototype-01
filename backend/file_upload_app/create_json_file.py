import json
import os
from django.conf import settings
from datetime import date

def load_json_file(file_path):
    """Loads a JSON file and returns its contents."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json_file(data, file_path):
    """Saves a Python dictionary to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def merge_json_data(audit_data, project_data):
    """Merges data from two JSON sources into a new structure."""
    merged_data = {
        'project_name': project_data['projectName'],
        'breeam_entrepreneur_responsible': project_data['breeamEntrepreneurResponsible'],
        'breeam_civil_engineer_responsible': project_data['breeamCivilEngineerResponsible'],
        'breeam_assessor': project_data['breeamAssessor'],
        'audit_criteria': project_data['auditCriteria'],
        'premise': project_data['premise'],
        'total_points': audit_data['total_points'],
        'prepared_by': project_data['preparedBy'],
        'date_created': date.today().strftime("%d.%m.%Y"),
        'compliance_description': audit_data['compliance_description'],
        'attachments': audit_data['attachments']
    }
    return merged_data

def merge_audit_and_project_data():
    # File paths
    audit_file_path = os.path.join(settings.MEDIA_ROOT, 'final_output.json')
    project_file_path = os.path.join(settings.MEDIA_ROOT, 'data.json')
    output_file_path = os.path.join(settings.MEDIA_ROOT, 'merged_output.json')

    # Load data from files
    audit_data = load_json_file(audit_file_path)
    project_data = load_json_file(project_file_path)

    # Merge the data
    merged_data = merge_json_data(audit_data, project_data)

    # Save the merged data to a new file
    save_json_file(merged_data, output_file_path)
    print(f"Merged data saved to {output_file_path}")
