
from datasets import load_dataset
from huggingface_hub import list_datasets
import pandas as pd
import os

class DatasetResult:
    def __init__(self, id, url, description=""):
        self.id = id
        self.url = f"https://huggingface.co/datasets/{id}"
        self.description = description

class HuggingFaceDatasetSearchAgent:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def search_datasets(self, task_spec, limit=5):
        query = task_spec.get("goal", "")
        try:
            results = list_datasets(search=query, limit=limit)
            return [DatasetResult(r.id, r.cardData.get("description", "") if r.cardData else "") for r in results]
        except Exception as e:
            print(f"❌ Dataset search failed: {e}")
            return []

    def download_first_preview_csv(self, task_spec) -> str:
        datasets = self.search_datasets(task_spec)
        if not datasets:
            return None

        for result in datasets:
            try:
                dataset = load_dataset(result.id, split="train")
                df = dataset.to_pandas()
                if df.shape[0] > 0:
                    preview_df = df.head(100)
                    file_name = f"{result.id.replace('/', '_')}_preview.csv"
                    csv_path = os.path.join(self.output_dir, file_name)
                    preview_df.to_csv(csv_path, index=False)
                    return csv_path
            except Exception as e:
                print(f"⚠️ Skipping {result.id} — Load failed: {e}")
                continue

        return None
