
from groq import Groq
import os
import datetime
import subprocess
import time
from dotenv import load_dotenv
import json
from fpdf import FPDF

load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

class PDF(FPDF):
    """Custom PDF class to handle cover letter formatting."""
    def header(self):
        # Only add the "Cover Letter" heading on the first page
        if self.page_no() == 1:
            self.set_font('Arial', 'B', 14)
            self.cell(0, 12, 'Cover Letter', align='C', ln=1)
            self.ln(10)  # Add some space after the heading

def generate_cover_letter(job_description: dict, resume: dict) -> None:
    client = Groq(api_key=api_key)
  
    prompt = f"""
    You are an expert cover letter writer. Write a personalized cover letter for the following job description and resume:

    Job Description:
    {json.dumps(job_description, indent=4)}

    Resume:
    {json.dumps(resume, indent=4)}

    The cover letter should in the below format
    - Begin with 
    'Dear Hiring Manager'
    - First paragraph: Introduce the candidate and their background, highlighting relevant experience and skills.
    - Second paragraph: Detail experiences and projects, aligning them with the job requirements. Highlight how the projects and experience align with the job role.
    - Third paragraph: Explain why the candidate is ideal for the job and the company.
    - Be professional, concise, and tailored to the job requirements.

    Thanking you,
    candidate_name
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
            top_p=0.9,
            stream=False,
            stop=None,
        )

        # Extract the generated cover letter
        if completion.choices and completion.choices[0].message:
            cover_letter = completion.choices[0].message.content

            start_index = cover_letter.lower().find("dear")
            if start_index == -1:
                print('Error')
            else:
                cover_letter = cover_letter[start_index:]        

            pdf = PDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_left_margin(20)
            pdf.set_right_margin(20)
            pdf.set_font('Arial', size=10)


            for line in cover_letter.splitlines():
                pdf.multi_cell(0, 5, line, border=0, align='J')

            # Save the PDF
            output_file = "cover_letter.pdf"
            pdf.output(output_file)

            print(f"Cover letter successfully saved to '{output_file}'.")

        else:
            print("No response received from the LLM. Please try again.")

    except Exception as e:
        print(f"Error in LLM processing: {e}")
