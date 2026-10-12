"""
Astronomical Calibration Module.

TRANSPARENCY NOTE:
This module implements an illustrative, educational mathematical model of standard
astronomical data calibration stages (bias offset compensation, thermal dark current
adjustment, and optical flat-field filter response) applied to tabular observation data.
It does NOT claim raw hardware CCD FITS pixel reduction or real-time telescope calibration.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from src.config import FILTER_TRANSMISSION


class Calibrator:
    """Applies educational illustrative calibration corrections to observation records."""

    # Illustrative instrument calibration constants
    ELECTRONIC_BIAS_OFFSET = 0.05       # Baseline electronic read noise offset (magnitude equivalent)
    DARK_CURRENT_RATE_PER_SEC = 0.00008 # Thermal noise accumulation rate per second of exposure

    def __init__(self):
        self.calibration_summary: Dict[str, Any] = {}

    def calibrate(self, df_valid: pd.DataFrame) -> pd.DataFrame:
        """
        Applies bias, dark current, and flat-field filter corrections to valid records.

        Calibration Model (Illustrative):
        - Bias correction: Adjusts for detector baseline electronic offset.
        - Dark correction: Offsets thermal signal accumulation proportional to exposure time.
        - Flat-field correction: Normalizes brightness based on photometric filter optical throughput.

        Args:
            df_valid: Validated observations DataFrame.

        Returns:
            pd.DataFrame: Calibrated observations DataFrame.
        """
        df = df_valid.copy()
        if df.empty:
            return df

        # 1. Bias correction offset
        df['bias_correction_offset'] = self.ELECTRONIC_BIAS_OFFSET

        # 2. Dark current correction (dependent on exposure duration)
        exposure_s = df['exposure_time'].fillna(60.0)
        df['dark_correction_offset'] = exposure_s * self.DARK_CURRENT_RATE_PER_SEC

        # 3. Flat-field filter transmission normalization
        # Each optical filter has a characteristic relative transmission factor
        filter_factors = df['filter'].map(lambda f: FILTER_TRANSMISSION.get(str(f).strip(), 1.0))
        df['flat_field_factor'] = filter_factors

        # 4. Compute Calibrated Brightness
        # Calibrated magnitude accounts for electronic bias, dark accumulation, and throughput
        raw_mag = df['brightness'].fillna(15.0)
        # Small standard adjustment reflecting throughput and detector offsets
        throughput_delta = 2.5 * np.log10(filter_factors)
        df['calibrated_brightness'] = np.round(
            raw_mag - df['bias_correction_offset'] - df['dark_correction_offset'] + throughput_delta,
            3
        )

        # 5. Compute Calibrated SNR (calibrated signal quality metric)
        if 'snr' in df.columns:
            df['calibrated_snr'] = np.round(df['snr'] * np.sqrt(filter_factors), 2)
        else:
            df['calibrated_snr'] = 25.0

        df['calibration_status'] = 'Calibrated (Illustrative Model)'

        self.calibration_summary = {
            "records_calibrated": len(df),
            "mean_raw_brightness": round(float(df['brightness'].mean()), 2),
            "mean_calibrated_brightness": round(float(df['calibrated_brightness'].mean()), 2),
            "filters_calibrated": df['filter'].unique().tolist(),
            "model_type": "Illustrative Tabular Calibration (Educational)"
        }

        return df
