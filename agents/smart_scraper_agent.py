
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from urllib.parse import urlparse
from io import StringIO

class SmartScraperAgent:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def search_relevant_urls(self, query, max_results=5):
        urls = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    if r["href"].startswith("http"):
                        urls.append(r["href"])
        except Exception as e:
            print(f"❌ DuckDuckGo failed: {e}")
        return urls

    def extract_tables_and_lists(self, html):
        soup = BeautifulSoup(html, "html.parser")
        # Try HTML tables
        try:
            tables = pd.read_html(html)
            for table in tables:
                if not table.empty:
                    return table, "table"
        except:
            pass
        # Try structured list
        items = soup.find_all("li")
        rows = [li.get_text(strip=True) for li in items if len(li.get_text(strip=True).split()) > 3]
        if rows:
            return pd.DataFrame(rows, columns=["Extracted Info"]), "list"
        return None, None

    def extract_with_llm_fallback(self, html, query):
        from openai import OpenAI
        import os
        from dotenv import load_dotenv
        load_dotenv()
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            return None
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        try:
            soup = BeautifulSoup(html, "html.parser")
            raw_text = soup.get_text(separator="\n")[:3500]
            prompt = f"Extract structured tabular data related to: '{query}' from the following webpage content. Respond only in CSV format.\n\n{raw_text}"
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            csv_raw = response.choices[0].message.content
            df = pd.read_csv(StringIO(csv_raw))
            return df
        except Exception as e:
            print(f"❌ LLM fallback failed: {e}")
        return None

    def scrape_from_intent(self, task_spec):
        query = task_spec.get("goal", "")
        urls = self.search_relevant_urls(query, max_results=7)
        for url in urls:
            try:
                res = requests.get(url, timeout=10)
                html = res.text
                df, mode = self.extract_tables_and_lists(html)
                if df is not None:
                    fname = f"{urlparse(url).netloc.replace('.', '_')}_{mode}.csv"
                    fpath = os.path.join(self.output_dir, fname)
                    df.to_csv(fpath, index=False)
                    return {
                        "source_url": url,
                        "source_type": mode,
                        "table": df,
                        "csv_path": fpath
                    }
                # Try LLM fallback
                df_llm = self.extract_with_llm_fallback(html, query)
                if df_llm is not None and not df_llm.empty:
                    fname = f"{urlparse(url).netloc.replace('.', '_')}_llm.csv"
                    fpath = os.path.join(self.output_dir, fname)
                    df_llm.to_csv(fpath, index=False)
                    return {
                        "source_url": url,
                        "source_type": "llm",
                        "table": df_llm,
                        "csv_path": fpath
                    }
            except Exception as e:
                print(f"⚠️ Failed to scrape {url}: {e}")
                continue
        return {"source_url": None, "source_type": None, "csv_path": None, "table": None}
