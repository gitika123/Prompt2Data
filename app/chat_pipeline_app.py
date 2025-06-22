
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
if "hf_results" not in st.session_state:
    st.session_state.hf_results = []

for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

user_input = st.chat_input("Describe the dataset you want:")
if user_input and st.session_state.step == 0:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    with st.chat_message("assistant"):
        st.markdown("🧠 Let me understand what data you need...")
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

# Step 1: Hugging Face Dataset Agent
if st.session_state.step == 1:
    with st.chat_message("assistant"):
        st.markdown("🔍 Searching Hugging Face for relevant datasets...")
        hf = HuggingFaceDatasetSearchAgent()
        results = hf.search_datasets(st.session_state.task_spec)
        st.session_state.hf_results = results

        if results:
            for ds in results:
                st.markdown(
                    f"**{ds.id}** — [View Dataset]({ds.url})  "
                    f"{ds.description if ds.description else 'No description available.'}"
                )
            preview_path = hf.download_first_preview_csv(st.session_state.task_spec)
            if preview_path:
                st.session_state.final_csv = preview_path
                st.session_state.step = 3
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": "✅ Found and downloaded a dataset preview from Hugging Face."
                })
                st.rerun()
            else:
                st.warning("⚠️ Could not load a usable preview. Showing results but proceeding to scraping.")
                st.session_state.step = 2
                st.rerun()
        else:
            st.warning("❌ No datasets found. Proceeding to scraping.")
            st.session_state.step = 2
            st.rerun()

# Step 2: Smart Web Scraper fallback
if st.session_state.step == 2:
    with st.chat_message("assistant"):
        st.markdown("🌐 Scraping public sources for tabular data...")
        scraper = SmartScraperAgent()
        result = scraper.scrape_from_intent(st.session_state.task_spec)

        if result["csv_path"]:
            st.session_state.final_csv = result["csv_path"]
            st.session_state.step = 3
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": "✅ Scraped structured data from the web and saved to CSV. Cleaning next..."
            })
            st.rerun()
        else:
            st.error("❌ No structured data found via scraping.")
            st.stop()

# Step 3: Data Cleaning Agent
if st.session_state.step == 3:
    with st.chat_message("assistant"):
        path = st.session_state.final_csv
        if not os.path.exists(path):
            st.error("Final CSV not found.")
            st.stop()

        df = pd.read_csv(path)
        st.markdown("📄 Raw Scraped Data Preview:")
        st.dataframe(df.head())

        cleaner = DataCleaningAgent()
        cleaned = cleaner.clean_dataframe(df)
        cleaned_path = cleaner.save_cleaned_csv(cleaned, os.path.basename(path))

        st.markdown("✅ Cleaned Data Preview:")
        st.dataframe(cleaned.head())

        with open(cleaned_path, "rb") as f:
            st.download_button("⬇️ Download Cleaned CSV", f, file_name=os.path.basename(cleaned_path), mime="text/csv")
