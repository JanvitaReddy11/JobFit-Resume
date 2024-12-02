# JobFit-Resume

JobFit Resume aims to address this issue of users manually tailoring the resume for every job application which is prone to human errors, by creating a resume and cover letter that aligns with the job description. The primary goal of the JobFit Resume project is to save time for job seekers, enhance the quality of their applications, and ultimately improve their chances of securing interviews in a challenging job market.

1] Resume Parsing and User Profile Extraction:
   Uses Llama 3.2 70B LLM to parse and convert resumes into structured JSON format.
   Ensures accurate extraction with retries for consistent output.

2] Job Description Analysis:
    Extracts keywords, skills, and requirements from job descriptions into a structured JSON format for easy integration.
    
3] Customized Resume Generation:
    Highlights JD-relevant skills while removing irrelevant ones.
    Avoids adding skills not present in the original resume.
    Reframes content using action verbs and the STAR method.
    Emphasizes JD-relevant details and quantifies achievements.
    Outputs a tailored resume in LaTeX format converted to PDF.

4] Cover Letter Generation
    Automatically generates cover letter focusing on the candidate’s profile, JD alignment, and interest in the role.

5] ChatBot Integration
    Uses Langraph for conversational state management.
    Assists users in answering additional application questions, aligning responses with their profile and the JD.

### Steps:
1] Install dependencies: pip install -r requirements.txt.
2] Create a .env file and add your Groq API key as GROQ_API_KEY=<your-api-key>.
3] Run the application: streamlit run app.py.
