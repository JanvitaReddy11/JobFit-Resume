import PyPDF2
import json
import os
from dotenv import load_dotenv
from groq import Groq
from chatbot.chat import  respond_to_user


from json_parser import extract_resume_data, update_resume
from latex_format import escape_latex_special_chars, process_json, compile_tex_file
from latex_resume import latex_resume
from proj.project import analyze_projects
from exp.experience import analyze_exp
from skills.skill import analyze_skills
from cover_letter.cover import generate_cover_letter

resume_path = 'C:/Users/reddy/Downloads/LLM_Project/Sarin_Mohit.pdf'
job_description = """
 About the job
Software Engineer (Python) - 100% Remote! 



Optomi in partnership with a leader in the sustainable energy is seeking a talented Software Engineer to join a dynamic and innovative technology team. In this role, you will be instrumental in designing, developing, and implementing software solutions that enhance our energy infrastructure and drive operational efficiencies. You will work on cloud-native applications, data processing systems, and infrastructure automation to support key projects that impact millions of customers.



Key Responsibilities:

Design, develop, and maintain scalable software solutions using Python and Java.
Build and manage infrastructure-as-code solutions using Terraform on AWS.
Develop data processing pipelines using Apache Hudi and Flink for real-time and batch processing applications.
Collaborate with cross-functional teams to architect and deploy cloud-based solutions on AWS.
Ensure high performance, reliability, and scalability of software systems through automated testing and monitoring.
Participate in the full software development lifecycle, including requirements gathering, design, development, testing, deployment, and maintenance.
Optimize and maintain data storage and processing systems to meet business requirements.
Troubleshoot and resolve software defects and infrastructure issues in a timely manner.
Contribute to best practices in coding, testing, and continuous integration and deployment (CI/CD).


Must-Have Qualifications:

4+ years of hands-on experience in software development with Python and Java.
Strong experience with AWS cloud services (e.g., EC2, S3, Lambda, RDS, etc.).
Proficiency in managing infrastructure-as-code using Terraform.
Experience working with Apache Hudi and Apache Flink for large-scale data processing.
Solid understanding of modern software development practices (e.g., version control, CI/CD pipelines, unit testing, etc.).
Excellent problem-solving skills and the ability to work collaboratively in a team environment.


Nice-to-Have Qualifications:

Experience with additional cloud platforms (e.g., Azure or Google Cloud).
Familiarity with microservices architecture and containerization tools (e.g., Docker, Kubernetes).
Knowledge of energy sector technologies and challenges.
Experience with data lake architecture and stream processing frameworks.
Strong understanding of security best practices in cloud environments.


"""


extract_resume_data(resume_path, max_retries=5)
with open('resume.json') as f:
    resume_json = json.load(f)
candidate_proj = resume_json['projects']
candidate_exp = resume_json['work experience']
candidate_skills = resume_json['skills']


analyze_projects(candidate_proj, job_description)
analyze_exp(candidate_exp,job_description)
analyze_skills(candidate_skills, job_description)

print('Running')

with open('experience.json', 'r') as exp_file:
    exp_json = json.load(exp_file)

with open('project.json', 'r') as proj_file:
    proj_json = json.load(proj_file)

with open('skills.json', 'r') as skill_file:
    skill_json = json.load(skill_file)

print('Running')

resume = update_resume(resume_json,skill_json,exp_json,proj_json)
with open('final_resume.json','w') as f:
    json.dump(resume, f, indent=4)


with open('final_resume.json', 'r', encoding='utf-8') as f:
    data = json.load(f)


escaped_data = process_json(data)

# Save the updated JSON file
with open('updated_resume.json', 'w', encoding='utf-8') as f:
    json.dump(escaped_data, f, ensure_ascii=False, indent=4)

with open('updated_resume.json','r') as f:
    candidate_data = json.load(f)


latex_resume(candidate_data)
generate_cover_letter(job_description,resume_json)















