from openai import OpenAI
import os
import requests
import re
import json
from dotenv import load_dotenv
from .file_extractors import extract_text_from_file

# Load OpenAI API key from environment
load_dotenv()
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Function to print prompts and responses clearly
def print_formatted(message, is_prompt=True):
    """
    Prints prompts and responses with clear formatting.
    """
    separator = "-" * 80
    if is_prompt:
        print(f"\n{separator}\nPROMPT SENT TO AI:\n{separator}\n{message}\n{separator}")
    else:
        print(f"\n{separator}\nAI RESPONSE:\n{separator}\n{message}\n{separator}")

# Function to send a prompt to OpenAI
def generate_summary_for_file(prompt):
    """
    Function to interact with OpenAI API using a given prompt.
    """
    print_formatted(prompt)  # Print the prompt being sent
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # You can use "gpt-4-32k" or other available models
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500  # Adjust based on chunk size
    )
    response = completion.choices[0].message.content
    print_formatted(response, is_prompt=False)  # Print the AI's response
    return response

# Step 1: Fetch audit criteria data from the API
def fetch_audit_criteria_data():
    """
    Fetches the audit criteria data from the API endpoint.
    """
    response = requests.get("http://backend:8000/api/process-criteria-data/")

    if response.status_code == 200:
        return response.json()['data']
    else:
        print(f"Failed to fetch criteria data. Status code: {response.status_code}")
        return None

# Step 2: Send criteria data to OpenAI to set context
def initialize_audit_criteria(criteria_data):
    """
    Sends the audit criteria data to OpenAI as context before processing files.
    """
    prompt = f"""
    Here is the relevant audit criteria data:
    - Category: {criteria_data['category']['category_name']} ({criteria_data['category']['category_number']})
      Summary: {criteria_data['category']['category_summary']}
    - Assessment Issue: {criteria_data['assessment_issue']['issue_name']} ({criteria_data['assessment_issue']['issue_number']})
      Aim: {criteria_data['assessment_issue']['aim']}
    - Assessment Criteria: {criteria_data['assessment_criteria']['name']}
      Description: {criteria_data['assessment_criteria']['description']}
    - Credits: {criteria_data['credits']}
    - Guidance: {', '.join(criteria_data['guidances'])}
    - Evidence: {', '.join([e['evidence_guidance'] for e in criteria_data['evidences']])}

    Please remember this information as context for reviewing the documentation files.
    """
    generate_summary_for_file(prompt)
    print("Audit Criteria Context Sent.")

# Step 3: Chunk a document into smaller pieces
def chunk_text(text, chunk_size=3000):
    """
    Breaks the text into manageable chunks based on the token limit.
    """
    words = text.split()
    chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

# Step 4: Process files in the directory
def process_files_in_directory(directory):
    """
    Process all files in the given directory, extracting text and chunking them.
    """
    file_summaries = []

    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        try:
            file_text = extract_text_from_file(file_path)
            chunks = chunk_text(file_text)
            file_summaries.append({'file_name': file_name, 'chunks': chunks})
        except Exception as e:
            print(f"Error extracting text from {file_name}: {e}")

    return file_summaries

# Step 5: Send file chunks to OpenAI
def send_file_chunks(file_summaries):
    """
    Sends chunks of each document one by one, telling the AI to remember them.
    """
    for file_summary in file_summaries:
        file_name = file_summary['file_name']
        chunks = file_summary['chunks']

        for i, chunk in enumerate(chunks):
            prompt = f"""
            You are reviewing a document named '{file_name}'.

            Here is chunk {i + 1} of this document. This is a section of the document text:

            {chunk}

            Please remember this information for later when generating the final response based on the provided audit criteria.
            """
            generate_summary_for_file(prompt)
            print(f"Chunk {i + 1} of {file_name} sent.")

# Step 6: Final prompt to generate summaries, descriptions, and points
def finalize_summaries(total_points, file_summaries, criteria_data):
    """
    Sends the final prompt to generate summaries, descriptions, and calculate points based on the provided JSON data.
    All content must be in Norwegian, and points should be formatted as "X av Y".
    """

    # Build the prompt with a recap of what was sent
    final_prompt = "Du har tidligere mottatt deler av følgende dokumenter. Vennligst husk innholdet og lag følgende basert på konteksten som er gitt nedenfor, og i norsk språk:\n\n"

    for i, file_summary in enumerate(file_summaries, 1):
        file_name = file_summary['file_name']
        final_prompt += f"- Dokument {i}: {file_name}\n"

    # Re-state the audit criteria data (e.g., credits, guidance, and evidence)
    final_prompt += f"""
    Her er relevant revisjonskriteriedata for referanse:
    - Kategori: {criteria_data['category']['category_name']} ({criteria_data['category']['category_number']})
      Sammendrag: {criteria_data['category']['category_summary']}
    - Revisjonsspørsmål: {criteria_data['assessment_issue']['issue_name']} ({criteria_data['assessment_issue']['issue_number']})
      Mål: {criteria_data['assessment_issue']['aim']}
    - Vurderingskriterium: {criteria_data['assessment_criteria']['name']}
      Beskrivelse: {criteria_data['assessment_criteria']['description']}
    - Veiledning: {', '.join(criteria_data['guidances'])}
    - Bevis: {', '.join([e['evidence_guidance'] for e in criteria_data['evidences']])}
    - Poeng:
    """

    # Loop through credits and add them to the prompt
    for credit in criteria_data['credits']:
        final_prompt += f"  - {credit['assessment_stage']}: {credit['credits_value']} (Delpoeng: {credit.get('sub_credit_value', 'N/A')})\n"

    # Add instructions for summaries, descriptions, and points calculation in JSON format
    #Samsvarsbeskrivelsen må bevise hvilke tiltak som har blitt gjort for å bestå revisjonskriteriet. Må peke på side
    #Formålet med prosjekt er å gjøre at miljøarbeidere unngår å gå gjennom dokumentet for å finne bevis på hvordan revisjonskriteriet ble møtt. Det må være kildehenvisning, det krever revisor. Bevisene må pekes hvor de ligger.
    #Den skal basert på kravene i manualen, beskrive tiltak som har blitt gjort og peke på bevise med kildehenvisning og dokument.
    # Send mail med ønsker og hva du trenger for å gjøre modellen bedre og teste frem og tilbake for å produsere noe som er nesten identisk til svarene du allerede har.
    final_prompt += f"""
    Basert på disse dokumentene og de gitte revisjonskriteriene, bruk bare informasjon og data som du har blitt gitt, og generer følgende på norsk i JSON-format:
    
    1. Basert på kravene i relevant revisjonskriteriedata, beskriv tiltak som har blitt gjort (110-350 tegn), og pek på bevis med kildehenvisning med sidetall og dokument.
        Her er noen eksempler. Ikke kopier, ta det som inspirasjon:
        - Visuell påvirkning i anleggsfasen er inkludert i prosjektets miljøplan (Miljørisikovurdering og Miljøplan SUN01) kapittel 1.3.2, som tar for seg viktigheten av avfallssortering, system for lagring av masser og materialer, i tillegg til generell opprydning etter arbeid. 
        - Bane NOR har månedlige kampanje med ulike tema, hvor mai 2023 hadde tema orden og ryddighet. Kampanjene distribueres internt hos Bane NOR og videreføres til entreprenørene. Kampanjen beskriver hvordan materialer og utstyr skal lagres langs jernbanen, støvdempende tiltak, god merking for kildesortering, generell orden og ryddighet (Orden og ryddighet mai 2023). 
    2. En unik beskrivelse for hvert dokument (30-110 tegn), basert på spesifikt innhold i dokumentet.
    3. Beregn opptjente poeng ut av totalt {total_points} for hele prosjektet. Poengene skal reflektere hvor godt dokumentene oppfyller poengene, veiledningen, og bevisene som er gitt ovenfor.

    Svaret skal følge dette formatet:

    {{
        "compliance_description": [
            {{
                "document_number": "01",
                "summary": "Bærekraftige prinsipper og klima- og miljømål for prosjektet er satt av Byggherre i dokument D4.6 under avsnitt 2 og 3.1 – 3.9."
            }},
            {{
                "document_number": "02",
                "summary": "Spesifikke klima og miljømål og krav for prosjektet er beskrevet i Byggherrens MOP (miljøoppfølgingsplan), UVB-03-A-10408_02B, under avsnitt 4.1-4.5."
            }}
        ],
        "attachments": [
            {{
                "number": "01",
                "name": "D4.6 Spesialle krav til Klima og miljø",
                "description": "Byggherrens overordnede klima og miljømål for utbyggingen."
            }},
            {{
                "number": "02",
                "name": "UVB-03-A-10408_02B",
                "description": "Byggherrens MOP (Miljøoppfølgingsplan)."
            }}
        ],
        "total_points": X av {total_points}"
    }}
    """

    # Send the final prompt to the AI
    response = generate_summary_for_file(final_prompt)

    return response

# Step 7: Calculate total points based on criteria
def calculate_total_points(criteria_data):
    """
    Calculate the total points based on the construction stage in the audit criteria data.
    It extracts the maximum number from the 'credits_value' field for the construction stage.
    """
    total_points = 0

    for credit in criteria_data['credits']:
        # Only consider credits from the 'construction' assessment stage
        if credit['assessment_stage'] == 'construction':
            # Extract the numeric value from the 'credits_value' field (e.g., "up to 13")
            match = re.search(r'\d+', credit['credits_value'])
            if match:
                points = int(match.group())
                # Take the maximum of the current total_points and this points value
                total_points = max(total_points, points)

    return total_points

def save_response_as_json(response, file_path):
    try:
        # Check for triple backticks and remove them
        if response.startswith("```json") and response.endswith("```"):
            # Strip the triple backticks and any newlines or spaces around the JSON data
            cleaned_response = response[7:-3].strip()
        else:
            cleaned_response = response.strip()

        # Convert the cleaned string to a JSON object
        response_data = json.loads(cleaned_response)

        # Write JSON data to a file
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(response_data, file, indent=4)
        print(f"JSON data saved to {file_path}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode response as JSON. Error: {e}")
    except Exception as e:
        print(f"An error occurred while saving the JSON data: {e}")

# Main execution flow
if __name__ == "__main__":
    # Path to the directory containing files
    directory = os.path.join(os.path.dirname(__file__), '..', 'media', 'uploads')

    # Step 1: Fetch audit criteria data from the API
    criteria_data = fetch_audit_criteria_data()

    if not criteria_data:
        print("No criteria data found.")
    else:
        initialize_audit_criteria(criteria_data)

        file_summaries = process_files_in_directory(directory)

        send_file_chunks(file_summaries)

        total_points = calculate_total_points(criteria_data)
        final_response = finalize_summaries(total_points, file_summaries, criteria_data)

        print("Final response content for debugging:", final_response)  # Debugging print
        save_response_as_json(final_response, 'final_output.json')
