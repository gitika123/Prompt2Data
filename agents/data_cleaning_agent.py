
import pandas as pd
import os

class DataCleaningAgent:
    def __init__(self, output_dir="outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def clean_dataframe(self, df):
        df = df.copy()
        if df.columns.duplicated().any():
            df.columns = pd.io.parsers.ParserBase({'names': df.columns})._maybe_dedup_names(df.columns)

        # Drop fully empty cols/rows
        df.dropna(axis=0, how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)

        # Trim whitespace and standardize column names
        df.columns = [str(col).strip().replace("\n", " ").replace("\r", "") for col in df.columns]

        # Try to convert any parsable string numeric columns
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='ignore')
            except:
                continue

        return df

    def save_cleaned_csv(self, df, original_name):
        name = os.path.splitext(original_name)[0]
        path = os.path.join(self.output_dir, f"{name}_cleaned.csv")
        df.to_csv(path, index=False)
        return path
