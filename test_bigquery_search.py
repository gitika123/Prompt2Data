import os
from agents.bigquery_dataset_search_agent import BigQueryDatasetSearchAgent

# Optional: load from .env if you’re using dotenv
from dotenv import load_dotenv
load_dotenv()

# Make sure your service account path is set correctly
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Create the agent
agent = BigQueryDatasetSearchAgent()

# Define a sample task spec from your Intent Agent
task_spec = {
    "goal": "Analyze school performance",
    "data_requirements": [
        "test scores", "school funding", "student demographics"
    ],
    "location": "United States",
    "timeframe": "last 5 years",
    "preferred_format": "tabular",
    "output_type": "analysis"
}

# Run the search
print("🔍 Searching public BigQuery datasets...")
results = agent.search_datasets(task_spec)

# Display results
if results:
    print(f"\n✅ Found {len(results)} relevant tables:")
    for r in results:
        print(f"- {r['full_path']} (keyword: {r['keyword']})")
else:
    print("❌ No relevant datasets found.")
