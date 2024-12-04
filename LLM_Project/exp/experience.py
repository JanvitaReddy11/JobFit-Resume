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



def analyze_exp(candidate_profile: dict, job_description: dict, max_trials: int = 5) -> None:
    client = Groq(api_key=api_key)
    # Step 1: Define the prompt for optimizing the experience section
    prompt = f"""
    You are an expert resume writer focused on optimizing profiles for ATS (Applicant Tracking System) compliance and job application success. Your task is to enhance the candidate's "Experience" section based on the provided job description:

    1. **Extract Key Responsibilities and Achievements**:
       - From the job description, identify and extract key responsibilities and metrics associated with the ideal candidate's role.

    2. **Optimize the Candidate’s Experience Section**:
       - Carefully review the "Experience" section and rewrite each bullet point to align with the job description and ATS compatibility.
       - Follow the STAR method (Situation, Task, Action, Result) format to describe each experience.
       - Use strong action verbs, quantify achievements if metrics are available, and prioritize relevance.
       - Avoid repetition of action verbs and overuse of words.
       - Ensure each bullet point aligns with the job description and highlights the candidate's relevant skills and achievements.
       - If appropriate, incorporate relevant keywords from the job description in the experiences description that can improve ATS compatibility, but only if they make sense in context.
        - Prioritize relevance to the specific job over general achievements.

    3. **Ethics and Integrity**:
       - Do not invent new accomplishments or metrics.
       - Keep the information truthful and concise.

    4. **Output Format**:
       - Provide the optimized "Experience" section in valid JSON format.
       - The output must only contain the updated "Experience" section and nothing else.

    ### Candidate Profile:
    {json.dumps(candidate_profile, indent=4)}

    ### Job Description:
    {json.dumps(job_description, indent=4)}
    """

    try:
        # Step 2: Query the LLM for optimization
        completion = client.chat.completions.create(
            model="llama3-70b-8192",  # Replace with your model name
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9,
            stream=False,
            stop=None,
        )

        if not (completion.choices and completion.choices[0].message):
            print("No valid response received from the LLM.")
            return

        first_output = completion.choices[0].message.content

        second_prompt = f"""
        You are a JSON parser. Extract only the valid JSON object from the following text without any additional explanation.

        ### Input:
        {first_output}

        ### Output:
        Provide only the JSON object.
        """

        second_response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": second_prompt}],
            temperature=0.3,
            max_tokens=1024,
            top_p=0.9,
            stream=False,
            stop=None,
        )

        if not (second_response.choices and second_response.choices[0].message):
            print("No valid response received for JSON extraction.")
            return

        second_output = second_response.choices[0].message.content

        # Attempt to save the JSON object, retrying up to max_trials
        for attempt in range(max_trials):
            try:
                extracted_json = json.loads(second_output.strip())
                with open("experience.json", "w") as file:
                    json.dump(extracted_json, file, indent=4)
                print("Optimized experience JSON saved to 'experience.json'.")
                return
            except json.JSONDecodeError:
                print(f"Trial {attempt + 1}/{max_trials}: Error parsing JSON. Retrying...")
                time.sleep(1)  # Optional delay before retry

        print("Failed to parse and save JSON after maximum retries.")

    except Exception as e:
        print(f"Error in LLM processing: {e}")
