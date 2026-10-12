"""
Data Preprocessing Module.
Handles cleaning of astronomical observation records:
- Trimming strings and normalizing whitespace
- Converting columns to strict numerical and datetime types
- Identifying and handling duplicate observation records
- Tracking missing values across essential observation fields
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


class Preprocessor:
    """Preprocesses raw observation records to clean duplicates, missing values, and types."""

    def __init__(self):
        self.stats: Dict[str, Any] = {}

    def preprocess(self, df_raw: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Cleans and parses raw observation records.

        Args:
            df_raw: Raw DataFrame loaded by DataLoader.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]:
                - df_cleaned: DataFrame with trimmed values, converted numeric types, and duplicate rows marked/removed.
                - df_duplicates: DataFrame containing identified duplicate records.
        """
        df = df_raw.copy()

        # Step 1: Strip leading/trailing whitespaces from string columns
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip()
                # Convert empty strings and 'nan' strings to actual NaN
                df[col] = df[col].replace({'': np.nan, 'nan': np.nan, 'None': np.nan, 'NULL': np.nan})

        # Step 2: Identify Duplicate Records
        # A duplicate can be an identical row or a record with identical telescope, date, time, and coordinates
        key_subset = [
            col for col in ['telescope_id', 'observation_date', 'observation_time', 'right_ascension', 'declination']
            if col in df.columns
        ]

        if key_subset:
            duplicate_mask = df.duplicated(subset=key_subset, keep='first')
        else:
            duplicate_mask = df.duplicated(keep='first')

        df_duplicates = df[duplicate_mask].copy()
        if not df_duplicates.empty:
            df_duplicates['rejection_reason'] = 'Duplicate observation record (identical telescope, timestamp, and coordinates)'
            df_duplicates['quality_status'] = 'Rejected'

        # Retain unique records for further processing
        df_unique = df[~duplicate_mask].copy()

        # Step 3: Type Conversions
        numeric_columns = ['right_ascension', 'declination', 'exposure_time', 'brightness', 'snr', 'airmass']
        for col in numeric_columns:
            if col in df_unique.columns:
                df_unique[col] = pd.to_numeric(df_unique[col], errors='coerce')

        if 'observation_date' in df_unique.columns:
            df_unique['observation_date'] = pd.to_datetime(df_unique['observation_date'], errors='coerce')
            df_unique['month'] = df_unique['observation_date'].dt.month
            df_unique['year'] = df_unique['observation_date'].dt.year

        # Normalize primary_object_type
        if 'primary_object_type' in df_unique.columns:
            df_unique['primary_object_type'] = df_unique['primary_object_type'].fillna('Other')
            df_unique['primary_object_type'] = df_unique['primary_object_type'].astype(str).str.title()

        # Summary statistics
        self.stats = {
            "initial_rows": len(df_raw),
            "duplicate_records_found": len(df_duplicates),
            "unique_records_retained": len(df_unique),
            "missing_values_by_column": df_unique.isna().sum().to_dict()
        }

        return df_unique, df_duplicates
