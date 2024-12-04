import streamlit as st
import json
import time
import os
from dotenv import load_dotenv
from groq import Groq
from json_parser import extract_resume_data, update_resume
from latex.latex_format import process_json
from latex.latex_resume import latex_resume
from proj.project import analyze_projects
from exp.experience import analyze_exp
from skills.skill import analyze_skills
from cover_letter.cover import generate_cover_letter
from chatbot import handle_conversation, initialize_prompt_template,compile_application
from langchain_core.messages import HumanMessage, AIMessage
from job_desc.jd_parser import extract_job_description_details


load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=groq_api_key)

TEMP_RESUME_PATH = "temp_resume.pdf"
FINAL_RESUME_PATH = "resume.pdf"
COVER_LETTER_PATH = "cover_letter.pdf"
RESUME_JSON_PATH = "resume.json"
JD_PATH = "job_description.json"

st.title("Resume Builder")

st.sidebar.header("Upload Your Resume")
uploaded_file = st.sidebar.file_uploader("Upload your PDF Resume", type=["pdf"])

st.sidebar.header("Enter Job Description")
with st.sidebar.form("job_desc_form"):
    job_description = st.text_area("Paste the job description here", height=150)
    submit_button = st.form_submit_button("Submit")

if "resume_json" not in st.session_state:
    st.session_state.resume_json = None
if "job_description" not in st.session_state:
    st.session_state.job_description_json = None
if "resume_generated" not in st.session_state:
    st.session_state.resume_generated = False
if "cover_letter_generated" not in st.session_state:
    st.session_state.cover_letter_generated = False
if "threads" not in st.session_state:
    st.session_state.threads = {}

def load_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None


def save_json_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



if uploaded_file and submit_button:
   
    if not job_description.strip():
        st.warning("Job description cannot be empty.")
    else:
        try:
            with open(TEMP_RESUME_PATH, "wb") as f:
                f.write(uploaded_file.read())
            extract_resume_data(TEMP_RESUME_PATH, max_retries=5)
            extract_job_description_details(job_description)
            st.session_state.resume_json = load_json_file(RESUME_JSON_PATH)
            st.session_state.job_description_json = load_json_file(RESUME_JSON_PATH)

            if not st.session_state.resume_json:
                st.error("Error extracting data from the uploaded resume. Please try again.")
            else:
                st.session_state.job_description = job_description.strip()
                with open('jd.txt', 'w') as f:  
                    f.write(job_description.strip())


                st.success("Resume and job description are successfully loaded!")
        
        except Exception as e:
            st.error(f"An error occurred during resume processing: {e}")

if st.session_state.resume_json and st.session_state.job_description:
    st.subheader("Generate Your Document")
    document_option = st.selectbox(
        "Select the document you want to generate:",
        options=["Resume", "Cover Letter"]
    )

    if st.button("Generate Document"):
        try:
            if document_option == "Resume" and not st.session_state.resume_generated:
                st.info("Analyzing and generating the updated resume...")
                candidate_proj = st.session_state.resume_json.get('projects', [])
                candidate_exp = st.session_state.resume_json.get('work experience', [])
                candidate_skills = st.session_state.resume_json.get('skills', [])

                analyze_projects(candidate_proj,st.session_state.job_description_json)
                analyze_exp(candidate_exp, st.session_state.job_description_json)
                analyze_skills(candidate_skills, st.session_state.job_description_json)

                exp_json = load_json_file("experience.json")
                proj_json = load_json_file("project.json")
                skill_json = load_json_file("skills.json")

                updated_resume = update_resume(
                    st.session_state.resume_json, skill_json, exp_json, proj_json
                )
                save_json_file(updated_resume, "update_resume.json")
                with open('update_resume.json', 'r') as f:
                   updated_resume = json.load(f)

                escaped_resume = process_json(updated_resume)
                save_json_file(escaped_resume, "final_resume.json")

                with open('final_resume.json', 'r') as f:
                   escaped_resume = json.load(f)

                latex_resume(escaped_resume)

                st.session_state.document_generated = True
                time.sleep(5)
                st.success("Resume generated successfully!")
                st.download_button(
                    "Download Updated Resume",
                    data=open(FINAL_RESUME_PATH, "rb").read(),
                    file_name="updated_resume.pdf",
                    mime="application/pdf",
                )

            if document_option == "Cover Letter" and not st.session_state.cover_letter_generated:
                st.info("Generating the cover letter...")

                generate_cover_letter(
                    st.session_state.job_description_json, st.session_state.resume_json
                )

                st.session_state.document_generated = True
                st.success("Cover Letter generated successfully!")
                st.download_button(
                    "Download Cover Letter",
                    data=open(COVER_LETTER_PATH, "rb").read(),
                    file_name="cover_letter.pdf",
                    mime="application/pdf",
                )
        except Exception as e:
            st.error(f"An error occurred during document generation: {e}")

if "user_input1" not in st.session_state:
    st.session_state.user_input1 = ""  

if "response_generated" not in st.session_state:
    st.session_state.response_generated = False

if "threads" not in st.session_state:
    st.session_state.threads = {}


st.title("Job Assistant")
user_input1 = st.text_area("Ask a question", value=st.session_state.user_input1, key="user_input1")
if user_input1 != st.session_state.user_input1:
        st.session_state.user_input1 = user_input1

context = []
if st.button('Ask') and st.session_state.user_input1.strip():
        thread_id = "chatbot_thread_1"

        if thread_id not in st.session_state.threads:
            print('Entering the first loop')
            st.session_state.threads[thread_id] = {}  
            app = compile_application()  
            config = {"configurable": {"thread_id": thread_id}}  
            st.session_state.threads[thread_id] = {
                "app": app, 
                "config": config  
            }

            context.append(HumanMessage(content=f"Here is the resume: {json.dumps(st.session_state.resume_json)}"))
            context.append(HumanMessage(content=f"Here is the job description: {json.dumps(st.session_state.job_description_json)}"))
            
            output = app.invoke({"messages": context}, config)

        else:
            app = st.session_state.threads[thread_id]['app']
            config = st.session_state.threads[thread_id]['config']
        
        response = handle_conversation(
            st.session_state.user_input1,
            thread_id,
            st.session_state.resume_json,
            st.session_state.job_description,
            st.session_state.threads,app,config
        )

        st.session_state.response_generated = True
        st.session_state.chatbot_response = response
        st.write(response)

