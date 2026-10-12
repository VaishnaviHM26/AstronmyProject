"""
Feature Extraction and Scientific Analysis Module.
Extracts and summarizes:
- Astronomical object classifications (Stars, Galaxies, Planets, Other celestial objects)
- Brightness and angular size statistics per object type
- Telescope utilization metrics
- Observation filter distributions
- Monthly observing trends (M1 to M12)
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np


class FeatureExtractor:
    """Extracts scientific features and statistical summaries from astronomical catalogs."""

    def __init__(self):
        self.summary: Dict[str, Any] = {}

    def analyze_catalog(
        self,
        df_valid_obs: pd.DataFrame,
        df_objects: pd.DataFrame,
        df_telescopes: pd.DataFrame = None
    ) -> Dict[str, Any]:
        """
        Analyzes observations and cataloged objects to generate scientific summaries.

        Args:
            df_valid_obs: Validated observations DataFrame.
            df_objects: Cataloged celestial objects DataFrame.
            df_telescopes: Optional telescope registry DataFrame.

        Returns:
            Dict[str, Any]: Comprehensive analysis dictionary.
        """
        # 1. Object Type Distribution (Table 6.3 in Report)
        total_objects = len(df_objects)
        object_summary = {}

        if not df_objects.empty and 'object_type' in df_objects.columns:
            counts = df_objects['object_type'].value_counts()
            for obj_type in ['Star', 'Galaxy', 'Planet', 'Other']:
                count = int(counts.get(obj_type, 0))
                pct = round((count / total_objects) * 100, 2) if total_objects > 0 else 0.0

                # Brightness stats for this object type
                sub_df = df_objects[df_objects['object_type'] == obj_type]
                mag_series = pd.to_numeric(sub_df.get('apparent_magnitude', sub_df.get('brightness')), errors='coerce')
                size_series = pd.to_numeric(sub_df.get('estimated_size_arcsec'), errors='coerce')

                object_summary[obj_type] = {
                    "count": count,
                    "percentage": pct,
                    "brightness_mean": round(float(mag_series.mean()), 2) if not mag_series.isna().all() else None,
                    "brightness_min": round(float(mag_series.min()), 2) if not mag_series.isna().all() else None,
                    "brightness_max": round(float(mag_series.max()), 2) if not mag_series.isna().all() else None,
                    "size_arcsec_mean": round(float(size_series.mean()), 2) if not size_series.isna().all() else None,
                }
        else:
            # Fallback to observations primary_object_type if objects table is empty
            counts = df_valid_obs['primary_object_type'].value_counts()
            total_obs = len(df_valid_obs)
            for obj_type, count in counts.items():
                object_summary[obj_type] = {
                    "count": int(count),
                    "percentage": round((count / total_obs) * 100, 2),
                    "brightness_mean": round(float(df_valid_obs[df_valid_obs['primary_object_type'] == obj_type]['brightness'].mean()), 2)
                }

        # 2. Telescope Utilization
        tel_summary = {}
        if 'telescope_id' in df_valid_obs.columns:
            tel_counts = df_valid_obs['telescope_id'].value_counts()
            for tel_id, count in tel_counts.items():
                sub = df_valid_obs[df_valid_obs['telescope_id'] == tel_id]
                tel_summary[tel_id] = {
                    "observation_count": int(count),
                    "percentage": round((count / len(df_valid_obs)) * 100, 2),
                    "mean_exposure_sec": round(float(sub['exposure_time'].mean()), 1)
                }

        # Merge with telescope names if registry provided
        if df_telescopes is not None and not df_telescopes.empty:
            for _, row in df_telescopes.iterrows():
                t_id = row['telescope_id']
                if t_id in tel_summary:
                    tel_summary[t_id]['telescope_name'] = row.get('telescope_name', t_id)
                    tel_summary[t_id]['telescope_type'] = row.get('telescope_type', 'Optical')
                    tel_summary[t_id]['aperture_m'] = row.get('aperture_m', 'N/A')

        # 3. Monthly Observation Trends (12 months)
        monthly_trends = {}
        if 'month' in df_valid_obs.columns:
            for m in range(1, 13):
                m_count = int((df_valid_obs['month'] == m).sum())
                month_name = pd.to_datetime(f"2025-{m:02d}-01").strftime("%B")
                monthly_trends[f"M{m}"] = {
                    "month_number": m,
                    "month_name": month_name,
                    "observations": m_count
                }

        # 4. Photometric Filter Distribution
        filter_summary = {}
        if 'filter' in df_valid_obs.columns:
            f_counts = df_valid_obs['filter'].value_counts()
            for filt, cnt in f_counts.items():
                filter_summary[str(filt)] = {
                    "count": int(cnt),
                    "percentage": round((cnt / len(df_valid_obs)) * 100, 2)
                }

        # 5. Brightness Overall Statistics
        brightness_col = 'calibrated_brightness' if 'calibrated_brightness' in df_valid_obs.columns else 'brightness'
        b_series = pd.to_numeric(df_valid_obs[brightness_col], errors='coerce').dropna()
        brightness_stats = {
            "mean": round(float(b_series.mean()), 2) if not b_series.empty else 0.0,
            "median": round(float(b_series.median()), 2) if not b_series.empty else 0.0,
            "std": round(float(b_series.std()), 2) if not b_series.empty else 0.0,
            "min": round(float(b_series.min()), 2) if not b_series.empty else 0.0,
            "max": round(float(b_series.max()), 2) if not b_series.empty else 0.0
        }

        self.summary = {
            "total_objects_cataloged": total_objects,
            "object_distribution": object_summary,
            "telescope_utilization": tel_summary,
            "monthly_trends": monthly_trends,
            "filter_distribution": filter_summary,
            "brightness_statistics": brightness_stats
        }

        return self.summary
