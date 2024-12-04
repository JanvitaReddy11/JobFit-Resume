import streamlit as st
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_core.messages import HumanMessage, AIMessage
from groq import Groq
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import json

# Load environment variables
load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

# Initialize the model
model = ChatGroq(model="llama-3.2-3b-preview")

# Initialize the prompt template
def initialize_prompt_template():
    """
    Initialize the chat prompt template with predefined instructions.
    """
    return ChatPromptTemplate.from_messages(
        [
            ("system",
             "You are a highly skilled assistant specialized in answering questions related to user profiles, particularly resumes and job descriptions. "
             "You will be provided with a resume (in JSON format) and a job description. Your task is to answer questions about the user's qualifications, "
             " You should give answers in a precose way, that aligns with the job description"
             "You should give answers related to the user resume and not make up your own projects or experiences"
             "Chances for the user to get selected increases."
             ),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )

# Initialize the workflow for handling user queries
def initialize_workflow():
    """
    Set up the workflow for handling user queries.
    """
    workflow = StateGraph(state_schema=MessagesState)
    prompt_template = initialize_prompt_template()  # Initialize the prompt template

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

# Compile the application with memory checkpointing
def compile_application():
    """
    Compile the application with memory checkpointing.
    """
    workflow = initialize_workflow()
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

# Handle the conversation based on the provided user input and thread ID
def handle_conversation(user_input, thread_id, resume, job_description, threads,app,config):
    # Check if thread exists or new context is provided
    
    context = [HumanMessage(content=user_input)]

    # Invoke the chatbot application
    
    output = app.invoke({"messages": context}, config)

    # Return the latest response
    return output["messages"][-1].content