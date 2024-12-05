import PyPDF2
import json
import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

def extract_job_description_details(job_description: str, max_retries=5):
    client = Groq(api_key=api_key)


    prompt = f"""
    Please extract the following information from the job description and format it as JSON with the following keys:
    - "role"
    - "company"
    - "job description"
    - "employment type" (e.g., full-time, part-time, contract,internship)
    - "key responsibilities" (a list of responsibilities as mentioned in the job description)
    - "required skills" (a list of explicitly mentioned skills)
    - "preferred qualifications" (if mentioned)
    - "other details" (any additional information provided in the description)
    
    Return the result as JSON only, with no additional explanation or formatting.

    Job Description:
    {job_description}
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
        with open('job_description.json', 'w') as outfile:
            json.dump(json_data, outfile, indent=4)
        print("Job Description JSON saved successfully!")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Raw output: {second_output}")
        return None
