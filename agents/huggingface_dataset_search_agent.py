
from datasets import load_dataset
from huggingface_hub import list_datasets
import pandas as pd
import os
from rapidfuzz import fuzz

class DatasetResult:
    def __init__(self, id, url, description="", score=0):
        self.id = id
        self.url = f"https://huggingface.co/datasets/{id}"
        self.description = description
        self.score = score

class HuggingFaceDatasetSearchAgent:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def search_datasets(self, task_spec, limit=10):
        query = task_spec.get("goal", "")
        try:
            results = list_datasets(search=query, limit=limit)
            query_keywords = query.lower().split()

            dataset_results = []
            for r in results:
                desc = r.cardData.get("description", "") if r.cardData else ""
                full_text = (r.id + " " + desc).lower()
                match_score = max([fuzz.partial_ratio(word, full_text) for word in query_keywords]) if query_keywords else 0
                dataset_results.append(DatasetResult(r.id, f"https://huggingface.co/datasets/{r.id}", desc, score=match_score))

            return sorted(dataset_results, key=lambda x: x.score, reverse=True)
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []

    def download_best_dataset_csv(self, task_spec) -> str:
        datasets = self.search_datasets(task_spec)
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
                print(f"⚠️ Failed loading {result.id} — {e}")
        return None
