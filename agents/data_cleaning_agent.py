
import pandas as pd
import numpy as np
import os
import re

class DataCleaningAgent:
    def __init__(self):
        pass

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # 1. Strip whitespace from column names
        df.columns = df.columns.str.strip()

        # 2. Drop completely empty rows/columns
        df.dropna(how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)

        # 3. Standardize column names
        df.columns = [re.sub(r"[^a-zA-Z0-9_]", "_", col.strip().lower()) for col in df.columns]

        # 4. Trim strings and remove special characters
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace(r"[\r\n\t]+", " ", regex=True)
            df[col] = df[col].str.replace(r"\s{2,}", " ", regex=True)

        # 5. Try converting numeric columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col].str.replace(",", ""), errors='ignore')
                except:
                    continue

        # 6. Remove duplicate rows
        df.drop_duplicates(inplace=True)

        return df

    def save_cleaned_csv(self, df: pd.DataFrame, original_filename: str) -> str:
        cleaned_name = original_filename.replace(".csv", "_cleaned.csv")
        output_path = os.path.join("outputs", cleaned_name)
        df.to_csv(output_path, index=False)
        return output_path

# Example usage
if __name__ == "__main__":
    agent = DataCleaningAgent()
    test_path = "outputs/sample.csv"
    if os.path.exists(test_path):
        df = pd.read_csv(test_path)
        cleaned_df = agent.clean_dataframe(df)
        cleaned_path = agent.save_cleaned_csv(cleaned_df, "sample.csv")
        print(f"✅ Cleaned dataset saved to: {cleaned_path}")
