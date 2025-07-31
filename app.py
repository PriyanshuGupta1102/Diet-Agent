# app.py

import streamlit as st
import os
import urllib.parse
from dotenv import load_dotenv

# Import our backend components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from tools import get_retriever_tool, calculate_bmi, create_diet_plan

# --- Import our NEW pantry manager ---
import pantry_manager

# --- 1. SETUP THE AI AGENT (No changes here) ---
@st.cache_resource
def get_agent_executor():
    load_dotenv()
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0)
    nutrition_retriever_tool = get_retriever_tool()
    tools = [calculate_bmi, create_diet_plan, nutrition_retriever_tool]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful and friendly AI diet and nutrition assistant..."), # Your system prompt
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    return agent_executor

# --- 2. HELPER FUNCTION FOR E-COMMERCE LINKS ---
def create_affiliated_link(item_name, platform):
    """Creates a search link for an item on an e-commerce platform."""
    # In a real app, you would have a real affiliate tag.
    AFFILIATE_TAG = "dietai-aff-123" 
    
    base_urls = {
        "Blinkit": "https://blinkit.com/s/?q=",
        "Zepto": "https://app.zeptonow.com/search?q=",
        "Instamart": "https://www.swiggy.com/instamart/search?query="
    }
    
    encoded_item = urllib.parse.quote_plus(item_name)
    search_url = f"{base_urls.get(platform, '')}{encoded_item}"
    
    # Append affiliate tag if the platform is supported
    if platform in base_urls:
        return f"{search_url}&tag={AFFILIATE_TAG}" # Example affiliate linking
    return search_url

# --- 3. SETUP THE STREAMLIT FRONTEND ---

st.set_page_config(page_title="DietAI & Pantry", layout="wide")
st.title("🍏 DietAI: Your Personal Nutrition & Pantry Assistant")

# Create two tabs
tab1, tab2 = st.tabs(["🤖 AI Chatbot", "🛒 Pantry Manager"])


# --- TAB 1: AI CHATBOT ---
with tab1:
    st.header("Chat with your AI Dietitian")

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hi! I'm DietAI. Ask me anything about nutrition!"}
        ]
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    agent_executor = get_agent_executor()

    # Display past chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input
    if prompt := st.chat_input("Ask me about nutrition..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent_executor.invoke({
                    "input": prompt,
                    "chat_history": st.session_state.memory.load_memory_variables({})['chat_history']
                })
                st.session_state.memory.save_context({"input": prompt}, {"output": response['output']})
                st.markdown(response['output'])
        
        st.session_state.messages.append({"role": "assistant", "content": response['output']})


# --- TAB 2: PANTRY MANAGER ---
with tab2:
    st.header("Manage Your Kitchen Pantry")

    # Load pantry data into session state to work with it
    if "pantry" not in st.session_state:
        st.session_state.pantry = pantry_manager.load_pantry()

    # Section to display pantry items
    st.subheader("Your Items")
    
    if not st.session_state.pantry:
        st.info("Your pantry is empty! Add an item below to get started.")

    # Create columns for a cleaner layout
    col_titles = st.columns((2, 1, 1, 3, 1))
    with col_titles[0]: st.write("**Item**")
    with col_titles[1]: st.write("**Quantity**")
    with col_titles[2]: st.write("**Use One**")
    with col_titles[3]: st.write("**Buy Now (Low Stock)**")
    with col_titles[4]: st.write("**Delete**")

    # Loop through a copy of the list to allow safe deletion
    for item in st.session_state.pantry[:]:
        is_low_stock = item['current_quantity'] <= item['low_stock_threshold']
        
        cols = st.columns((2, 1, 1, 3, 1))
        
        with cols[0]: # Item Name
            st.metric(label=item['name'], value=f"{item['current_quantity']} / {item['total_quantity']}")

        with cols[1]: # Quantity Progress
            st.progress(item['current_quantity'] / item['total_quantity'])

        with cols[2]: # Use One Button
            if st.button("🍽️ Use", key=f"use_{item['name']}"):
                if item['current_quantity'] > 0:
                    item['current_quantity'] -= 1
                    pantry_manager.save_pantry(st.session_state.pantry)
                    st.rerun()

        with cols[3]: # Buy Now Links (only if low stock)
            if is_low_stock:
                st.warning("Low Stock!")
                link_cols = st.columns(3)
                with link_cols[0]: st.link_button("Blinkit", create_affiliated_link(item['name'], "Blinkit"))
                with link_cols[1]: st.link_button("Zepto", create_affiliated_link(item['name'], "Zepto"))
                with link_cols[2]: st.link_button("Instamart", create_affiliated_link(item['name'], "Instamart"))

        with cols[4]: # Delete Button
            if st.button("🗑️", key=f"del_{item['name']}"):
                st.session_state.pantry.remove(item)
                pantry_manager.save_pantry(st.session_state.pantry)
                st.rerun()

    st.divider()

    # Section to add new items
    with st.expander("➕ Add a New Item to Your Pantry"):
        with st.form("new_item_form", clear_on_submit=True):
            item_name = st.text_input("Item Name (e.g., Eggs, Milk)")
            total_quantity = st.number_input("Total Quantity (e.g., 12 for a dozen eggs)", min_value=1, step=1)
            low_stock_threshold = st.number_input("Low Stock Warning Level", min_value=0, step=1)
            
            submitted = st.form_submit_button("Add Item")
            if submitted:
                if item_name:
                    new_item_data = {
                        "name": item_name,
                        "total_quantity": total_quantity,
                        "current_quantity": total_quantity,
                        "low_stock_threshold": low_stock_threshold
                    }
                    st.session_state.pantry.append(new_item_data)
                    pantry_manager.save_pantry(st.session_state.pantry)
                    st.success(f"Added {item_name} to your pantry!")
                    st.rerun()
                else:
                    st.error("Item name cannot be empty.")