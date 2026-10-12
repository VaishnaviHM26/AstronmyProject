"""
Data Ingestion Module.
Responsible for reading observation records, telescope profiles, and object datasets
from CSV files with schema validation and error reporting.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
from src.config import REQUIRED_OBS_COLUMNS


class DataLoader:
    """Handles ingestion of astronomical observation records and metadata."""

    def __init__(self):
        self.last_load_info: Dict[str, Any] = {}

    def load_observations(self, file_path: Path | str) -> pd.DataFrame:
        """
        Loads observation records from a CSV file and validates required columns.

        Args:
            file_path: Path to the observations CSV file.

        Returns:
            pd.DataFrame: Loaded raw observations DataFrame.

        Raises:
            FileNotFoundError: If the target file does not exist.
            ValueError: If the file is empty or missing required schema columns.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(
                f"[Ingestion Error] Observation dataset not found at: '{path}'. "
                f"Please ensure the file exists or run 'py data/generate_dataset.py'."
            )

        if path.suffix.lower() != ".csv":
            raise ValueError(f"[Ingestion Error] Expected a CSV file (.csv), but got: '{path.name}'")

        try:
            df = pd.read_csv(path, dtype=str)  # Load initially as string to inspect raw inputs
        except pd.errors.EmptyDataError:
            raise ValueError(f"[Ingestion Error] The file '{path.name}' is completely empty.")
        except Exception as exc:
            raise RuntimeError(f"[Ingestion Error] Failed reading '{path.name}': {exc}")

        if df.empty:
            raise ValueError(f"[Ingestion Error] The CSV file '{path.name}' contains zero rows of data.")

        # Check required columns
        missing_cols = [col for col in REQUIRED_OBS_COLUMNS if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"[Ingestion Error] Dataset '{path.name}' is missing required columns: {missing_cols}. "
                f"Required schema: {REQUIRED_OBS_COLUMNS}"
            )

        self.last_load_info = {
            "file_name": path.name,
            "file_path": str(path.resolve()),
            "total_records_ingested": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
        }

        return df

    def load_telescopes(self, file_path: Path | str) -> pd.DataFrame:
        """Loads telescope specifications registry."""
        path = Path(file_path)
        if not path.exists():
            return pd.DataFrame(columns=["telescope_id", "telescope_name", "telescope_type", "location", "aperture_m"])
        return pd.read_csv(path)

    def load_objects(self, file_path: Path | str) -> pd.DataFrame:
        """Loads cataloged celestial objects if available."""
        path = Path(file_path)
        if not path.exists():
            return pd.DataFrame(columns=["object_id", "observation_id", "object_type", "right_ascension", "declination", "apparent_magnitude"])
        return pd.read_csv(path)
