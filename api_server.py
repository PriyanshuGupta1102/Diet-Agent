# api_server.py

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

# Import our backend components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from tools import get_retriever_tool, calculate_bmi, create_diet_plan

# --- AGENT SETUP ---
load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.5) # Slightly higher temp for more creative meal plans

tools = [get_retriever_tool(), calculate_bmi, create_diet_plan]

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful and friendly AI diet and nutrition assistant. Your name is DietAI. For general questions, answer them. When asked to create a diet plan with user details, create a comprehensive plan. If you need more information to create a plan, ask for it."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


# --- UNIFIED MEMORY & STATE MANAGEMENT ---
session_data = {}

def get_session(session_id: str):
    if session_id not in session_data:
        session_data[session_id] = {
            "memory": ConversationBufferMemory(memory_key="chat_history", return_messages=True),
            "plan_state": None,
        }
    return session_data[session_id]

PLAN_QUESTIONS = [
    {"key": "age_gender", "prompt": "I can definitely help with that! To create a personalized plan, I need some information. First, could you tell me your age and gender?"},
    {"key": "height_weight", "prompt": "Great. What is your current height and weight? (e.g., 175cm, 70kg)"},
    {"key": "activity_level", "prompt": "Thanks. How would you describe your activity level? (e.g., sedentary, lightly active, moderately active, very active)"},
    {"key": "preferences", "prompt": "Almost there. Do you have any dietary preferences or restrictions? (e.g., vegetarian, vegan, allergies to nuts, etc.)"},
    {"key": "goals", "prompt": "Finally, what is your primary goal? (e.g., weight loss, muscle gain, maintenance)"}
]

# --- API DEFINITION ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
async def chat(request: ChatRequest):
    session = get_session(request.session_id)
    memory = session["memory"]
    user_message = request.message

    if session["plan_state"]:
        state = session["plan_state"]
        question_index = state["question_index"]
        
        last_question_key = PLAN_QUESTIONS[question_index - 1]["key"]
        state["data"][last_question_key] = user_message
        
        if question_index < len(PLAN_QUESTIONS):
            next_question = PLAN_QUESTIONS[question_index]["prompt"]
            state["question_index"] += 1
            return {"response": next_question}
        else:
            collected_data = state["data"]
            
            # --- THE ONLY CHANGE IS HERE ---
            # We are creating a more detailed prompt to ask for a full week's schedule.
            final_prompt = f"""
            Please create a personalized and detailed **full one-week (7-day) diet schedule** for a user with the following details:
            - **Age and Gender:** {collected_data['age_gender']}
            - **Height and Weight:** {collected_data['height_weight']}
            - **Activity Level:** {collected_data['activity_level']}
            - **Dietary Preferences/Restrictions:** {collected_data['preferences']}
            - **Primary Goal:** {collected_data['goals']}

            **Instructions for the plan:**
            1.  Structure the plan day-by-day (e.g., Monday, Tuesday, Wednesday, etc.).
            2.  For each day, provide suggestions for **Breakfast, Lunch, Dinner, and one or two healthy Snacks**.
            3.  Please try to include some variety in the meals throughout the week to keep it interesting.
            4.  Include a brief disclaimer at the end that this is a sample plan and consulting a professional is recommended for medical advice.
            """
            
            response = agent_executor.invoke({
                "input": final_prompt,
                "chat_history": memory.load_memory_variables({})['chat_history']
            })
            
            memory.save_context({"input": "All my details have been provided."}, {"output": response['output']})
            session["plan_state"] = None # Reset state
            return {"response": response['output']}

    # Handle general conversation
    if "diet plan" in user_message.lower() or "create a plan" in user_message.lower():
        session["plan_state"] = {"question_index": 1, "data": {}}
        first_question = PLAN_QUESTIONS[0]["prompt"]
        memory.save_context({"input": user_message}, {"output": first_question})
        return {"response": first_question}
    else:
        response = agent_executor.invoke({
            "input": user_message,
            "chat_history": memory.load_memory_variables({})['chat_history']
        })
        memory.save_context({"input": user_message}, {"output": response['output']})
        return {"response": response['output']}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)