from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
from django.http import JsonResponse
from .database_service import (
    get_db_connection,
    get_all_assessment_criteria,
    get_audit_criteria_by_id,
    get_projects_by_audit_criteria,
    get_guidance_for_audit_criteria,
    get_evidence_requirements_for_audit_criteria,
    get_minimum_standards_for_audit_criteria,
    get_prerequisites_for_audit_criteria,
    get_category_weighting_for_audit_criteria,
    get_assessment_criteria_credits,
    get_comprehensive_criteria_data,
)
from .generate_report import create_word_document, gather_data
import uuid
import time
from .ai_integration import (
    fetch_audit_criteria_data,
    initialize_audit_criteria,
    process_files_in_directory,
    send_file_chunks,
    calculate_total_points,
    finalize_summaries,
    save_response_as_json,
)
from .create_json_file import merge_audit_and_project_data

task_statuses = {}

@api_view(['GET'])
def audit_criteria_list(request):
    conn = get_db_connection()
    criteria = get_all_assessment_criteria(conn)
    return Response(criteria)

@api_view(['GET'])
def audit_criteria_detail(request, criteria_id):
    conn = get_db_connection()
    criteria = get_audit_criteria_by_id(conn, criteria_id)
    if criteria:
        return Response(criteria)
    return Response({"error": "Criteria not found"}, status=404)

@api_view(['GET'])
def projects_by_criteria(request, criteria_id):
    conn = get_db_connection()
    projects = get_projects_by_audit_criteria(conn, criteria_id)
    return Response(projects)

@api_view(['GET'])
def guidance_for_criteria(request, criteria_id):
    conn = get_db_connection()
    guidance = get_guidance_for_audit_criteria(conn, criteria_id)
    return Response(guidance)

@api_view(['GET'])
def evidence_for_criteria(request, criteria_id):
    conn = get_db_connection()
    evidence = get_evidence_requirements_for_audit_criteria(conn, criteria_id)
    return Response(evidence)

@api_view(['GET'])
def minimum_standards_for_criteria(request, criteria_id):
    conn = get_db_connection()
    standards = get_minimum_standards_for_audit_criteria(conn, criteria_id)
    return Response(standards)

@api_view(['GET'])
def prerequisites_for_criteria(request, criteria_id):
    conn = get_db_connection()
    prerequisites = get_prerequisites_for_audit_criteria(conn, criteria_id)
    return Response(prerequisites)

@api_view(['GET'])
def category_weighting_for_criteria(request, criteria_id):
    conn = get_db_connection()
    weighting = get_category_weighting_for_audit_criteria(conn, criteria_id)
    return Response({"weighting_percentage": weighting})


@csrf_exempt
def upload_data_and_files(request):
    if request.method == 'POST':
        try:
            # Attempt to load the JSON data
            data = json.loads(request.POST.get('data'))

            # Ensure the MEDIA_ROOT directory exists
            if not os.path.exists(settings.MEDIA_ROOT):
                os.makedirs(settings.MEDIA_ROOT)

            # Define the path for the 'data.json' file
            json_file_path = os.path.join(settings.MEDIA_ROOT, 'data.json')

            # Open the file in write mode, 'w' will create the file if it does not exist
            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=4)

            # Handle file uploads
            files = request.FILES.getlist('file')
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')

            # Ensure the upload directory exists
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            # Save each file
            for file in files:
                file_path = os.path.join(upload_dir, file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            # Generate a unique task ID
            task_id = str(uuid.uuid4())

            # Simulate background task by setting the task status to 'processing'
            task_statuses[task_id] = {'status': 'processing'}

            # === OpenAI Processing Start ===
            # You can trigger the OpenAI workflow here
            try:
                # Path to the directory containing files
                directory = os.path.join(settings.MEDIA_ROOT, 'uploads')

                # Step 1: Fetch audit criteria data from the API
                criteria_data = fetch_audit_criteria_data()

                if not criteria_data:
                    raise Exception("Failed to fetch criteria data.")

                # Step 2: Initialize OpenAI with criteria context
                initialize_audit_criteria(criteria_data)

                # Step 3: Process files in the directory
                file_summaries = process_files_in_directory(directory)

                # Step 4: Send file chunks to OpenAI for processing
                send_file_chunks(file_summaries)

                # Step 5: Calculate total points
                total_points = calculate_total_points(criteria_data)

                # Step 6: Finalize summaries and get the AI response
                final_response = finalize_summaries(total_points, file_summaries, criteria_data)

                # Save the final response (summary) to a JSON file
                save_response_as_json(final_response, os.path.join(settings.MEDIA_ROOT, 'final_output.json'))

                merge_audit_and_project_data()

                # Step 6: Generate the audit report (Word document)
                output_path = os.path.join(settings.MEDIA_ROOT, 'generated_audit_report.docx')
                merged_data_path = os.path.join(settings.MEDIA_ROOT, 'merged_output.json')
                with open(merged_data_path, 'r', encoding='utf-8') as merged_file:
                    merged_data = json.load(merged_file)
                create_word_document(merged_data, output_path)

                # Set task status to completed and include the output file link
                task_statuses[task_id] = {
                    'status': 'completed',
                    'file_url': f"{request.build_absolute_uri('/media/generated_audit_report.docx')}"
                }

            except Exception as e:
                task_statuses[task_id] = {'status': 'error', 'message': str(e)}

            # === OpenAI Processing End ===

            return JsonResponse({'status': 'success', 'taskId': task_id, 'message': 'Data and file(s) processed successfully'})

        except Exception as e:
            # Return error message if an exception occurs
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    # Return error if the wrong method is used
    return JsonResponse({'status': 'error', 'message': 'Only POST method is accepted'}, status=405)


@csrf_exempt
def process_criteria_data(request):
    if request.method == 'GET':
        try:
            # Path to the data.json file
            json_file_path = os.path.join(settings.MEDIA_ROOT, 'data.json')

            # Read the data.json file to get the auditCriteria ID
            with open(json_file_path, 'r') as file:
                data = json.load(file)
                audit_criteria_id = data.get('auditCriteria')

            if not audit_criteria_id:
                return JsonResponse({'status': 'error', 'message': 'Audit criteria ID not found in data.json'},
                                    status=404)

            # Establish database connection
            conn = get_db_connection()

            # Fetch comprehensive criteria data from the database
            criteria_data = get_comprehensive_criteria_data(conn, audit_criteria_id)

            if criteria_data:
                return JsonResponse({'status': 'success', 'data': criteria_data})
            else:
                return JsonResponse(
                    {'status': 'error', 'message': 'Failed to retrieve data for the given audit criteria ID'},
                    status=500)

        except FileNotFoundError:
            return JsonResponse({'status': 'error', 'message': 'data.json file not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON in data.json file'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        return JsonResponse({'status': 'error', 'message': 'Only GET method is accepted'}, status=405)

@csrf_exempt
def check_task_status(request, task_id):
    print(f"Checking status for task: {task_id}")  # Log the task_id being checked
    if request.method == 'GET':
        # Check if the task exists
        if task_id in task_statuses:
            print(f"Task {task_id} found with status: {task_statuses[task_id]}")
            # Return the status of the task
            return JsonResponse(task_statuses[task_id])
        else:
            print(f"Task {task_id} not found")
            return JsonResponse({'status': 'error', 'message': 'Task not found'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Only GET method is accepted'}, status=405)