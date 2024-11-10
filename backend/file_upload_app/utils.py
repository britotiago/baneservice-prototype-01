import docx
import re

def extract_audit_criteria(file_name):
    doc = docx.Document(file_name)
    extracted_data = {}

    current_section = None
    current_sub_section = None

    for para in doc.paragraphs:
        text = para.text.strip()

        # Regex pattern to detect headings or sections
        section_match = re.match(r"^\d+(\.\d+)*\s.+", text)

        if section_match:
            current_section = text
            extracted_data[current_section] = {"content": "", "sub_section": None}
        elif text:
            if current_section:
                if text.startswith("Subsection"):
                    current_sub_section = text
                    extracted_data[current_section]["sub_section"] = current_sub_section
                else:
                    extracted_data[current_section]["content"] += f"\n{text}"

    return extracted_data
