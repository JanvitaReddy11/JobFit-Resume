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


load_dotenv()
api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)


model = ChatGroq(model="llama-3.2-3b-preview")
def initialize_prompt_template():
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

def initialize_workflow():
    workflow = StateGraph(state_schema=MessagesState)
    prompt_template = initialize_prompt_template()  

    def call_model(state: MessagesState):
       
        prompt = prompt_template.invoke(state)
        response = model.invoke(prompt) 
        return {"messages": response}

    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)
    return workflow


def compile_application():
    workflow = initialize_workflow()
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

def handle_conversation(user_input, thread_id, resume, job_description, threads,app,config):
  
    context = [HumanMessage(content=user_input)]
    output = app.invoke({"messages": context}, config)
    return output["messages"][-1].content
