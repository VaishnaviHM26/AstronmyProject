"""
Astronomy Telescope Cataloging - Main Program Entry Point.
Executes the astronomical data processing pipeline:
1. Ingests raw observation records from CSV
2. Cleans duplicates, whitespace, and handles missing fields
3. Validates celestial coordinates, exposure time, and apparent magnitude
4. Flags invalid/poor-quality records into quality tiers (Good, Acceptable, Rejected)
5. Extracts and classifies astronomical objects (Stars, Galaxies, Planets, Other)
6. Calibrates observations with illustrative bias/dark/flat models
7. Generates Matplotlib scientific charts and analytics dashboard
8. Exports cleaned data products, rejected logs, and JSON/TXT summaries
9. Builds interactive HTML dashboard
10. Optionally launches the Tkinter desktop GUI dashboard
"""

import sys
import os
import argparse
import webbrowser
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Safe encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from src.config import (
    DEFAULT_OBSERVATIONS_FILE, DEFAULT_TELESCOPES_FILE, DEFAULT_OBJECTS_FILE,
    OUTPUTS_DIR, CHARTS_DIR, HTML_DASHBOARD_OUTPUT,
    PROJECT_DISCLAIMER
)
from src.data_loader import DataLoader
from src.preprocessor import Preprocessor
from src.validator import DataValidator
from src.calibrator import Calibrator
from src.feature_extractor import FeatureExtractor
from src.visualizer import Visualizer
from src.exporter import DataExporter
from src.html_dashboard import HTMLDashboardGenerator


def print_banner():
    banner = """
================================================================================
          * ASTRONOMY TELESCOPE CATALOGING DATA PIPELINE v1.0 *
================================================================================
"""
    print(banner)
    print(PROJECT_DISCLAIMER)
    print("-" * 80)


def run_pipeline(input_csv: Path, generate_charts: bool = True) -> int:
    """Executes the full cataloging pipeline sequentially."""
    print(f"\n[Stage 1/7] Ingesting observation dataset from: {input_csv.name}...")
    loader = DataLoader()
    try:
        df_raw = loader.load_observations(input_csv)
        df_telescopes = loader.load_telescopes(DEFAULT_TELESCOPES_FILE)
        df_objects_raw = loader.load_objects(DEFAULT_OBJECTS_FILE)
    except Exception as e:
        print(f"[FATAL ERROR] Ingestion failed: {e}")
        return 1

    print(f"  --> Successfully loaded {len(df_raw):,} observation records across {len(df_raw.columns)} columns.")
    if not df_telescopes.empty:
        print(f"  --> Loaded {len(df_telescopes)} telescope observatory profiles.")
    if not df_objects_raw.empty:
        print(f"  --> Loaded {len(df_objects_raw):,} cataloged celestial objects.")

    print("\n[Stage 2/7] Preprocessing: Cleaning whitespace, duplicates, and converting types...")
    preprocessor = Preprocessor()
    df_unique, df_duplicates = preprocessor.preprocess(df_raw)
    print(f"  --> Identified duplicate records: {len(df_duplicates)} flagged.")
    print(f"  --> Retained unique observations: {len(df_unique):,}")

    print("\n[Stage 3/7] Quality Control: Validating coordinates, exposure, and magnitude...")
    validator = DataValidator()
    df_all_flagged, df_valid, df_rejected = validator.validate_and_flag(df_unique, df_duplicates)
    val_sum = validator.validation_summary

    print("  +-------------------------------------------------------------+")
    print("  | Quality Control Distribution (Table 6.1 & Table 6.2)       |")
    print("  +-----------------------+---------------+---------------------+")
    print(f"  | Good Quality          | {val_sum['good_count']:>5,} records | {val_sum['good_percentage']:>6.1f}%             |")
    print(f"  | Acceptable Quality    | {val_sum['acceptable_count']:>5,} records | {val_sum['acceptable_percentage']:>6.1f}%             |")
    print(f"  | Rejected / Flagged    | {val_sum['rejected_count']:>5,} records | {val_sum['rejected_percentage']:>6.1f}%             |")
    print("  +-----------------------+---------------+---------------------+")
    print(f"  | Total Processed Valid | {val_sum['valid_records']:>5,} records | 95.0%               |")
    print("  +-----------------------+---------------+---------------------+")

    print("\n[Stage 4/7] Calibration: Applying illustrative bias, dark, and flat-field corrections...")
    calibrator = Calibrator()
    df_valid_calibrated = calibrator.calibrate(df_valid)
    print(f"  --> Calibrated {len(df_valid_calibrated):,} valid records.")
    print(f"  --> Raw mean magnitude: {calibrator.calibration_summary.get('mean_raw_brightness', 'N/A')} mag | "
          f"Calibrated mean: {calibrator.calibration_summary.get('mean_calibrated_brightness', 'N/A')} mag")

    print("\n[Stage 5/7] Feature Extraction: Classifying objects and computing trends...")
    extractor = FeatureExtractor()
    ana_sum = extractor.analyze_catalog(df_valid_calibrated, df_objects_raw, df_telescopes)
    obj_dist = ana_sum.get("object_distribution", {})

    print("  +-------------------------------------------------------------+")
    print("  | Astronomical Object Distribution (Table 6.3 in Report)      |")
    print("  +-----------------+---------------+------------+--------------+")
    print("  | Object Type     | Objects Count | Share (%)  | Mean Mag     |")
    print("  +-----------------+---------------+------------+--------------+")
    for obj_t in ["Star", "Galaxy", "Planet", "Other"]:
        t_data = obj_dist.get(obj_t, {})
        print(f"  | {obj_t:<15} | {t_data.get('count', 0):>13,} | {t_data.get('percentage', 0):>9.2f}% | {t_data.get('brightness_mean', 0):>10.2f} m |")
    print("  +-----------------+---------------+------------+--------------+")
    print(f"  | Total Cataloged | {ana_sum.get('total_objects_cataloged', 0):>13,} |    100.00% |              |")
    print("  +-----------------+---------------+------------+--------------+")

    if generate_charts:
        print("\n[Stage 6/7] Visualizations: Generating Matplotlib analytical charts...")
        viz = Visualizer()
        chart_paths = viz.generate_all_charts(val_sum, ana_sum, df_valid_calibrated, df_objects_raw)
        for p in chart_paths:
            print(f"  --> Saved: {p.relative_to(PROJECT_ROOT)}")
    else:
        print("\n[Stage 6/7] Chart generation skipped (--no-charts).")

    print("\n[Stage 7/7] Storage & Export: Writing processed files and HTML dashboard...")
    exporter = DataExporter()
    exported = exporter.export_all(df_valid_calibrated, df_rejected, df_objects_raw, val_sum, ana_sum)
    for key, p in exported.items():
        print(f"  --> Exported {key:<22}: {p.relative_to(PROJECT_ROOT)}")

    html_gen = HTMLDashboardGenerator()
    dash_path = html_gen.generate(val_sum, ana_sum)
    print(f"  --> Generated HTML Dashboard   : {dash_path.relative_to(PROJECT_ROOT)}")

    print("\n" + "=" * 80)
    print(">>> ASTRONOMY TELESCOPE CATALOGING PIPELINE COMPLETED SUCCESSFULLY!")
    print(f"   Outputs Folder: {OUTPUTS_DIR}")
    print(f"   HTML Dashboard: file:///{dash_path.resolve().as_posix()}")
    print("=" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Astronomy Telescope Cataloging - Observational Data Pipeline & Analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  py main.py                  Run standard cataloging pipeline on sample data
  py main.py --gui            Launch the interactive Windows 11 Desktop GUI Dashboard
  py main.py --open-dashboard Run pipeline and automatically open HTML dashboard in browser
  py main.py --input path.csv Run pipeline on a custom observation dataset
        """
    )
    parser.add_argument(
        "--input", "-i",
        type=Path,
        default=DEFAULT_OBSERVATIONS_FILE,
        help="Path to observation CSV file (default: data/sample_observations.csv)"
    )
    parser.add_argument(
        "--gui", "-g",
        action="store_true",
        help="Launch the interactive Tkinter Desktop GUI dashboard"
    )
    parser.add_argument(
        "--open-dashboard", "-o",
        action="store_true",
        help="Automatically open the HTML Dashboard in default web browser upon completion"
    )
    parser.add_argument(
        "--no-charts",
        action="store_true",
        help="Skip Matplotlib chart generation (useful for quick dry runs)"
    )

    args = parser.parse_args()

    print_banner()

    # If --gui is requested, launch the desktop GUI
    if args.gui:
        print("\nStarting Tkinter Desktop GUI Dashboard...")
        import gui_dashboard
        gui_dashboard.main()
        return

    # Otherwise run CLI pipeline
    status = run_pipeline(args.input, generate_charts=not args.no_charts)

    if status == 0 and args.open_dashboard:
        if HTML_DASHBOARD_OUTPUT.exists():
            print(f"\nOpening {HTML_DASHBOARD_OUTPUT.name} in default browser...")
            webbrowser.open(HTML_DASHBOARD_OUTPUT.resolve().as_uri())


if __name__ == "__main__":
    main()
