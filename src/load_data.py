"""Load raw CSVs into pandas DataFrames with parsed dates. Raw files are never modified."""
import pandas as pd
from config import RAW, TABLES


def load_table(name: str) -> pd.DataFrame:
    spec = TABLES[name]
    return pd.read_csv(RAW / spec["file"], parse_dates=spec["dates"])


def load_all() -> dict:
    return {name: load_table(name) for name in TABLES}


if __name__ == "__main__":
    for name, df in load_all().items():
        print(f"{name:16s} rows={len(df):6d} cols={df.shape[1]}")
