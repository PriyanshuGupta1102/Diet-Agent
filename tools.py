# tools.py

from langchain.tools import tool
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
# NEW: Import Google's embeddings model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.tools.retriever import create_retriever_tool

# Tools 1 and 2 (calculate_bmi, create_diet_plan) do not need any changes.
@tool
def calculate_bmi(height_m: float, weight_kg: float) -> str:
    """Calculates BMI... (code is the same)"""
    bmi = weight_kg / (height_m ** 2)
    bmi_rounded = round(bmi, 1)
    if bmi_rounded < 18.5: category = "Underweight"
    elif 18.5 <= bmi_rounded < 24.9: category = "Normal weight"
    elif 25 <= bmi_rounded < 29.9: category = "Overweight"
    else: category = "Obesity"
    return f"The calculated BMI is {bmi_rounded}, which is considered '{category}'."

@tool
def create_diet_plan(calories: int, dietary_preference: str) -> str:
    """Creates a basic one-day diet plan... (code is the same)"""
    if dietary_preference.lower() == 'vegetarian': protein_source = "tofu or lentils"
    else: protein_source = "chicken breast or fish"
    plan = f"""
    Here is a basic {calories} calorie diet plan for a '{dietary_preference}' preference:
    - Breakfast (approx. 400 cal): Oatmeal with berries and a handful of nuts.
    - Lunch (approx. 600 cal): Large salad with mixed greens, vegetables, {protein_source}, and a light vinaigrette.
    - Dinner (approx. 600 cal): Grilled {protein_source} with a side of quinoa and steamed broccoli.
    - Snack (approx. 200 cal): Greek yogurt or an apple with peanut butter.
    
    Disclaimer: This is a sample plan. Consult a professional for personalized advice.
    """
    return plan

# Tool 3: The knowledge base retriever tool
def get_retriever_tool():
    """Creates a tool for retrieving information from our nutrition knowledge base."""
    loader = TextLoader("./knowledge_base/nutrition_facts.txt")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # NEW: Use GoogleGenerativeAIEmbeddings and its required model name
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma.from_documents(texts, embeddings)
    retriever = vectorstore.as_retriever()
    
    retriever_tool = create_retriever_tool(
        retriever,
        "nutrition_facts_retriever",
        "Searches and returns information about general nutrition, diet principles, hydration, and calories."
    )
    return retriever_tool