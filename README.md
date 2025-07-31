# 🍏 DietAI - Your Personal AI Nutrition Agent

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

DietAI is a smart, conversational AI-powered chatbot designed to be your personal nutrition assistant. It can generate fully personalized 7-day diet plans based on your specific needs, answer general nutrition questions, and can be easily embedded into any existing website with a simple code snippet.

The project follows a modern decoupled architecture, with a powerful FastAPI backend handling the AI logic and a lightweight, dependency-free HTML/CSS/JS widget for the frontend.

###  Demo

 
*(This is a placeholder GIF. You can replace it by recording your own screen!)*

---

## ✨ Features

- **Personalized 7-Day Meal Plans:** Go through an interactive, one-by-one question flow to generate a detailed week-long diet schedule tailored to your goals.
- **General Nutrition Q&A:** Leverages Retrieval-Augmented Generation (RAG) to answer general questions about food, macros, and healthy eating from a knowledge base.
- **Interactive Data Collection:** A user-friendly "slot-filling" conversation to gather user details (age, weight, goals, etc.) without overwhelming them.
- **Embeddable Web Widget:** A self-contained chat widget built with vanilla HTML, CSS, and JavaScript that can be added to any website.
- **Dynamic UI:** The chat widget is movable and resizable, providing a seamless user experience.
- **Powered by Gemini & LangChain:** Utilizes Google's powerful Gemini model through the LangChain framework for intelligent responses and tool usage.

---

## 🛠️ Tech Stack

- **Backend:**
  - **Framework:** FastAPI
  - **AI Orchestration:** LangChain
  - **LLM:** Google Gemini (`gemini-1.5-flash-latest`)
  - **Vector Database:** ChromaDB (for RAG)
  - **Server:** Uvicorn
- **Frontend:**
  - **Languages:** HTML, CSS, JavaScript (Vanilla)
  - **Libraries:** Marked.js (for rendering Markdown)
- **Core Language:** Python 3.9+

---

## 🚀 Getting Started

Follow these instructions to get the project running on your local machine.

### Prerequisites

- Python 3.9 or higher
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/YourUsername/diet-agent-ai.git
cd diet-agent-ai
