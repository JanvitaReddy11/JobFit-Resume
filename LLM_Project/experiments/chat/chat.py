from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import HumanMessage, AIMessage
from groq import Groq
import os 
from dotenv import load_dotenv
from langchain_groq import ChatGroq
load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

model = ChatGroq(model="llama-3.2-3b-preview")

def initialize_prompt_template():
    
    """
    Initialize the chat prompt template with predefined instructions.
    """
    return ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a highly skilled assistant specialized in answering questions related to user profiles, particularly resumes and job descriptions. "
             "You will be provided with a resume (in JSON format) and a job description. Your task is to answer questions about the user's qualifications, "
             "provide insights about how well the resume aligns with the job description. "
             "You should be able to summarize the user's experience and answer questions in such a way that it aligns with the job description. "
             "Chances for the user to get selected increases."
             ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )


def initialize_workflow():
    """
    Set up the workflow for handling user queries.
    """
    workflow = StateGraph(state_schema=MessagesState)

    def call_model(state: MessagesState):
        """
        Function to handle the model invocation for a given state.
        """
        prompt = prompt_template.invoke(state)
        response = model.invoke(prompt)  # Replace with your actual model API call
        return {"messages": response}

    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)
    return workflow


def compile_application():
    """
    Compile the application with memory checkpointing.
    """
    workflow = initialize_workflow()
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def handle_conversation(user_input, thread_id, resume=None, job_description=None):
    """
    Manage conversation threads and handle user inputs.
    
    Args:
        user_input (str): User's question or input.
        thread_id (str): A unique identifier for the conversation thread.
        resume (dict, optional): User's resume in JSON format.
        job_description (str, optional): The job description text.

    Returns:
        str: The assistant's response to the latest user input.
    """
    # Initialize the threads if not already present
    if thread_id not in threads or resume or job_description:
        # Reset the thread if new context is provided
        threads[thread_id] = {
            "resume": resume,
            "job_description": job_description,
            "messages": [],
        }

        # Prepare the conversation context
        context = []
        if resume:
            context.append(HumanMessage(content=f"Here is the resume: {resume}"))
        if job_description:
            context.append(HumanMessage(content=f"Here is the job description: {job_description}"))

        # Add the user input as the latest message
        context.append(HumanMessage(content=user_input))
    else:
        # If thread exists and no new resume/job description, just add user input
        context = [HumanMessage(content=user_input)]

    # Invoke the chatbot application
    config = {"configurable": {"thread_id": thread_id}}
    output = app.invoke({"messages": context}, config)

    # Update the thread state
    threads[thread_id]["messages"] = output["messages"]

    # Return the latest response
    return output["messages"][-1].content


# Initialization
prompt_template = initialize_prompt_template()
app = compile_application()
threads = {}

# Example Usage
def respond_to_user(user_input, thread_id, resume, job_description):
    return handle_conversation(user_input, thread_id, resume, job_description)

# Example call
# response = respond_to_user(user_input="Describe why I am a good fit for this job", thread_id="thread_1", resume=resume_json, job_description=job_description)
