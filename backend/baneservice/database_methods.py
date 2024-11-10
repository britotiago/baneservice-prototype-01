import psycopg2
from psycopg2.extras import DictCursor

def get_audit_criteria_by_id(conn, criteria_id):
    """
    Retrieves details of an assessment criteria based on its criteria_id.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT ac.id, ac.criteria_id, ac.name, ac.description, ac.type,
                   ai.issue_number, ai.issue_name,
                   c.category_number, c.category_name
            FROM assessment_criteria ac
            JOIN assessment_issues ai ON ac.assessment_issue_id = ai.id
            JOIN categories c ON ai.category_id = c.id
            WHERE ac.criteria_id = %s;
        """
        cursor.execute(query, (criteria_id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    except Exception as error:
        print(f"Error retrieving audit criteria {criteria_id}: {error}")
        return None

def get_projects_by_audit_criteria(conn, criteria_id):
    """
    Retrieves all projects associated with a specific assessment criteria.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT p.id, p.project_name, p.premise, p.total_points, p.date_created
            FROM projects p
            JOIN project_audit_criteria pac ON p.id = pac.project_id
            JOIN assessment_criteria ac ON pac.assessment_criteria_id = ac.id
            WHERE ac.criteria_id = %s;
        """
        cursor.execute(query, (criteria_id,))
        projects = cursor.fetchall()
        cursor.close()
        return projects
    except Exception as error:
        print(f"Error retrieving projects for audit criteria {criteria_id}: {error}")
        return []

def get_documentation_files_by_project(conn, project_id):
    """
    Retrieves all documentation files for a specific project.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT df.id, df.file_name, df.description, df.number
            FROM documentation_files df
            WHERE df.project_id = %s;
        """
        cursor.execute(query, (project_id,))
        files = cursor.fetchall()
        cursor.close()
        return files
    except Exception as error:
        print(f"Error retrieving documentation files for project {project_id}: {error}")
        return []
def get_guidance_for_audit_criteria(conn, criteria_id):
    """
    Retrieves guidance text for a specific assessment criteria.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT g.guidance_text
            FROM guidance g
            JOIN assessment_criteria ac ON g.assessment_criteria_id = ac.id
            WHERE ac.criteria_id = %s;
        """
        cursor.execute(query, (criteria_id,))
        guidance = cursor.fetchall()
        cursor.close()
        return [g['guidance_text'] for g in guidance]
    except Exception as error:
        print(f"Error retrieving guidance for audit criteria {criteria_id}: {error}")
        return []

def get_evidence_requirements_for_audit_criteria(conn, criteria_id):
    """
    Retrieves evidence requirements for a specific assessment criteria.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT e.type, e.evidence_guidance
            FROM evidence e
            JOIN assessment_criteria ac ON e.assessment_criteria_id = ac.id
            WHERE ac.criteria_id = %s;
        """
        cursor.execute(query, (criteria_id,))
        evidence = cursor.fetchall()
        cursor.close()
        return evidence
    except Exception as error:
        print(f"Error retrieving evidence requirements for audit criteria {criteria_id}: {error}")
        return []

def get_assessment_criteria_credits(conn, criteria_id):
    """
    Retrieves credit information for a specific assessment criteria.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT acc.assessment_stage, acc.credits_value
            FROM assessment_criteria_credits acc
            JOIN assessment_criteria ac ON acc.assessment_criteria_id = ac.id
            WHERE ac.criteria_id = %s;
        """
        cursor.execute(query, (criteria_id,))
        credits = cursor.fetchall()
        cursor.close()
        return credits
    except Exception as error:
        print(f"Error retrieving credits for audit criteria {criteria_id}: {error}")
        return []

def get_sub_credits_for_criteria_credit(conn, criteria_credit_id):
    """
    Retrieves sub-credits for a specific assessment criteria credit.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT accs.description, accs.role, accs.credits, accs.assessment_stage
            FROM assessment_criteria_sub_credits accs
            WHERE accs.assessment_criteria_credit_id = %s;
        """
        cursor.execute(query, (criteria_credit_id,))
        sub_credits = cursor.fetchall()
        cursor.close()
        return sub_credits
    except Exception as error:
        print(f"Error retrieving sub-credits for criteria credit {criteria_credit_id}: {error}")
        return []

def get_minimum_standards_for_audit_criteria(conn, criteria_id):
    """
    Retrieves minimum standards associated with a specific assessment criteria.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT rl.rating, ms.minimum_standard
            FROM minimum_standards ms
            JOIN rating_levels rl ON ms.rating_level_id = rl.id
            JOIN assessment_criteria ac ON ms.assessment_criteria_id = ac.id
            WHERE ac.criteria_id = %s;
        """
        cursor.execute(query, (criteria_id,))
        standards = cursor.fetchall()
        cursor.close()
        return standards
    except Exception as error:
        print(f"Error retrieving minimum standards for audit criteria {criteria_id}: {error}")
        return []

def get_prerequisites_for_audit_criteria(conn, criteria_id):
    """
    Retrieves prerequisites associated with a specific assessment criteria.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT c.category_name, ai.issue_number, ai.issue_name, ac2.criteria_id, ac2.name
            FROM prerequisites p
            JOIN categories c ON p.category_id = c.id
            JOIN assessment_issues ai ON p.assessment_issue_id = ai.id
            JOIN assessment_criteria ac1 ON p.assessment_criteria_id = ac1.id
            JOIN assessment_criteria ac2 ON ac1.id = ac2.id
            WHERE ac1.criteria_id = %s;
        """
        cursor.execute(query, (criteria_id,))
        prerequisites = cursor.fetchall()
        cursor.close()
        return prerequisites
    except Exception as error:
        print(f"Error retrieving prerequisites for audit criteria {criteria_id}: {error}")
        return []

def get_category_weighting_for_audit_criteria(conn, criteria_id):
    """
    Retrieves the category weighting for the category associated with a specific assessment criteria.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT cw.weighting_percentage
            FROM category_weightings cw
            JOIN categories c ON cw.category_id = c.id
            JOIN assessment_issues ai ON c.id = ai.category_id
            JOIN assessment_criteria ac ON ai.id = ac.assessment_issue_id
            WHERE ac.criteria_id = %s;
        """
        cursor.execute(query, (criteria_id,))
        weighting = cursor.fetchone()
        cursor.close()
        return weighting['weighting_percentage'] if weighting else None
    except Exception as error:
        print(f"Error retrieving category weighting for audit criteria {criteria_id}: {error}")
        return None

def get_all_assessment_criteria(conn):
    """
    Retrieves all assessment criteria with their associated categories and issues.
    """
    try:
        cursor = conn.cursor(cursor_factory=DictCursor)
        query = """
            SELECT ac.criteria_id, ac.name, ac.description, ac.type,
                   ai.issue_number, ai.issue_name,
                   c.category_number, c.category_name
            FROM assessment_criteria ac
            JOIN assessment_issues ai ON ac.assessment_issue_id = ai.id
            JOIN categories c ON ai.category_id = c.id
            ORDER BY c.category_number, ai.issue_number, ac.criteria_id;
        """
        cursor.execute(query)
        criteria_list = cursor.fetchall()
        cursor.close()
        return criteria_list
    except Exception as error:
        print(f"Error retrieving all assessment criteria: {error}")
        return []
