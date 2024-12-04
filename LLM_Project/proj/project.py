
from groq import Groq
import os
import datetime
import subprocess
import time
from dotenv import load_dotenv
import json

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)


def analyze_projects(candidate_proj: dict, job_description: dict) -> None:
    # Step 1: Define the refined prompt for the LLM (this will optimize the project section)
    client = Groq(api_key=api_key)
    prompt = f"""
    You are an expert resume writer and a professional ATS (Applicant Tracking System) optimization specialist. Your task is to enhance the candidate's "Project" section in their profile to make it more aligned with the provided job description. Follow the steps below carefully:

    1. **Analyze the Job Description**:
       - Extract the key responsibilities, skills, technologies, and metrics that are critical for the role.
       - Focus on the most important aspects that the ideal candidate should demonstrate.

    2. **Optimize the Candidate's Project Section**:
       - Carefully review the "Project" section in the candidate's profile.
       - For each bullet point:
         - Start with a strong, impactful action verb (e.g., "Led," "Developed," "Implemented").
         - Follow the STAR method to ensure each project is well-structured:
         - Quantify achievements wherever possible using existing metrics, but **do not add new metrics**.
         - Emphasize relevant skills, technologies, software, and accomplishments that align with the job description.
         - Avoid repetition of action verbs, ensuring each sentence introduces a new verb for variety.
         - Ensure that the content aligns closely with the job description and highlights the candidate's most relevant skills.
         - If appropriate, incorporate relevant keywords from the job description in the project description that can improve ATS compatibility, but only if they make sense in context.
         - Prioritize relevance to the specific job over general achievements.

    3. **Ethics and Integrity**:
       - Do **not** invent new accomplishments or metrics.
       - Avoid exaggerations—keep the information truthful while optimizing the content for clarity and ATS compatibility.

    4. **Format the Output**:
       - Return the optimized "Project" section in JSON format, structured in the same way as the candidate's original profile (e.g., under the "project" section).
       - Ensure the response is clearly formatted and valid JSON without any extra comments or explanations.

    ### Input: Candidate Profile
    {json.dumps(candidate_proj, indent=4)}

    ### Input: Job Description
    {json.dumps(job_description, indent=4)}

    Your output should only include:
    - The optimized "Project" section in JSON format, without any additional explanations.

    Ensure your response is ATS-friendly, realistic, and maintains the integrity of the candidate’s profile while making it more appealing to hiring managers.
    """

    try:
        # Step 2: Query the LLM to optimize the project section
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Replace with your actual model name
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9,
            stream=False,
            stop=None,
        )

        # Extracting the content from the first LLM response
        if completion.choices and completion.choices[0].message:
            first_output = completion.choices[0].message.content
        

            # Step 3: Define the second prompt for JSON extraction
            second_prompt = f"""
            You are a JSON parser and validator. Your task is to extract only the JSON object from the following text, ensuring it is valid and well-formed. Do not include any additional explanations or comments in your response.

            ### Input:
            {first_output}

            ### Output:
            Provide only the JSON object.
            """
            
            second_response = client.chat.completions.create(
                model="llama3-70b-8192",  # Replace with your actual model name
                messages=[{"role": "user", "content": second_prompt}],
                temperature=0.3,
                max_tokens=1024,
                top_p=0.9,
                stream=False
            )

            # Extract the second output
            second_output = second_response.choices[0].message.content if second_response.choices else None

            if not second_output:
                print("Second LLM did not produce a valid response.")
                return

            # Retry mechanism for saving the JSON up to 5 times in case of issues
            retries = 5
            for attempt in range(retries):
                try:
                    # Attempt to load the JSON from the second LLM response
                    extracted_json = json.loads(second_output.strip())
                    
                    # Write the JSON to a file
                    with open("project.json", "w") as file:
                        json.dump(extracted_json, file, indent=4)
                    
                    print("Optimized project JSON saved to 'project.json'.")
                    break  # Exit the retry loop if the operation succeeds

                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON (Attempt {attempt + 1}/{retries}): {e}")
                    print(f"Invalid JSON output: {second_output}")
                    if attempt < retries - 1:  # Retry if there are attempts left
                        time.sleep(2)  # Optional: Add a delay before retrying
                    else:
                        print("Max retries reached. Could not parse the JSON.")
                        return

        else:
            print("No valid response received from the first LLM.")

    except Exception as e:
        print(f"Error in LLM processing: {e}")
