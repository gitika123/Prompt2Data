
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import pandas as pd
from urllib.parse import urljoin
import os
import re
from typing import List, Dict

class SmartScraperAgent:
    def __init__(self, output_dir="outputs", min_score=3):
        self.headers = {"User-Agent": "Mozilla/5.0"}
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        self.min_score = min_score

    def search_site(self, query: str, max_results=10) -> List[str]:
        with DDGS() as ddgs:
            return [res["href"] for res in ddgs.text(query, max_results=max_results) if res.get("href", "").startswith("http")]

    def extract_tables(self, soup) -> List[pd.DataFrame]:
        tables = soup.find_all("table")
        dataframes = []
        for table in tables:
            rows = table.find_all("tr")
            content = [[cell.get_text(strip=True) for cell in row.find_all(["th", "td"])] for row in rows]
            if len(content) > 1 and len(content[0]) > 1:
                try:
                    df = pd.DataFrame(content[1:], columns=content[0])
                    if df.shape[1] >= 2 and df.shape[0] >= 3:
                        dataframes.append(df)
                except:
                    continue
        return dataframes

    def extract_csv_links(self, soup, base_url: str) -> List[str]:
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if ".csv" in href.lower() or ".json" in href.lower() or ".xlsx" in href.lower():
                full_url = urljoin(base_url, href)
                links.append(full_url)
        return links

    def save_single_csv(self, df: pd.DataFrame, task_name: str) -> str:
        filename = re.sub(r"[^a-zA-Z0-9]", "_", task_name.lower()) + "_final.csv"
        path = os.path.join(self.output_dir, filename)
        df.to_csv(path, index=False)
        return path

    def merge_or_select_table(self, tables: List[pd.DataFrame], query: str) -> pd.DataFrame:
        if len(tables) == 1:
            return tables[0]

        base_cols = set(tables[0].columns)
        all_same = all(set(df.columns) == base_cols for df in tables)

        if all_same:
            return pd.concat(tables, ignore_index=True)

        def score(df):
            score = len(df.columns) * len(df)
            headers = " ".join(df.columns).lower()
            if any(kw in headers for kw in query.lower().split()):
                score += 50
            return score

        best_df = max(tables, key=score)
        return best_df

    def scrape_from_intent(self, task_spec, max_pages=10) -> Dict[str, object]:
        query = task_spec.get("goal", "public data")
        results = self.search_site(query, max_results=max_pages)

        for url in results:
            try:
                res = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(res.text, "html.parser")

                tables = self.extract_tables(soup)
                csv_links = self.extract_csv_links(soup, url)

                score = len(tables) * 3 + len(csv_links) * 2
                if score >= self.min_score and tables:
                    merged_table = self.merge_or_select_table(tables, query)
                    csv_path = self.save_single_csv(merged_table, query)

                    return {
                        "source_url": url,
                        "table": merged_table,
                        "csv_path": csv_path,
                        "csv_links": csv_links
                    }

            except Exception as e:
                print(f"❌ Failed to scrape {url}: {e}")
                continue

        return {
            "source_url": "",
            "table": None,
            "csv_path": "",
            "csv_links": []
        }
