import PyPDF2
import json
import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

def extract_resume_data(pdf_path: str, max_retries=5):
    client = Groq(api_key=api_key)
    my_resume = ''
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            for page in pdf_reader.pages:
                my_resume += page.extract_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None
    

    load_dotenv()
   
    prompt = f"""
    Please extract the following information from the resume and format it as JSON with the following keys:
- Note when ever you come across the duration dont add any special characeters just give like Jan 2023. That much
- "name"
- "contact" (subkeys: "phone", "email", "linkedin", "github")
-"education" (an array of objects with "degree","major" "institution", "location", "duration (eg like Jan 23 - March 23 format)", "cgpa (eg 8/10)")
- "skills" (grouped by type as keys with arrays of values)
- 
- "work experience" (an array of objects with "title", "company (only the name of company and not location or country or place)", "location", "duration (In Month Year like Jan 23 format)", "responsibilities (give a list of it whatever is mentioned, do not eliminate words)")
- "projects" (an array of objects with "title", "description(give a list of it whatever is mentioned, do not eliminate words))")
Return the result as JSON only, with no additional explanation or formatting.


    Resume:
    {my_resume}
    """

    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192", 
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                stream=False,
            )
            first_output = completion.choices[0].message.content if completion.choices else ""
            break
        except Exception as e:
            print(f"Error in Groq API call (Attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(2)
            else:
                print("Max retries reached, exiting.")
                return None

    prompt2 = f"""
    You are a JSON parser and validator. Your task is to extract only the JSON object from the following text, ensuring it is valid and well-formed. Do not include any additional explanations or comments.

    ### Input:
    {first_output}

    ### Output:
    Provide only the JSON object.
    """
    
    for attempt in range(max_retries):
        try:
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt2}],
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
                stream=False,
            )
            second_output = completion.choices[0].message.content if completion.choices else ""
            break
        except Exception as e:
            print(f"Error in Groq API call for JSON extraction (Attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                print("Retrying...")
                time.sleep(2)
            else:
                print("Max retries reached, exiting.")
                return None

    try:
        json_data = json.loads(second_output)
        with open('resume.json', 'w') as outfile:
            json.dump(json_data, outfile, indent=4)
        print("Resume JSON saved successfully!")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw output: {second_output}")
        return None
    



def update_resume(original_resume,skill_json,exp_json,proj_json) -> dict:
    resume = original_resume.copy()
    resume['skills'] = skill_json
    resume['work experience'] = exp_json
    resume['projects'] = proj_json
    
    return resume



