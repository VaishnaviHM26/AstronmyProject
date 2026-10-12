"""
Quality Control and Validation Module.
Validates celestial coordinates (RA/Dec), exposure duration, brightness magnitude,
and observation completeness, classifying records into:
- Good (High SNR, complete data, accurate parameters)
- Acceptable (Medium SNR, valid parameters suitable for cataloging)
- Rejected (Invalid coordinates, non-positive exposure, missing metadata, corrupt readings)
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np
from src.config import (
    RA_MIN_DEG, RA_MAX_DEG, DEC_MIN_DEG, DEC_MAX_DEG,
    EXPOSURE_MIN_SEC, EXPOSURE_MAX_SEC, MAG_MIN, MAG_MAX,
    GOOD_SNR_THRESHOLD, ACCEPTABLE_SNR_THRESHOLD
)


class DataValidator:
    """Validates astronomical parameters and assigns quality control status."""

    def __init__(self):
        self.validation_summary: Dict[str, Any] = {}

    def validate_and_flag(
        self,
        df_unique: pd.DataFrame,
        df_duplicates: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Validates unique records, flags quality issues, and combines with duplicate rejections.

        Args:
            df_unique: Cleaned unique DataFrame from Preprocessor.
            df_duplicates: Duplicate records identified during preprocessing.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
                - df_all_flagged: Combined dataset with quality_status and rejection_reason columns.
                - df_valid: Valid records (Good and Acceptable, total 950 records).
                - df_rejected: Rejected records (total 50 records).
        """
        df = df_unique.copy()

        # Initialize status and reasons
        df['quality_status'] = 'Good'
        df['rejection_reason'] = ''

        # Vectorized check for each failure criterion
        rejection_reasons = []

        for idx, row in df.iterrows():
            reasons = []

            # 1. Coordinate Validation: Right Ascension
            ra = row.get('right_ascension')
            if pd.isna(ra):
                reasons.append("Missing Right Ascension coordinate")
            elif not (RA_MIN_DEG <= ra < RA_MAX_DEG):
                reasons.append(f"Invalid Right Ascension ({ra:.2f}°): must be in [{RA_MIN_DEG}°, {RA_MAX_DEG}°)")

            # Coordinate Validation: Declination
            dec = row.get('declination')
            if pd.isna(dec):
                reasons.append("Missing Declination coordinate")
            elif not (DEC_MIN_DEG <= dec <= DEC_MAX_DEG):
                reasons.append(f"Invalid Declination ({dec:.2f}°): must be in [{DEC_MIN_DEG}°, {DEC_MAX_DEG}°]")

            # 2. Exposure Time Validation
            exp_time = row.get('exposure_time')
            if pd.isna(exp_time):
                reasons.append("Missing exposure time")
            elif exp_time <= 0:
                reasons.append(f"Non-positive exposure time ({exp_time} s): must be > 0 s")
            elif exp_time > EXPOSURE_MAX_SEC:
                reasons.append(f"Excessive exposure time ({exp_time} s): exceeds limit of {EXPOSURE_MAX_SEC} s")

            # 3. Brightness / Magnitude Validation
            mag = row.get('brightness')
            if pd.isna(mag):
                reasons.append("Missing or non-numeric brightness measurement")
            elif not (MAG_MIN <= mag <= MAG_MAX):
                reasons.append(f"Out-of-range magnitude ({mag}): must be between {MAG_MIN} and {MAG_MAX}")

            # 4. Essential Metadata Validation
            if pd.isna(row.get('telescope_id')) or str(row.get('telescope_id')).strip() == '':
                reasons.append("Missing telescope identifier")
            if pd.isna(row.get('filter')) or str(row.get('filter')).strip() == '':
                reasons.append("Missing photometric filter designation")
            if pd.isna(row.get('observation_date')):
                reasons.append("Missing or unparseable observation date")

            # 5. Signal Quality Check
            snr = row.get('snr')
            if pd.notna(snr) and snr < ACCEPTABLE_SNR_THRESHOLD:
                reasons.append(f"Signal-to-noise ratio too low ({snr:.1f} < {ACCEPTABLE_SNR_THRESHOLD})")

            # Determine quality status
            if reasons:
                status = 'Rejected'
                reason_str = "; ".join(reasons)
            else:
                # Differentiate between Good and Acceptable
                if pd.notna(snr) and snr >= GOOD_SNR_THRESHOLD:
                    status = 'Good'
                else:
                    status = 'Acceptable'
                reason_str = 'Passed quality control checks'

            df.at[idx, 'quality_status'] = status
            df.at[idx, 'rejection_reason'] = reason_str

        # Separate valid and rejected records from unique pool
        df_valid = df[df['quality_status'].isin(['Good', 'Acceptable'])].copy()
        df_rejected_unique = df[df['quality_status'] == 'Rejected'].copy()

        # Combine with duplicate records
        df_rejected = pd.concat([df_rejected_unique, df_duplicates], ignore_index=True)
        df_all_flagged = pd.concat([df_valid, df_rejected], ignore_index=True)

        # Quality distribution summary
        total_records = len(df_all_flagged)
        good_count = len(df_all_flagged[df_all_flagged['quality_status'] == 'Good'])
        acceptable_count = len(df_all_flagged[df_all_flagged['quality_status'] == 'Acceptable'])
        rejected_count = len(df_all_flagged[df_all_flagged['quality_status'] == 'Rejected'])

        self.validation_summary = {
            "total_records": total_records,
            "valid_records": len(df_valid),
            "rejected_records": len(df_rejected),
            "good_count": good_count,
            "good_percentage": round((good_count / total_records) * 100, 2) if total_records else 0,
            "acceptable_count": acceptable_count,
            "acceptable_percentage": round((acceptable_count / total_records) * 100, 2) if total_records else 0,
            "rejected_count": rejected_count,
            "rejected_percentage": round((rejected_count / total_records) * 100, 2) if total_records else 0,
            "rejection_breakdown": df_rejected['rejection_reason'].value_counts().to_dict()
        }

        return df_all_flagged, df_valid, df_rejected
