
import streamlit as st
import json
import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.intent_agent import get_intent_from_prompt
from agents.huggingface_dataset_search_agent import HuggingFaceDatasetSearchAgent
from agents.smart_scraper_agent import SmartScraperAgent
from agents.data_cleaning_agent import DataCleaningAgent

st.set_page_config(page_title="Prompt2Data - From Prompt to Cleaned CSV")
st.title("Prompt2Data - From Prompt to Cleaned CSV")

if "step" not in st.session_state:
    st.session_state.step = 0
if "task_spec" not in st.session_state:
    st.session_state.task_spec = {}
if "final_csv" not in st.session_state:
    st.session_state.final_csv = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

user_input = st.chat_input("What dataset do you want to create?")
if user_input and st.session_state.step == 0:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    with st.chat_message("assistant"):
        st.markdown("🧠 Understanding your request...")
        response = get_intent_from_prompt(user_input, {})
        try:
            parsed = response if isinstance(response, dict) else json.loads(response)
            st.session_state.task_spec = parsed
            st.session_state.step = 1
            formatted = json.dumps(parsed, indent=2)
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Here's what I understood:```json{formatted}```"
            })
            st.rerun()
        except Exception as e:
            st.error("❌ Failed to parse your request.")
            st.code(str(response))
            st.stop()

# Step 1: Hugging Face search
if st.session_state.step == 1:
    with st.chat_message("assistant"):
        st.markdown("🔍 Searching Hugging Face for relevant datasets...")
        hf = HuggingFaceDatasetSearchAgent()
        path = hf.download_best_dataset_csv(st.session_state.task_spec)
        if path:
            st.session_state.final_csv = path
            st.session_state.step = 3
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "✅ Found a dataset on Hugging Face and downloaded preview CSV."
            })
            st.rerun()
        else:
            st.session_state.step = 2
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "⚠️ No good match on Hugging Face. Falling back to scraping..."
            })
            st.rerun()

# Step 2: Smart Scraper fallback
if st.session_state.step == 2:
    with st.chat_message("assistant"):
        st.markdown("🌐 Scraping public data sources or using AI fallback...")
        scraper = SmartScraperAgent()
        result = scraper.scrape_from_intent(st.session_state.task_spec)

        if result["csv_path"]:
            st.session_state.final_csv = result["csv_path"]
            st.session_state.step = 3
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"✅ Scraped/extracted data from: {result['source_url']}"
            })
            st.rerun()
        else:
            st.error("❌ Scraping failed. No data could be extracted.")
            st.stop()

# Step 3: Cleaning and output
if st.session_state.step == 3:
    with st.chat_message("assistant"):
        path = st.session_state.final_csv
        if not os.path.exists(path):
            st.error("📂 File not found.")
            st.stop()

        df = pd.read_csv(path)
        st.markdown("📄 Raw Data Preview:")
        st.dataframe(df.head())

        cleaner = DataCleaningAgent()
        cleaned = cleaner.clean_dataframe(df)
        cleaned_path = cleaner.save_cleaned_csv(cleaned, os.path.basename(path))

        st.markdown("✅ Cleaned Data Preview:")
        st.dataframe(cleaned.head())

        with open(cleaned_path, "rb") as f:
            st.download_button("⬇️ Download Cleaned CSV", f, file_name=os.path.basename(cleaned_path), mime="text/csv")
