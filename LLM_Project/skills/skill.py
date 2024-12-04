from groq import Groq
import os
import datetime
import subprocess
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
#client = Groq(api_key=api_key)

import json
import time

def analyze_skills(candidate_profile: dict, job_description, max_retries=5) -> None:
    client = Groq(api_key=api_key)
    # Step 1: Define prompt for the first LLM (Skills and Responsibilities Optimization)
    first_prompt = f"""
    You are a resume optimization expert for ATS compliance. Your task is to enhance the candidate's skills and modify it based on the job description:

    1. **Extract Key Skills and Responsibilities**:
       - Identify and list the key skills, responsibilities, and keywords from the job description that are essential for the ideal candidate.

    2. **Optimize the Candidate's Skills Section**:
       - Review the candidate's "Skills" section carefully.
       - Prioritize and rearrange skills based on relevance to the job description.
       - Remove irrelevant skills and avoid adding new or highly technical skills the candidate doesn't possess.
       - Add transferable, miscellaneous, analytical or any other skill section if applicable, ensuring they align with the job description and are somewhat consistent with the candidate’s profile.
       - Do not include any sections (e.g., "Cloud", "Programming Languages") if they have no corresponding skills or if adding them would result in an empty or visually redundant section. Remove the section entirely if empty.
       - You may add new sections only if they are relevant and include appropriate skills.
       - Return the output in JSON format, with each section containing only non-empty skill lists.

    3. **Output Format**:
       - Provide the optimized "Skills" section in compatible JSON format.

    ### Candidate Profile:
    {json.dumps(candidate_profile, indent=4)}

    ### Job Description:
    {json.dumps(job_description, indent=4)}

    Your output should be in the form of an enhanced JSON object for the "Skills" section.
    """

    try:
        # Step 2: Query the LLM for the optimized skills section
        first_response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": first_prompt}],
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9,
            stream=False,
            stop=None,
        )
        first_output = first_response.choices[0].message.content if first_response.choices else None

        if not first_output:
            print("First LLM did not produce a valid response.")
            return

        # Save the first output for review
        

        # Step 3: Retry parsing and saving JSON output up to max_retries times
        for attempt in range(1, max_retries + 1):
            print(f"Attempt {attempt} of {max_retries}...")

            second_prompt = f"""
            Extract and return only the JSON object from the following text. Do not include any extra explanations or comments.

            ### Input:
            {first_output}

            ### Output:
            Provide only the valid JSON object.
            """

            try:
                second_response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": second_prompt}],
                    temperature=0.3,
                    max_tokens=1024,
                    top_p=0.9,
                    stream=False,
                    stop=None,
                )
                second_output = second_response.choices[0].message.content if second_response.choices else None

                if not second_output:
                    print("Second LLM did not produce a valid response.")
                    continue

                # Validate the JSON output
                try:
                    extracted_json = json.loads(second_output.strip())
                    # Save the JSON file
                    with open("skills.json", "w") as file:
                        json.dump(extracted_json, file, indent=4)
                    print("Optimized skills JSON saved to 'skills.json'.")
                    return  # Exit loop if successful
                except json.JSONDecodeError:
                    print("Error parsing JSON from the second LLM response.")
                    print(f"Invalid JSON output: {second_output}")
                    # Continue to the next attempt

            except Exception as e:
                print(f"Error during LLM processing on attempt {attempt}: {e}")

            # Optional: Delay between retries
            time.sleep(1)

        print(f"Failed to extract valid JSON after {max_retries} attempts.")

    except Exception as e:
        print(f"Error during LLM processing: {e}")
