
"""
Clean and standardize RavenStack datasets.
Original files in data/raw are never modified.
Cleaned intermediate files are saved in data/interim.
"""

import pandas as pd

from config import INTERIM, TABLES
from load_data import load_all


def clean_table(df):
    """
    Apply safe, non-destructive cleaning:
    - Remove unnecessary spaces from text values.
    - Convert empty text values into missing values.
    - Preserve all rows.
    """

    cleaned = df.copy()

    whitespace_changes = 0

    # Standardize text columns
    text_columns = cleaned.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:

        original = cleaned[column].copy()

        cleaned[column] = cleaned[column].map(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

        whitespace_changes += (
            original.ne(cleaned[column])
            & original.notna()
        ).sum()

        # Convert empty strings into missing values
        cleaned[column] = cleaned[column].replace(
            "", pd.NA
        )

    return cleaned, int(whitespace_changes)


def main():

    # Load original datasets
    datasets = load_all()

    # Create interim folder if it does not exist
    INTERIM.mkdir(parents=True, exist_ok=True)

    cleaning_results = []

    for name, df in datasets.items():

        print(f"\nCleaning table: {name}")

        original_rows = len(df)
        original_nulls = int(df.isna().sum().sum())

        # Clean the dataset
        cleaned, whitespace_changes = clean_table(df)

        cleaned_rows = len(cleaned)
        cleaned_nulls = int(cleaned.isna().sum().sum())

        # Save cleaned dataset
        output_file = INTERIM / f"{name}_cleaned.csv"

        cleaned.to_csv(output_file, index=False)

        # Record cleaning summary
        cleaning_results.append({
            "table": name,
            "original_rows": original_rows,
            "cleaned_rows": cleaned_rows,
            "original_nulls": original_nulls,
            "cleaned_nulls": cleaned_nulls,
            "whitespace_changes": whitespace_changes,
            "rows_removed": original_rows - cleaned_rows,
            "output_file": str(output_file.name)
        })

        print(f"Original rows: {original_rows}")
        print(f"Cleaned rows: {cleaned_rows}")
        print(f"Whitespace changes: {whitespace_changes}")
        print(f"Saved to: {output_file}")

    # Save cleaning report
    report = pd.DataFrame(cleaning_results)

    report.to_csv(
        INTERIM / "cleaning_report.csv",
        index=False
    )

    print("\n================================")
    print("DATA CLEANING COMPLETED")
    print("================================")
    print(report.to_string(index=False))


if __name__ == "__main__":
    main()
