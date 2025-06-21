
# 🚀 Prompt2Data

**Prompt2Data** is a conversational AI tool that turns natural language prompts into structured data specifications. It helps automate dataset generation by capturing goals, schema, and metadata — starting with an intelligent prompt interpreter powered by Claude 4.

> Think of it as ChatGPT for dataset design and pipeline automation.

---

## ✨ Features

- 🧠 Prompt-to-JSON task parsing using Claude 4 (Anthropic)
- 💬 Continuous chat context using Streamlit
- 📦 Outputs a fully structured spec: goal, data fields, location, time, format
- 🔁 Remembers past instructions, updates specs incrementally
- ✅ Plug-in ready for multi-agent expansion (dataset search, cleaning, etc.)

---

## 🧰 Tech Stack

- Python 3.9+
- Streamlit (for UI)
- Anthropic Claude API (for intent parsing)
- Dotenv (for API key handling)

---

## 🧑‍💻 Local Development Setup (Windows)

### ✅ Prerequisites

- [Python 3.9+](https://www.python.org/downloads/windows/)
- A GitHub account (for cloning)
- A free [Anthropic Claude API Key](https://console.anthropic.com)

---

### 🛠 Step-by-Step Instructions

#### 1. Clone the Repo
```bash
git clone https://github.com/your-username/Prompt2Data.git
cd Prompt2Data
```

#### 2. Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

> ⚠️ On first use: you may need to run this in **PowerShell** with execution enabled:  
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> ```

#### 3. Install Dependencies
```bash
pip install streamlit anthropic python-dotenv
```

> Optionally save them for others:
```bash
pip freeze > requirements.txt
```

#### 4. Create `.env` File
In your root folder, add a new file called `.env`:
```
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
```

> 🔐 Get your API key from: [https://console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

#### 5. Folder Structure Should Look Like:
```
Prompt2Data/
├── venv/
├── .env
├── intent_ui.py
├── intent_agent.py
├── requirements.txt
```

---

### ▶️ Run the App

```bash
streamlit run intent_ui.py
```

It will open a browser window at:  
`http://localhost:8501`

---

## 💡 Example Prompts

> I want data on housing prices and crime rates in California  
> Make it from 2010 to 2020  
> Output should be a CSV  
> Add air quality if available

Each message updates your task spec!

---

## 📌 Roadmap

- [x] Intent Agent (Claude-powered)
- [ ] Dataset Search Agent
- [ ] Schema Alignment Agent
- [ ] Cleaning & Feature Engineering Agent
- [ ] Model Validation Agent
- [ ] Dataset Export + Report PDF

---

## 🏆 Hackathon Info

Built for **UC Berkeley AI Hackathon 2025**  
Track: *Productivity & Dev Tools*  
Sponsors used: **Anthropic Claude 4**

---

## 📄 License

MIT — free to use, fork, and remix.

---

## 🤝 Contributing

PRs and ideas welcome — DM us or submit issues if you’d like to extend agents or plug in other APIs!
