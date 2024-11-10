import json
import os
from dotenv import load_dotenv
from datetime import date
import psycopg2
from psycopg2.extras import execute_values
import database_methods

def connect_db():
    try:
        load_dotenv()
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT')
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        exit(1)

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def populate_users_table(conn):
    users = [
        ("John", "Doe"),
        ("Jane", "Smith"),
    ]
    query = "INSERT INTO users (first_name, last_name) VALUES (%s, %s)"
    try:
        cursor = conn.cursor()
        for user in users:
            # Check if the user already exists
            check_query = "SELECT id FROM users WHERE first_name = %s AND last_name = %s"
            cursor.execute(check_query, user)
            existing_user = cursor.fetchone()

            if existing_user:
                print(f"User {user[0]} {user[1]} already exists, skipping insertion.")
                continue

            # Insert the user if not existing
            cursor.execute(query, user)

        conn.commit()
        cursor.close()
        print("Users data inserted into database successfully")
    except Exception as error:
        print(f"Error: {error}")
        conn.rollback()

def populate_projects_table(conn):
    projects = [
        ('Project Alpha', '1.1.1', True, 50, date(2024, 1, 1)),
        ('Project Beta', '1.1.3', False, 30, date(2024, 2, 15)),
        ('Project Gamma', '1.4.4', True, 70, date(2024, 3, 5)),
        ('Project Delta', '1.1.1', False, 40, date(2024, 4, 20)),
    ]

    query = "INSERT INTO projects (project_name, assessment_criteria_id, premise, total_points, date_created) VALUES (%s, %s, %s, %s, %s)"

    try:
        cursor = conn.cursor()
        for project in projects:
            # Check if the project already exists
            check_query = "SELECT id FROM projects WHERE project_name = %s AND assessment_criteria_id = %s"
            cursor.execute(check_query, (project[0], project[1]))
            existing_project = cursor.fetchone()

            if existing_project:
                print(f"Project {project[0]} with criteria {project[1]} already exists, skipping insertion.")
                continue

            # Insert the project if not existing
            cursor.execute(query, project)

        conn.commit()
        cursor.close()
        print("Projects data inserted into database successfully")
    except Exception as error:
        print(f"Error: {error}")
        conn.rollback()

def populate_projects_user_roles_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, project_name FROM projects")
        projects = cursor.fetchall()

        project_ids = {project_name: project_id for project_id, project_name in projects}

        cursor.execute("SELECT id, first_name, last_name FROM users")
        users = cursor.fetchall()

        user_ids = {f"{first_name} {last_name}": user_id for user_id, first_name, last_name in users}

        roles = [
            (project_ids['Project Alpha'], user_ids['John Doe'], 'Project Manager'),
            (project_ids['Project Alpha'], user_ids['Jane Smith'], 'Developer'),
            (project_ids['Project Beta'], user_ids['John Doe'], 'Developer'),
            (project_ids['Project Gamma'], user_ids['Jane Smith'], 'Tester')
        ]

        query = "INSERT INTO project_user_roles (project_id, user_id, role) VALUES (%s, %s, %s)"

        for role in roles:
            # Check if the role already exists
            check_query = """
                        SELECT project_id FROM project_user_roles
                        WHERE project_id = %s AND user_id = %s AND role = %s
            """
            cursor.execute(check_query, role)
            existing_role = cursor.fetchone()

            if existing_role:
                print(f"Role {role[2]} for project ID {role[0]} and user ID {role[1]} already exists, skipping insertion.")
                continue

            # Insert the role if not existing
            cursor.execute(query, role)

        conn.commit()
        cursor.close()
        print("Projects user roles data inserted into database successfully")
    except Exception as error:
        print(f"Error: {error}")
        conn.rollback()

def populate_documentation_files_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, project_name FROM projects")
        projects = cursor.fetchall()

        project_ids = {project_name: project_id for project_id, project_name in projects}

        documentation_files = [
            (project_ids['Project Alpha'], 'requirements.pdf', 'Requirements document for Project Alpha', 1),
            (project_ids['Project Alpha'], 'design.pdf', 'Design document for Project Alpha', 2),
            (project_ids['Project Beta'], 'user_manual.docx', 'User manual for Project Beta', 1),
            (project_ids['Project Gamma'], 'architecture.png', 'Architecture diagram for Project Gamma', 1)
        ]

        query = "INSERT INTO documentation_files (project_id, file_name, description, number) VALUES (%s, %s, %s, %s)"

        for documentation in documentation_files:
            # Check if the documentation file already exists
            check_query = "SELECT id FROM documentation_files WHERE project_id = %s AND file_name = %s"
            cursor.execute(check_query, (documentation[0], documentation[1]))
            existing_documentation = cursor.fetchone()

            if existing_documentation:
                print(f"Documentation file {documentation[1]} for project ID {documentation[0]} already exists, skipping insertion.")
                continue

            # Insert the documentation file if not existing
            cursor.execute(query, documentation)

        conn.commit()
        cursor.close()
        print("Documentation files data inserted into database successfully")
    except Exception as error:
        print(f"Error: {error}")
        conn.rollback()


def populate_categories_table(conn):
    with open('/app/assets/json_files/category_assessment_data/management/category.json', 'r') as file:
        data = json.load(file)

    category = data["category"]
    category_number = category["id"]
    category_name = category["name"]
    summary = category["summary"]
    total_credits_available = category["total_credits_available"]

    query = """
        INSERT INTO categories (category_number, category_name, summary, total_credits_available)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """

    values = (category_number, category_name, summary, total_credits_available)

    try:
        cursor = conn.cursor()

        # Check if the category already exists
        check_query = "SELECT id FROM categories WHERE category_number = %s"
        cursor.execute(check_query, (category_number,))
        existing_category = cursor.fetchone()

        if existing_category:
            print(f"Category with number {category_number} already exists, skipping insertion.")
            cursor.close()
            return existing_category[0]

        # Insert the category if it does not exist
        cursor.execute(query, values)
        category_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        print("Categories data inserted into database successfully")
        return category_id
    except Exception as error:
        print(f"Error: {error}")
        conn.rollback()
        return None

def populate_assessment_issues_table(conn, category_id):
    assessment_issue_paths = [
        '/app/assets/json_files/category_assessment_data/management/1_sustainability_leadership/1_assessment_issue.json',
        '/app/assets/json_files/category_assessment_data/management/2_environmental_management/1_assessment_issue.json',
        '/app/assets/json_files/category_assessment_data/management/3_responsible_construction_management/1_assessment_issue.json',
        '/app/assets/json_files/category_assessment_data/management/4_staff_supply_chain_social_governance/1_assessment_issue.json',
        '/app/assets/json_files/category_assessment_data/management/5_whole_life_costing/1_assessment_issue.json',
    ]

    assessment_issue_ids = []

    for issue_file_path in assessment_issue_paths:
        with open(issue_file_path, 'r') as issue_file:
            issue_data = json.load(issue_file)
            issue = issue_data["assessment_issue"]
            issue_number = issue["id"]
            issue_name = issue["name"]
            aim = issue["aim"]

        query = """
            INSERT INTO assessment_issues (category_id, issue_number, issue_name, aim)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        values = (category_id, issue_number, issue_name, aim)

        try:
            cursor = conn.cursor()

            # Check if the assessment issue already exists
            check_query = "SELECT id FROM assessment_issues WHERE category_id = %s AND issue_number = %s"
            cursor.execute(check_query, (category_id, issue_number))
            existing_issue = cursor.fetchone()

            if existing_issue:
                print(f"Assessment issue with number {issue_number} already exists, skipping insertion.")
                assessment_issue_ids.append((os.path.dirname(issue_file_path), existing_issue[0]))
                cursor.close()
                continue

            # Insert the assessment issue if it does not exist
            cursor.execute(query, values)
            assessment_issue_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            assessment_issue_ids.append((os.path.dirname(issue_file_path), assessment_issue_id))
            print(f"Assessment issue {issue_number} data inserted into database successfully")
        except Exception as error:
            print(f"Error: {error}")
            conn.rollback()

    return assessment_issue_ids

def populate_assessment_criteria_table(conn, assessment_issue_ids):
    assessment_criteria_ids = []
    for issue_dir, assessment_issue_id in assessment_issue_ids:
        criteria_file_path = os.path.join(issue_dir, '4_assessment_criteria.json')
        if os.path.exists(criteria_file_path):
            with open(criteria_file_path, 'r') as criteria_file:
                criteria_data = json.load(criteria_file)
                assessment_criteria = criteria_data["assessment_criteria"]

                for criteria in assessment_criteria:
                    criteria_id = criteria["criteria_id"]
                    name = criteria["name"]
                    description = criteria["description"]
                    criteria_type = criteria.get("type")

                    query = """
                        INSERT INTO assessment_criteria (assessment_issue_id, criteria_id, name, description, type)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id;
                    """
                    values = (assessment_issue_id, criteria_id, name, description, criteria_type)

                    try:
                        cursor = conn.cursor()

                        # Check if the assessment criteria already exists
                        check_query = "SELECT id FROM assessment_criteria WHERE assessment_issue_id = %s AND criteria_id = %s"
                        cursor.execute(check_query, (assessment_issue_id, criteria_id))
                        existing_criteria = cursor.fetchone()

                        if existing_criteria:
                            print(f"Assessment criteria with ID {criteria_id} already exists, skipping insertion.")
                            assessment_criteria_ids.append((issue_dir, criteria, existing_criteria[0]))
                            cursor.close()
                            continue

                        # Insert the assessment criteria if it does not exist
                        cursor.execute(query, values)
                        assessment_criteria_id = cursor.fetchone()[0]
                        conn.commit()
                        cursor.close()
                        assessment_criteria_ids.append((issue_dir, criteria, assessment_criteria_id))
                        print(f"Assessment criteria {criteria_id} data inserted into database successfully")
                    except Exception as error:
                        print(f"Error: {error}")
                        conn.rollback()

    return assessment_criteria_ids

def populate_assessment_criteria_credits_table(conn, assessment_criteria_ids):
    assessment_criteria_credit_ids = []
    for _, criteria, assessment_criteria_id in assessment_criteria_ids:
        credits = criteria.get("credits")
        if credits:
            for stage, value in credits.items():
                if value is not None:
                    query = """
                        INSERT INTO assessment_criteria_credits (assessment_criteria_id, assessment_stage, credits_value)
                        VALUES (%s, %s, %s)
                        RETURNING id;
                    """
                    values = (assessment_criteria_id, stage, value)

                    try:
                        cursor = conn.cursor()

                        # Check if the assessment criteria credit already exists
                        check_query = """
                            SELECT id FROM assessment_criteria_credits
                            WHERE assessment_criteria_id = %s AND assessment_stage = %s
                        """
                        cursor.execute(check_query, (assessment_criteria_id, stage))
                        existing_credit = cursor.fetchone()

                        if existing_credit:
                            print(f"Assessment criteria credit for stage {stage} already exists, skipping insertion.")
                            assessment_criteria_credit_ids.append((criteria, existing_credit[0]))
                            cursor.close()
                            continue

                        # Insert the assessment criteria credit if it does not exist
                        cursor.execute(query, values)
                        assessment_criteria_credit_id = cursor.fetchone()[0]
                        conn.commit()
                        cursor.close()
                        assessment_criteria_credit_ids.append((criteria, assessment_criteria_credit_id))
                        print(f"Assessment criteria credit data for stage {stage} inserted into database successfully")
                    except Exception as error:
                        print(f"Error: {error}")
                        conn.rollback()

    return assessment_criteria_credit_ids

def populate_assessment_criteria_sub_credits_table(conn, assessment_criteria_credit_ids):
    for criteria, assessment_criteria_credit_id in assessment_criteria_credit_ids:
        sub_credits = criteria.get("sub_credits")
        if sub_credits:
            for sub_credit in sub_credits:
                description = sub_credit.get("description")
                role = sub_credit.get("role")
                credits = sub_credit["credits"]
                assessment_stages = sub_credit.get("assessment_stage")

                if isinstance(assessment_stages, list):
                    for stage in assessment_stages:
                        query = """
                            INSERT INTO assessment_criteria_sub_credits (assessment_criteria_credit_id, description, role, credits, assessment_stage)
                            VALUES (%s, %s, %s, %s, %s);
                        """
                        values = (assessment_criteria_credit_id, description, role, credits, stage)

                        try:
                            cursor = conn.cursor()

                            # Check if the sub-credit already exists
                            check_query = """
                                SELECT id FROM assessment_criteria_sub_credits
                                WHERE assessment_criteria_credit_id = %s AND assessment_stage = %s AND role = %s
                            """
                            cursor.execute(check_query, (assessment_criteria_credit_id, stage, role))
                            existing_sub_credit = cursor.fetchone()

                            if existing_sub_credit:
                                print(f"Sub-credit for criteria credit {assessment_criteria_credit_id} in stage {stage} with role {role} already exists, skipping insertion.")
                                cursor.close()
                                continue

                            # Insert the sub-credit if it does not exist
                            cursor.execute(query, values)
                            conn.commit()
                            cursor.close()
                            print(f"Sub-credit for criteria credit {assessment_criteria_credit_id} in stage {stage} inserted successfully")
                        except Exception as error:
                            print(f"Error: {error}")
                            conn.rollback()
                else:
                    query = """
                        INSERT INTO assessment_criteria_sub_credits (assessment_criteria_credit_id, description, role, credits, assessment_stage)
                        VALUES (%s, %s, %s, %s, %s);
                    """
                    values = (assessment_criteria_credit_id, description, role, credits, assessment_stages)

                    try:
                        cursor = conn.cursor()

                        # Check if the sub-credit already exists
                        check_query = """
                            SELECT id FROM assessment_criteria_sub_credits
                            WHERE assessment_criteria_credit_id = %s AND assessment_stage = %s AND role = %s
                        """
                        cursor.execute(check_query, (assessment_criteria_credit_id, assessment_stages, role))
                        existing_sub_credit = cursor.fetchone()

                        if existing_sub_credit:
                            print(f"Sub-credit for criteria credit {assessment_criteria_credit_id} in stage {assessment_stages} with role {role} already exists, skipping insertion.")
                            cursor.close()
                            continue

                        # Insert the sub-credit if it does not exist
                        cursor.execute(query, values)
                        conn.commit()
                        cursor.close()
                        print(f"Sub-credit for criteria credit {assessment_criteria_credit_id} inserted successfully")
                    except Exception as error:
                        print(f"Error: {error}")
                        conn.rollback()

def populate_guidance_table(conn, assessment_criteria_ids):
    for issue_dir, _, _ in assessment_criteria_ids:
        guidance_file_path = os.path.join(issue_dir, '5_guidance.json')
        if os.path.exists(guidance_file_path):
            with open(guidance_file_path, 'r') as guidance_file:
                try:
                    guidance_data = json.load(guidance_file)
                    if "guidance" not in guidance_data:
                        print(f"No 'guidance' key found in {guidance_file_path}, skipping.")
                        continue

                    guidance_list = guidance_data["guidance"]

                    for guidance in guidance_list:
                        criteria_id = guidance["assessment_criteria_id"]
                        guidance_text = guidance["guidance_text"]

                        cursor = conn.cursor()
                        fetch_query = """
                            SELECT id FROM assessment_criteria
                            WHERE criteria_id = %s;
                        """
                        cursor.execute(fetch_query, (criteria_id,))
                        result = cursor.fetchone()
                        if result:
                            assessment_criteria_id = result[0]
                        else:
                            print(f"No matching assessment_criteria found for criteria_id {criteria_id}")
                            continue

                        # Check if the guidance text already exists for this criteria
                        check_query = """
                            SELECT id FROM guidance
                            WHERE assessment_criteria_id = %s AND guidance_text = %s;
                        """
                        cursor.execute(check_query, (assessment_criteria_id, guidance_text))
                        existing_guidance = cursor.fetchone()

                        if existing_guidance:
                            print(f"Guidance for criteria {criteria_id} already exists, skipping insertion.")
                            continue

                        query = """
                            INSERT INTO guidance (assessment_criteria_id, guidance_text)
                            VALUES (%s, %s);
                        """
                        values = (assessment_criteria_id, guidance_text)

                        try:
                            cursor.execute(query, values)
                            conn.commit()
                            print(f"Guidance for criteria {criteria_id} inserted successfully")
                        except Exception as error:
                            print(f"Error: {error}")
                            conn.rollback()
                        finally:
                            cursor.close()
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON file {guidance_file_path}: {e}")

def populate_evidence_issue_table(conn, assessment_criteria_ids):
    for issue_dir, _, _ in assessment_criteria_ids:
        evidence_file_path = os.path.join(issue_dir, '6_evidence.json')
        if os.path.exists(evidence_file_path):
            with open(evidence_file_path, 'r') as evidence_file:
                evidence_data = json.load(evidence_file)
                evidence_list = evidence_data["evidence"]

                for evidence in evidence_list:
                    criteria_id = evidence["assessment_criteria_id"]
                    evidence_type = evidence["type"]
                    evidence_guidance = evidence["evidence_guidance"]

                    cursor = conn.cursor()
                    fetch_query = """
                        SELECT id FROM assessment_criteria
                        WHERE criteria_id = %s;
                    """
                    cursor.execute(fetch_query, (criteria_id,))
                    result = cursor.fetchone()
                    if result:
                        assessment_criteria_id = result[0]
                    else:
                        print(f"No matching assessment_criteria found for criteria_id {criteria_id}")
                        cursor.close()
                        continue

                    # Check if the evidence already exists
                    check_query = """
                        SELECT id FROM evidence
                        WHERE assessment_criteria_id = %s AND type = %s
                    """
                    cursor.execute(check_query, (assessment_criteria_id, evidence_type))
                    existing_evidence = cursor.fetchone()

                    if existing_evidence:
                        print(f"Evidence for criteria {criteria_id} and type {evidence_type} already exists, skipping insertion.")
                        cursor.close()
                        continue

                    query = """
                        INSERT INTO evidence (assessment_criteria_id, type, evidence_guidance)
                        VALUES (%s, %s, %s);
                    """
                    values = (assessment_criteria_id, evidence_type, evidence_guidance)

                    try:
                        cursor.execute(query, values)
                        conn.commit()
                        cursor.close()
                        print(f"Evidence for criteria {criteria_id} inserted successfully")
                    except Exception as error:
                        print(f"Error: {error}")
                        conn.rollback()

def populate_project_types_table(conn):
    with open('/app/assets/json_files/scope/1_project_types.json', 'r') as file:
        data = json.load(file)
        for project_type in data['project_types']:
            type_name = project_type['type_name']
            description = project_type['description']

            cursor = conn.cursor()

            # Check if the project type already exists
            check_query = """
                SELECT id FROM project_types
                WHERE type_name = %s
            """
            cursor.execute(check_query, (type_name,))
            existing_project_type = cursor.fetchone()

            if existing_project_type:
                print(f"Project type {type_name} already exists, skipping insertion.")
                cursor.close()
                continue

            query = """
                INSERT INTO project_types (type_name, description)
                VALUES (%s, %s);
            """
            values = (type_name, description)

            try:
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                print(f"Project type {type_name} inserted successfully")
            except Exception as error:
                print(f"Error: {error}")
                conn.rollback()

def populate_assessment_stages_table(conn):
    with open('/app/assets/json_files/scope/2_assessment_stages.json', 'r') as file:
        data = json.load(file)
        for stage in data['assessment_stages']:
            stage_name = stage['stage_name']
            description = stage['description']

            cursor = conn.cursor()

            # Check if the assessment stage already exists
            check_query = """
                SELECT id FROM assessment_stages
                WHERE stage_name = %s
            """
            cursor.execute(check_query, (stage_name,))
            existing_stage = cursor.fetchone()

            if existing_stage:
                print(f"Assessment stage {stage_name} already exists, skipping insertion.")
                cursor.close()
                continue

            query = """
                INSERT INTO assessment_stages (stage_name, description)
                VALUES (%s, %s);
            """
            values = (stage_name, description)

            try:
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                print(f"Assessment stage {stage_name} inserted successfully")
            except Exception as error:
                print(f"Error: {error}")
                conn.rollback()

def populate_assessment_types_table(conn):
    assessment_type_stages_list = []
    with open('/app/assets/json_files/scope/3_assessment_types.json', 'r') as file:
        data = json.load(file)
        for assessment_type in data['assessment_types']:
            type_name = assessment_type['type_name']
            description = assessment_type['description']

            cursor = conn.cursor()

            # Check if the assessment type already exists
            check_query = """
                SELECT id FROM assessment_types
                WHERE type_name = %s
            """
            cursor.execute(check_query, (type_name,))
            existing_assessment_type = cursor.fetchone()

            if existing_assessment_type:
                print(f"Assessment type {type_name} already exists, skipping insertion.")
                assessment_type_stages_list.append((existing_assessment_type[0], assessment_type['applicable_stages'], type_name))
                cursor.close()
                continue

            query = """
                INSERT INTO assessment_types (type_name, description)
                VALUES (%s, %s) RETURNING id;
            """
            values = (type_name, description)

            try:
                cursor.execute(query, values)
                assessment_type_id = cursor.fetchone()[0]
                conn.commit()
                print(f"Assessment type {type_name} inserted successfully")
                assessment_type_stages_list.append((assessment_type_id, assessment_type['applicable_stages'], type_name))
            except Exception as error:
                print(f"Error: {error}")
                conn.rollback()
            finally:
                cursor.close()

    return assessment_type_stages_list

def populate_assessment_type_stages_table(conn, assessment_type_stages_list):
    for assessment_type_id, applicable_stages, type_name in assessment_type_stages_list:
        for stage_name in applicable_stages:
            cursor = conn.cursor()
            fetch_query = """
                SELECT id FROM assessment_stages
                WHERE stage_name = %s;
            """
            cursor.execute(fetch_query, (stage_name,))
            stage_result = cursor.fetchone()
            if stage_result:
                stage_id = stage_result[0]

                # Check if the stage is already linked to the assessment type
                check_query = """
                    SELECT 1 FROM assessment_type_stages
                    WHERE assessment_type_id = %s AND assessment_stage_id = %s;
                """
                cursor.execute(check_query, (assessment_type_id, stage_id))
                existing_link = cursor.fetchone()

                if existing_link:
                    print(f"Stage {stage_name} is already linked to assessment type {type_name}, skipping insertion.")
                    cursor.close()
                    continue

                insert_query = """
                    INSERT INTO assessment_type_stages (assessment_type_id, assessment_stage_id)
                    VALUES (%s, %s);
                """
                try:
                    cursor.execute(insert_query, (assessment_type_id, stage_id))
                    conn.commit()
                    cursor.close()
                    print(f"Stage {stage_name} linked to assessment type {type_name} successfully")
                except Exception as error:
                    print(f"Error inserting stage {stage_name} for assessment type {type_name}: {error}")
                    conn.rollback()
            else:
                print(f"Stage {stage_name} not found for assessment type {type_name}")
def populate_verification_points_table(conn):
    with open('/app/assets/json_files/scope/4_verification_points.json', 'r') as file:
        data = json.load(file)
        for verification in data['verification_points']:
            assessment_type_name = verification['assessment_type']
            verification_stages = verification['verification_stages']

            cursor = conn.cursor()
            fetch_query = """
                SELECT id FROM assessment_types
                WHERE type_name = %s;
            """
            cursor.execute(fetch_query, (assessment_type_name,))
            assessment_type_result = cursor.fetchone()
            if assessment_type_result:
                assessment_type_id = assessment_type_result[0]
                for stage in verification_stages:
                    stage_name = stage['stage']
                    verification_type = stage['verification_type']

                    # Check if the verification point already exists
                    check_query = """
                        SELECT 1 FROM verification_points
                        WHERE assessment_type_id = %s AND stage = %s AND verification_type = %s;
                    """
                    cursor.execute(check_query, (assessment_type_id, stage_name, verification_type))
                    existing_verification_point = cursor.fetchone()

                    if existing_verification_point:
                        print(f"Verification point for stage {stage_name} and assessment type {assessment_type_name} already exists, skipping insertion.")
                        continue

                    insert_query = """
                        INSERT INTO verification_points (assessment_type_id, stage, verification_type)
                        VALUES (%s, %s, %s);
                    """
                    values = (assessment_type_id, stage_name, verification_type)

                    try:
                        cursor.execute(insert_query, values)
                        conn.commit()
                        print(f"Verification point for stage {stage_name} and assessment type {assessment_type_name} inserted successfully")
                    except Exception as error:
                        print(f"Error inserting verification point for stage {stage_name} and assessment type {assessment_type_name}: {error}")
                        conn.rollback()
            else:
                print(f"Assessment type {assessment_type_name} not found")
            cursor.close()
def populate_system_boundaries_table(conn):
    with open('/app/assets/json_files/scope/5_system_boundaries.json', 'r') as file:
        data = json.load(file)
        for boundary in data['system_boundaries']:
            boundary_name = boundary['boundary_name']
            description = boundary['description']

            cursor = conn.cursor()

            # Check if the system boundary already exists
            check_query = """
                SELECT 1 FROM system_boundaries
                WHERE boundary_name = %s;
            """
            cursor.execute(check_query, (boundary_name,))
            existing_boundary = cursor.fetchone()

            if existing_boundary:
                print(f"System boundary {boundary_name} already exists, skipping insertion.")
                cursor.close()
                continue

            query = """
                INSERT INTO system_boundaries (boundary_name, description)
                VALUES (%s, %s);
            """
            values = (boundary_name, description)

            try:
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                print(f"System boundary {boundary_name} inserted successfully")
            except Exception as error:
                print(f"Error inserting system boundary {boundary_name}: {error}")
                conn.rollback()
def populate_rating_levels_table(conn):
    with open('/app/assets/json_files/scoring_rating/1_rating_levels.json', 'r') as file:
        data = json.load(file)
        for rating_level in data['rating_levels']:
            rating = rating_level['rating']
            overall_score_min = rating_level['overall_score_min']
            overall_score_max = rating_level['overall_score_max']

            cursor = conn.cursor()

            # Check if the rating level already exists
            check_query = """
                SELECT 1 FROM rating_levels
                WHERE rating = %s;
            """
            cursor.execute(check_query, (rating,))
            existing_rating = cursor.fetchone()

            if existing_rating:
                print(f"Rating level {rating} already exists, skipping insertion.")
                cursor.close()
                continue

            query = """
                INSERT INTO rating_levels (rating, overall_score_min, overall_score_max)
                VALUES (%s, %s, %s);
            """
            values = (rating, overall_score_min, overall_score_max)

            try:
                cursor.execute(query, values)
                conn.commit()
                cursor.close()
                print(f"Rating level {rating} inserted successfully")
            except Exception as error:
                print(f"Error inserting rating level {rating}: {error}")
                conn.rollback()
def populate_minimum_standards_table(conn):
    with open('/app/assets/json_files/scoring_rating/2_minimum_standards.json', 'r') as file:
        data = json.load(file)
        for standard in data['minimum_standards']:
            rating_level_name = standard['rating_level']

            cursor = conn.cursor()
            fetch_query = """
                SELECT id FROM rating_levels
                WHERE rating = %s;
            """
            cursor.execute(fetch_query, (rating_level_name,))
            rating_level_result = cursor.fetchone()
            if rating_level_result:
                rating_level_id = rating_level_result[0]
                for issue in standard['assessment_issues']:
                    issue_number = issue['issue_number']
                    issue_name = issue['issue_name']

                    fetch_issue_query = """
                        SELECT id FROM assessment_issues
                        WHERE issue_number = %s AND issue_name = %s;
                    """
                    cursor.execute(fetch_issue_query, (issue_number, issue_name))
                    issue_result = cursor.fetchone()
                    if issue_result:
                        assessment_issue_id = issue_result[0]
                        for criteria in issue['assessment_criteria']:
                            criteria_number = criteria['criteria_number']
                            criteria_name = criteria['criteria_name']
                            minimum_standard = criteria['minimum_standard']

                            fetch_criteria_query = """
                                SELECT id FROM assessment_criteria
                                WHERE criteria_id = %s AND name = %s;
                            """
                            cursor.execute(fetch_criteria_query, (criteria_number, criteria_name))
                            criteria_result = cursor.fetchone()
                            if criteria_result:
                                assessment_criteria_id = criteria_result[0]

                                # Check if the minimum standard already exists
                                check_query = """
                                    SELECT 1 FROM minimum_standards
                                    WHERE rating_level_id = %s AND assessment_issue_id = %s AND assessment_criteria_id = %s;
                                """
                                cursor.execute(check_query, (rating_level_id, assessment_issue_id, assessment_criteria_id))
                                existing_standard = cursor.fetchone()

                                if existing_standard:
                                    print(f"Minimum standard for criteria {criteria_number} under issue {issue_number} already exists, skipping insertion.")
                                    continue

                                insert_query = """
                                    INSERT INTO minimum_standards (rating_level_id, assessment_issue_id, assessment_criteria_id, minimum_standard)
                                    VALUES (%s, %s, %s, %s);
                                """
                                values = (rating_level_id, assessment_issue_id, assessment_criteria_id, minimum_standard)

                                try:
                                    cursor.execute(insert_query, values)
                                    conn.commit()
                                    print(f"Minimum standard for criteria {criteria_number} under issue {issue_number} inserted successfully")
                                except Exception as error:
                                    print(f"Error inserting minimum standard for criteria {criteria_number}: {error}")
                                    conn.rollback()
                            else:
                                print(f"Assessment criteria {criteria_number} not found for issue {issue_number}")
                    else:
                        print(f"Assessment issue {issue_number} not found")
            else:
                print(f"Rating level {rating_level_name} not found")
            cursor.close()

def populate_category_weightings_table(conn):
    with open('/app/assets/json_files/scoring_rating/3_category_weightings.json', 'r') as file:
        data = json.load(file)
        for weighting in data['category_weightings']:
            category_name = weighting['category']
            weighting_percentage = weighting['weighting_percentage']

            cursor = conn.cursor()
            fetch_query = """
                SELECT id FROM categories
                WHERE category_name = %s;
            """
            cursor.execute(fetch_query, (category_name,))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]

                # Check if the category weighting already exists
                check_query = """
                    SELECT 1 FROM category_weightings
                    WHERE category_id = %s;
                """
                cursor.execute(check_query, (category_id,))
                existing_weighting = cursor.fetchone()

                if existing_weighting:
                    print(f"Category weighting for {category_name} already exists, skipping insertion.")
                    cursor.close()
                    continue

                insert_query = """
                    INSERT INTO category_weightings (category_id, weighting_percentage)
                    VALUES (%s, %s);
                """
                values = (category_id, weighting_percentage)

                try:
                    cursor.execute(insert_query, values)
                    conn.commit()
                    cursor.close()
                    print(f"Category weighting for {category_name} inserted successfully")
                except Exception as error:
                    print(f"Error inserting category weighting for {category_name}: {error}")
                    conn.rollback()
            else:
                print(f"Category {category_name} not found")

def populate_prerequisites_table(conn):
    with open('/app/assets/json_files/scoring_rating/4_prerequisites.json', 'r') as file:
        data = json.load(file)
        for prerequisite in data['prerequisites']:
            category_name = prerequisite['category']
            issue_number = prerequisite['issue_number']
            issue_name = prerequisite['issue_name']
            prerequisites = prerequisite['prerequisites']

            cursor = conn.cursor()
            fetch_category_query = """
                SELECT id FROM categories
                WHERE category_name = %s;
            """
            cursor.execute(fetch_category_query, (category_name,))
            category_result = cursor.fetchone()
            if category_result:
                category_id = category_result[0]
                fetch_issue_query = """
                    SELECT id FROM assessment_issues
                    WHERE issue_number = %s AND issue_name = %s;
                """
                cursor.execute(fetch_issue_query, (issue_number, issue_name))
                issue_result = cursor.fetchone()
                if issue_result:
                    assessment_issue_id = issue_result[0]
                    for prereq in prerequisites:
                        criteria_number = prereq['criteria_number']
                        criteria_name = prereq['criteria_name']

                        fetch_criteria_query = """
                            SELECT id FROM assessment_criteria
                            WHERE criteria_id = %s AND name = %s;
                        """
                        cursor.execute(fetch_criteria_query, (criteria_number, criteria_name))
                        criteria_result = cursor.fetchone()
                        if criteria_result:
                            assessment_criteria_id = criteria_result[0]

                            # Check if the prerequisite already exists
                            check_query = """
                                SELECT 1 FROM prerequisites
                                WHERE category_id = %s AND assessment_issue_id = %s AND assessment_criteria_id = %s;
                            """
                            cursor.execute(check_query, (category_id, assessment_issue_id, assessment_criteria_id))
                            existing_prerequisite = cursor.fetchone()

                            if existing_prerequisite:
                                print(f"Prerequisite for criteria {criteria_number} under issue {issue_number} already exists, skipping insertion.")
                                continue

                            insert_query = """
                                INSERT INTO prerequisites (category_id, assessment_issue_id, assessment_criteria_id)
                                VALUES (%s, %s, %s);
                            """
                            values = (category_id, assessment_issue_id, assessment_criteria_id)

                            try:
                                cursor.execute(insert_query, values)
                                conn.commit()
                                print(f"Prerequisite for criteria {criteria_number} under issue {issue_number} inserted successfully")
                            except Exception as error:
                                print(f"Error inserting prerequisite for criteria {criteria_number}: {error}")
                                conn.rollback()
                        else:
                            print(f"Assessment criteria {criteria_number} not found for issue {issue_number}")
                else:
                    print(f"Assessment issue {issue_number} not found")
            else:
                print(f"Category {category_name} not found")
            cursor.close()

def populate_innovation_credits_table(conn):
    with open('/app/assets/json_files/scoring_rating/5_innovation_credits.json', 'r') as file:
        data = json.load(file)
        description = data['innovation_credits']['description']

        cursor = conn.cursor()

        # Check if the innovation credit already exists
        check_query = """
            SELECT 1 FROM innovation_credits
            WHERE description = %s;
        """
        cursor.execute(check_query, (description,))
        existing_credit = cursor.fetchone()

        if existing_credit:
            print("Innovation credit already exists, skipping insertion.")
            cursor.close()
            return

        query = """
            INSERT INTO innovation_credits (description)
            VALUES (%s);
        """
        values = (description,)

        try:
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            print("Innovation credit inserted successfully")
        except Exception as error:
            print(f"Error inserting innovation credit: {error}")
            conn.rollback()

def populate_project_audit_criteria_table(conn):
    cursor = conn.cursor()
    fetch_query = """
        SELECT id, assessment_criteria_id FROM projects;
    """
    try:
        cursor.execute(fetch_query)
        projects = cursor.fetchall()
        project_audit_criteria = []

        for project in projects:
            project_id = project[0]
            criteria_id = project[1]

            fetch_criteria_query = """
                SELECT id FROM assessment_criteria
                WHERE criteria_id = %s;
            """
            cursor.execute(fetch_criteria_query, (criteria_id,))
            criteria_result = cursor.fetchone()
            if criteria_result:
                assessment_criteria_id = criteria_result[0]

                # Check if the project audit criteria already exists
                check_query = """
                    SELECT 1 FROM project_audit_criteria
                    WHERE project_id = %s AND assessment_criteria_id = %s;
                """
                cursor.execute(check_query, (project_id, assessment_criteria_id))
                existing_entry = cursor.fetchone()

                if existing_entry:
                    print(f"Project audit criteria for project ID {project_id} and criteria ID {assessment_criteria_id} already exists, skipping insertion.")
                    continue

                project_audit_criteria.append((project_id, assessment_criteria_id))

        if project_audit_criteria:
            query = "INSERT INTO project_audit_criteria (project_id, assessment_criteria_id) VALUES %s"
            execute_values(cursor, query, project_audit_criteria)
            conn.commit()
            print("Project audit criteria data inserted into database successfully")
        cursor.close()
    except Exception as error:
        print(f"Error: {error}")
        conn.rollback()

def delete_all_tables(conn):
    tables = [
        "users", "projects", "project_user_roles", "documentation_files", "categories",
        "assessment_issues", "assessment_criteria", "assessment_criteria_credits",
        "assessment_criteria_sub_credits", "guidance", "evidence", "project_types",
        "assessment_stages", "assessment_types", "assessment_type_stages", "verification_points",
        "system_boundaries", "rating_levels", "minimum_standards", "category_weightings",
        "prerequisites", "innovation_credits", "project_audit_criteria"
    ]

    try:
        cursor = conn.cursor()
        for table in tables:
            drop_query = f"DROP TABLE IF EXISTS {table} CASCADE;"
            cursor.execute(drop_query)
            print(f"Table {table} deleted successfully.")
        conn.commit()
        cursor.close()
    except Exception as error:
        print(f"Error deleting tables: {error}")
        conn.rollback()

def create_all_tables(conn):
    create_queries = [
        """
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(255),
            last_name VARCHAR(255)
        );
        """,
        """
        CREATE TABLE projects (
            id SERIAL PRIMARY KEY,
            project_name VARCHAR(255) NOT NULL,
            assessment_criteria_id VARCHAR(10),
            premise BOOLEAN,
            total_points INTEGER,
            date_created DATE NOT NULL
        );
        CREATE INDEX idx_projects_assessment_criteria_id ON projects (assessment_criteria_id);
        """,
        """
        CREATE TABLE project_user_roles (
            project_id INTEGER REFERENCES projects(id),
            user_id INTEGER REFERENCES users(id),
            role VARCHAR(255),
            PRIMARY KEY (project_id, user_id, role)
        );
        CREATE INDEX idx_project_user_roles_project_id ON project_user_roles (project_id);
        CREATE INDEX idx_project_user_roles_user_id ON project_user_roles (user_id);
        """,
        """
        CREATE TABLE documentation_files (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id),
            file_name VARCHAR(255),
            description TEXT,
            number INTEGER
        );
        CREATE INDEX idx_documentation_files_project_id ON documentation_files (project_id);
        """,
        """
        CREATE TABLE categories (
            id SERIAL PRIMARY KEY,
            category_number VARCHAR(10),
            category_name VARCHAR(255),
            summary TEXT,
            total_credits_available INTEGER
        );
        """,
        """
        CREATE TABLE assessment_issues (
            id SERIAL PRIMARY KEY,
            category_id INTEGER REFERENCES categories(id),
            issue_number VARCHAR(10),
            issue_name VARCHAR(255),
            aim TEXT
        );
        CREATE INDEX idx_assessment_issues_category_id ON assessment_issues (category_id);
        """,
        """
        CREATE TABLE assessment_criteria (
            id SERIAL PRIMARY KEY,
            assessment_issue_id INTEGER REFERENCES assessment_issues(id),
            criteria_id VARCHAR(10),
            name VARCHAR(255),
            description TEXT,
            type VARCHAR(50)
        );
        CREATE INDEX idx_assessment_criteria_assessment_issue_id ON assessment_criteria (assessment_issue_id);
        """,
        """
        CREATE TABLE assessment_criteria_credits (
            id SERIAL PRIMARY KEY,
            assessment_criteria_id INTEGER REFERENCES assessment_criteria(id),
            assessment_stage VARCHAR(50),
            credits_value VARCHAR(50)
        );
        CREATE INDEX idx_assessment_criteria_credits_assessment_criteria_id ON assessment_criteria_credits (assessment_criteria_id);
        """,
        """
        CREATE TABLE assessment_criteria_sub_credits (
            id SERIAL PRIMARY KEY,
            assessment_criteria_credit_id INTEGER REFERENCES assessment_criteria_credits(id),
            description TEXT,
            role VARCHAR(100),
            credits INTEGER,
            assessment_stage VARCHAR(50)
        );
        CREATE INDEX idx_assessment_criteria_sub_credits_assessment_criteria_credit_id ON assessment_criteria_sub_credits (assessment_criteria_credit_id);
        """,
        """
        CREATE TABLE guidance (
            id SERIAL PRIMARY KEY,
            assessment_criteria_id INTEGER REFERENCES assessment_criteria(id),
            guidance_text TEXT
        );
        CREATE INDEX idx_guidance_assessment_criteria_id ON guidance (assessment_criteria_id);
        """,
        """
        CREATE TABLE evidence (
            id SERIAL PRIMARY KEY,
            assessment_criteria_id INTEGER REFERENCES assessment_criteria(id),
            type VARCHAR(50),
            evidence_guidance TEXT
        );
        CREATE INDEX idx_evidence_assessment_criteria_id ON evidence (assessment_criteria_id);
        """,
        """
        CREATE TABLE project_types (
            id SERIAL PRIMARY KEY,
            type_name VARCHAR(255),
            description TEXT
        );
        """,
        """
        CREATE TABLE assessment_stages (
            id SERIAL PRIMARY KEY,
            stage_name VARCHAR(255),
            description TEXT
        );
        """,
        """
        CREATE TABLE assessment_types (
            id SERIAL PRIMARY KEY,
            type_name VARCHAR(255),
            description TEXT
        );
        """,
        """
        CREATE TABLE assessment_type_stages (
            assessment_type_id INTEGER REFERENCES assessment_types(id),
            assessment_stage_id INTEGER REFERENCES assessment_stages(id),
            PRIMARY KEY (assessment_type_id, assessment_stage_id)
        );
        CREATE INDEX idx_assessment_type_stages_assessment_type_id ON assessment_type_stages (assessment_type_id);
        CREATE INDEX idx_assessment_type_stages_assessment_stage_id ON assessment_type_stages (assessment_stage_id);
        """,
        """
        CREATE TABLE verification_points (
            id SERIAL PRIMARY KEY,
            assessment_type_id INTEGER REFERENCES assessment_types(id),
            stage VARCHAR(255),
            verification_type VARCHAR(50)
        );
        CREATE INDEX idx_verification_points_assessment_type_id ON verification_points (assessment_type_id);
        """,
        """
        CREATE TABLE system_boundaries (
            id SERIAL PRIMARY KEY,
            boundary_name VARCHAR(255),
            description TEXT
        );
        """,
        """
        CREATE TABLE rating_levels (
            id SERIAL PRIMARY KEY,
            rating VARCHAR(50),
            overall_score_min INTEGER,
            overall_score_max INTEGER
        );
        """,
        """
        CREATE TABLE minimum_standards (
            id SERIAL PRIMARY KEY,
            rating_level_id INTEGER REFERENCES rating_levels(id),
            assessment_issue_id INTEGER REFERENCES assessment_issues(id),
            assessment_criteria_id INTEGER REFERENCES assessment_criteria(id),
            minimum_standard TEXT
        );
        CREATE INDEX idx_minimum_standards_rating_level_id ON minimum_standards (rating_level_id);
        CREATE INDEX idx_minimum_standards_assessment_issue_id ON minimum_standards (assessment_issue_id);
        CREATE INDEX idx_minimum_standards_assessment_criteria_id ON minimum_standards (assessment_criteria_id);
        """,
        """
        CREATE TABLE category_weightings (
            id SERIAL PRIMARY KEY,
            category_id INTEGER REFERENCES categories(id),
            weighting_percentage INTEGER
        );
        CREATE INDEX idx_category_weightings_category_id ON category_weightings (category_id);
        """,
        """
        CREATE TABLE prerequisites (
            id SERIAL PRIMARY KEY,
            category_id INTEGER REFERENCES categories(id),
            assessment_issue_id INTEGER REFERENCES assessment_issues(id),
            assessment_criteria_id INTEGER REFERENCES assessment_criteria(id)
        );
        CREATE INDEX idx_prerequisites_category_id ON prerequisites (category_id);
        CREATE INDEX idx_prerequisites_assessment_issue_id ON prerequisites (assessment_issue_id);
        CREATE INDEX idx_prerequisites_assessment_criteria_id ON prerequisites (assessment_criteria_id);
        """,
        """
        CREATE TABLE innovation_credits (
            id SERIAL PRIMARY KEY,
            description TEXT
        );
        """,
        """
        CREATE TABLE project_audit_criteria (
            project_id INTEGER REFERENCES projects(id),
            assessment_criteria_id INTEGER REFERENCES assessment_criteria(id),
            PRIMARY KEY (project_id, assessment_criteria_id)
        );
        CREATE INDEX idx_project_audit_criteria_project_id ON project_audit_criteria (project_id);
        CREATE INDEX idx_project_audit_criteria_assessment_criteria_id ON project_audit_criteria (assessment_criteria_id);
        """
    ]

    try:
        cursor = conn.cursor()
        for query in create_queries:
            cursor.execute(query)
            print("Table created successfully.")
        conn.commit()
        cursor.close()
    except Exception as error:
        print(f"Error creating tables: {error}")
        conn.rollback()

def populate_database(conn):
    populate_users_table(conn)
    populate_projects_table(conn)
    populate_projects_user_roles_table(conn)
    populate_documentation_files_table(conn)
    category_id = populate_categories_table(conn)
    assessment_issue_ids = populate_assessment_issues_table(conn, category_id)
    assessment_criteria_ids = populate_assessment_criteria_table(conn, assessment_issue_ids)
    assessment_criteria_credit_ids = populate_assessment_criteria_credits_table(conn, assessment_criteria_ids)
    populate_assessment_criteria_sub_credits_table(conn, assessment_criteria_credit_ids)
    populate_guidance_table(conn, assessment_criteria_ids)
    populate_evidence_issue_table(conn, assessment_criteria_ids)
    populate_project_types_table(conn)
    populate_assessment_stages_table(conn)
    assessment_type_stages_list = populate_assessment_types_table(conn)
    populate_assessment_type_stages_table(conn, assessment_type_stages_list)
    populate_verification_points_table(conn)
    populate_system_boundaries_table(conn)
    populate_rating_levels_table(conn)
    populate_innovation_credits_table(conn)
    populate_project_audit_criteria_table(conn)

def main():
    conn = connect_db()
    delete_all_tables(conn)
    create_all_tables(conn)
    populate_database(conn)
    conn.close()

if __name__ == "__main__":
    main()
