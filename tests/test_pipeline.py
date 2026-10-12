"""
Automated Unit and Pipeline Test Suite.
Verifies all modules of the Astronomy Telescope Cataloging project:
- DataLoader
- Preprocessor
- DataValidator
- Calibrator
- FeatureExtractor
- Visualizer
- DataExporter
- HTMLDashboardGenerator
"""

import unittest
from pathlib import Path
import pandas as pd
import numpy as np

from src.config import (
    DEFAULT_OBSERVATIONS_FILE, DEFAULT_TELESCOPES_FILE, DEFAULT_OBJECTS_FILE,
    OUTPUTS_DIR, CHARTS_DIR
)
from src.data_loader import DataLoader
from src.preprocessor import Preprocessor
from src.validator import DataValidator
from src.calibrator import Calibrator
from src.feature_extractor import FeatureExtractor
from src.visualizer import Visualizer
from src.exporter import DataExporter
from src.html_dashboard import HTMLDashboardGenerator


class TestAstronomyPipeline(unittest.TestCase):
    """Test suite covering data ingestion, cleaning, validation, calibration, and analytics."""

    @classmethod
    def setUpClass(cls):
        cls.loader = DataLoader()
        cls.df_raw = cls.loader.load_observations(DEFAULT_OBSERVATIONS_FILE)
        cls.df_telescopes = cls.loader.load_telescopes(DEFAULT_TELESCOPES_FILE)
        cls.df_objects = cls.loader.load_objects(DEFAULT_OBJECTS_FILE)

    def test_01_data_ingestion(self):
        """Test dataset loading and column schema."""
        self.assertEqual(len(self.df_raw), 1000, "Expected exactly 1,000 raw observation records")
        self.assertEqual(len(self.df_telescopes), 5, "Expected 5 telescope registries")
        self.assertEqual(len(self.df_objects), 2845, "Expected 2,845 cataloged objects")

        required_cols = ['observation_id', 'telescope_id', 'observation_date', 'right_ascension', 'declination', 'exposure_time', 'filter', 'brightness']
        for col in required_cols:
            self.assertIn(col, self.df_raw.columns)

    def test_02_preprocessing(self):
        """Test whitespace stripping and duplicate identification."""
        pre = Preprocessor()
        df_unique, df_dups = pre.preprocess(self.df_raw)

        self.assertEqual(len(df_dups), 10, "Expected exactly 10 duplicate records identified")
        self.assertEqual(len(df_unique), 990, "Expected 990 unique records retained")
        self.assertIn('month', df_unique.columns, "Preprocessor should extract observation month")

    def test_03_quality_control_validation(self):
        """Test coordinate, exposure, brightness validation and status flagging."""
        pre = Preprocessor()
        df_unique, df_dups = pre.preprocess(self.df_raw)

        val = DataValidator()
        df_all, df_valid, df_rejected = val.validate_and_flag(df_unique, df_dups)
        summary = val.validation_summary

        self.assertEqual(len(df_valid), 950, "Expected exactly 950 valid records (Table 6.1)")
        self.assertEqual(len(df_rejected), 50, "Expected exactly 50 rejected records (Table 6.1)")
        self.assertEqual(summary['good_count'], 720, "Expected 720 Good quality records (Table 6.2)")
        self.assertEqual(summary['acceptable_count'], 230, "Expected 230 Acceptable quality records (Table 6.2)")
        self.assertEqual(summary['rejected_count'], 50, "Expected 50 Rejected records (Table 6.2)")
        self.assertAlmostEqual(summary['good_percentage'], 72.0, places=1)
        self.assertAlmostEqual(summary['acceptable_percentage'], 23.0, places=1)
        self.assertAlmostEqual(summary['rejected_percentage'], 5.0, places=1)

    def test_04_coordinate_boundaries(self):
        """Test that all valid records satisfy RA in [0, 360) and Dec in [-90, +90]."""
        pre = Preprocessor()
        df_unique, df_dups = pre.preprocess(self.df_raw)
        val = DataValidator()
        _, df_valid, _ = val.validate_and_flag(df_unique, df_dups)

        self.assertTrue((df_valid['right_ascension'] >= 0.0).all())
        self.assertTrue((df_valid['right_ascension'] < 360.0).all())
        self.assertTrue((df_valid['declination'] >= -90.0).all())
        self.assertTrue((df_valid['declination'] <= 90.0).all())
        self.assertTrue((df_valid['exposure_time'] > 0.0).all())

    def test_05_calibrator(self):
        """Test illustrative calibration module offsets and calibrated magnitude calculations."""
        pre = Preprocessor()
        df_unique, df_dups = pre.preprocess(self.df_raw)
        val = DataValidator()
        _, df_valid, _ = val.validate_and_flag(df_unique, df_dups)

        cal = Calibrator()
        df_cal = cal.calibrate(df_valid)

        self.assertEqual(len(df_cal), len(df_valid))
        self.assertIn('calibrated_brightness', df_cal.columns)
        self.assertIn('bias_correction_offset', df_cal.columns)
        self.assertIn('dark_correction_offset', df_cal.columns)
        self.assertIn('flat_field_factor', df_cal.columns)

    def test_06_feature_extraction(self):
        """Test astronomical object categorization and telescope metrics."""
        pre = Preprocessor()
        df_unique, df_dups = pre.preprocess(self.df_raw)
        val = DataValidator()
        _, df_valid, _ = val.validate_and_flag(df_unique, df_dups)
        cal = Calibrator()
        df_cal = cal.calibrate(df_valid)

        fe = FeatureExtractor()
        ana = fe.analyze_catalog(df_cal, self.df_objects, self.df_telescopes)

        obj_dist = ana['object_distribution']
        self.assertEqual(obj_dist['Star']['count'], 1720, "Expected 1,720 Stars (Table 6.3)")
        self.assertEqual(obj_dist['Galaxy']['count'], 685, "Expected 685 Galaxies (Table 6.3)")
        self.assertEqual(obj_dist['Planet']['count'], 120, "Expected 120 Planets (Table 6.3)")
        self.assertEqual(obj_dist['Other']['count'], 320, "Expected 320 Other objects (Table 6.3)")
        self.assertEqual(ana['total_objects_cataloged'], 2845)

    def test_07_visualizer_and_exporter(self):
        """Test chart generation and output file persistence."""
        pre = Preprocessor()
        df_unique, df_dups = pre.preprocess(self.df_raw)
        val = DataValidator()
        _, df_valid, df_rejected = val.validate_and_flag(df_unique, df_dups)
        cal = Calibrator()
        df_cal = cal.calibrate(df_valid)
        fe = FeatureExtractor()
        ana = fe.analyze_catalog(df_cal, self.df_objects, self.df_telescopes)

        viz = Visualizer()
        charts = viz.generate_all_charts(val.validation_summary, ana, df_cal, self.df_objects)
        self.assertEqual(len(charts), 5)
        for c in charts:
            self.assertTrue(c.exists(), f"Chart file must exist: {c}")

        exporter = DataExporter()
        exports = exporter.export_all(df_cal, df_rejected, self.df_objects, val.validation_summary, ana)
        for name, p in exports.items():
            self.assertTrue(p.exists(), f"Export file must exist: {p}")

        html_gen = HTMLDashboardGenerator()
        html_p = html_gen.generate(val.validation_summary, ana)
        self.assertTrue(html_p.exists(), f"HTML dashboard must exist: {html_p}")


if __name__ == '__main__':
    unittest.main()
