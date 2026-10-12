# 🔭 Astronomy Telescope Cataloging

> **A complete, beginner-friendly Python data engineering and scientific cataloging pipeline for astronomical observations on Windows 11.**

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2011-0078d4)](https://microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Tests](https://img.shields.io/badge/Tests-Passing%20(7%2F7)-success)](#automated-testing)

---

## 📌 Important Transparency & Educational Disclaimer

> [!NOTE]
> **Illustrative Synthetic Dataset & Algorithmic Scope:**
> This project uses a curated **illustrative mock dataset** (1,000 observation records, 5 observatory profiles, and 2,845 cataloged celestial objects) designed for educational data engineering, cleaning, quality control, and scientific visualization demonstrations.
> 
> The calibration module applies a **simplified educational tabular mathematical model** (electronic bias offset, exposure-dependent thermal dark current, and optical flat-field filter response) to illustrate the multi-stage astronomical processing workflow. **This software does not claim real-time telescope hardware driving, live sensor interfacing, or pixel-level CCD FITS reduction.**

---

## 📖 Project Overview

Modern astronomical observatories generate massive volumes of observational records across optical, radio, and space-borne instruments. Raw observations often contain duplicate readings, incomplete metadata, invalid coordinates, and noisy exposures. 

The **Astronomy Telescope Cataloging** system implements an automated 7-stage data pipeline based on the project report:

```
Raw CSV Ingestion ──> Preprocessing & Cleaning ──> Quality Control & Flagging
                                                            │
Storage & Reporting <── Analytical Visualization <── Calibration & Feature Extraction
```

### 🎯 Key Results Matching Project Report

| Metric | Project Report Value | Implementation Result | Match Status |
| :--- | :--- | :--- | :--- |
| **Total Ingested Observations** | 1,000 records | **1,000 records** | Exact ✅ |
| **Successfully Processed (Valid)** | 950 records (95.0%) | **950 records (95.0%)** | Exact ✅ |
| **Flagged / Rejected Records** | 50 records (5.0%) | **50 records (5.0%)** | Exact ✅ |
| **Good Quality Observations** | 720 records (72.0%) | **720 records (72.0%)** | Exact ✅ |
| **Acceptable Quality Observations**| 230 records (23.0%) | **230 records (23.0%)** | Exact ✅ |
| **Total Cataloged Objects** | 2,845 objects | **2,845 objects** | Exact ✅ |
| **Stars Cataloged** | 1,720 (60.46%) | **1,720 (60.46%)** | Exact ✅ |
| **Galaxies Cataloged** | 685 (24.08%) | **685 (24.08%)** | Exact ✅ |
| **Planets Cataloged** | 120 (4.22%) | **120 (4.22%)** | Exact ✅ |
| **Other Celestial Objects** | 320 (11.25%) | **320 (11.25%)** | Exact ✅ |
| **Observatories Active** | 5 telescopes | **5 telescopes** | Exact ✅ |
| **Observation Period** | 12 months | **12 months (M1–M12)**| Exact ✅ |

---

## 🛠️ Features Implemented

1. **Astronomical CSV Ingestion (`DataLoader`):**
   - Validates existence, format, schema integrity, and required columns (`observation_id`, `telescope_id`, `right_ascension`, `declination`, `exposure_time`, `filter`, `brightness`).
   - Supports telescope registry metadata and cataloged object linkage.

2. **Data Cleaning & Duplicate Removal (`Preprocessor`):**
   - Trims whitespace and normalizes empty/missing entries.
   - Detects duplicate observations (identical telescope, timestamp, and pointing coordinates).
   - Safely parses and coerces numeric and ISO datetime fields.

3. **Celestial & Physical Validation (`DataValidator`):**
   - **Right Ascension (RA):** Validates decimal coordinates within $[0.0^\circ, 360.0^\circ)$.
   - **Declination (Dec):** Validates coordinates within $[-90.0^\circ, +90.0^\circ]$.
   - **Exposure Duration:** Validates strictly positive exposures ($> 0\text{ s}$ and $\le 7200\text{ s}$).
   - **Brightness:** Validates apparent magnitudes within astronomical telescopic limits ($-5.0$ to $+30.0\text{ mag}$).

4. **Multi-Tier Quality Classification (`DataValidator`):**
   - **Good (720 records / 72%):** High signal-to-noise ($\text{SNR} \ge 15.0$), valid coordinates, complete metadata.
   - **Acceptable (230 records / 23%):** Medium signal-to-noise ($5.0 \le \text{SNR} < 15.0$), minor atmospheric airmass, passed all validations.
   - **Rejected / Flagged (50 records / 5%):** Out-of-bounds coordinates, non-positive exposures, corrupted sensor magnitudes, duplicates, or missing filters.

5. **Tabular Calibration Model (`Calibrator`):**
   - Implements illustrative electronic bias compensation, dark current thermal accumulation scaling, and optical flat-field filter transmission factors ($U, B, V, R, I, \text{Clear}$).

6. **Feature Extraction & Classification (`FeatureExtractor`):**
   - Aggregates object types (Stars, Galaxies, Planets, Other).
   - Computes magnitude statistics (mean, median, min, max, standard deviation).
   - Evaluates observatory utilization and monthly activity across 12 operational months.

7. **Publication-Quality Visualizations (`Visualizer`):**
   - Built with **Pandas** and **Matplotlib** at 300 DPI:
     - `object_distribution.png`: Bar and Donut chart of cataloged objects.
     - `brightness_distribution.png`: Apparent magnitude histogram with statistical markers.
     - `observation_quality.png`: Quality control distribution (Good, Acceptable, Rejected).
     - `monthly_trends.png`: Monthly observation activity trend curve.
     - `astronomy_analytics_dashboard.png`: Composite 4-panel dashboard figure (matching Figure 5.1).

8. **Dual Dashboard Interfaces:**
   - **Desktop GUI Dashboard (`gui_dashboard.py`):** Native Windows 11 desktop app built with Python standard library `tkinter` (no external GUI frameworks required). Features live KPI cards, interactive table browsers with search and filtering, visual chart switcher, and live pipeline executor.
   - **Standalone Web Dashboard (`outputs/dashboard.html`):** Beautiful dark-mode responsive HTML dashboard with base64 embedded charts viewable offline in any browser.

---

## 📂 Project Directory Structure

```
AstronmyProject/
│
├── data/                                   # Data directory
│   ├── generate_dataset.py                 # Reproducible mock dataset generator
│   ├── sample_observations.csv             # 1,000 raw observation records
│   ├── telescopes.csv                      # 5 participating observatory profiles
│   └── sample_objects.csv                  # 2,845 cataloged celestial objects
│
├── src/                                    # Source code modules
│   ├── __init__.py                         # Package initialization
│   ├── config.py                           # Validation thresholds, limits, and file paths
│   ├── data_loader.py                      # Stage 1: CSV ingestion & schema validation
│   ├── preprocessor.py                     # Stage 2: Whitespace, duplicate & type cleaning
│   ├── validator.py                        # Stage 3: Coordinate, exposure, brightness QC
│   ├── calibrator.py                       # Stage 4: Illustrative tabular calibration
│   ├── feature_extractor.py                # Stage 5: Scientific object & trend analysis
│   ├── visualizer.py                       # Stage 6: Pandas & Matplotlib chart generation
│   ├── exporter.py                         # Stage 7: Persistence to CSV, JSON, and TXT
│   └── html_dashboard.py                  # Standalone interactive HTML dashboard generator
│
├── tests/                                  # Automated test suite
│   ├── __init__.py
│   └── test_pipeline.py                    # Unit tests for all 7 modules
│
├── outputs/                                # Generated deliverables (created on run)
│   ├── cleaned_observations.csv            # 950 valid observations with calibration metrics
│   ├── rejected_observations.csv           # 50 rejected records with explicit reason log
│   ├── cataloged_objects.csv               # 2,845 cataloged astronomical objects
│   ├── analysis_summary.json               # Structured machine-readable metrics
│   ├── analysis_summary.txt                # Formatted scientific textual summary report
│   ├── dashboard.html                      # Standalone interactive web dashboard
│   └── charts/                             # High-resolution 300 DPI analytical figures
│       ├── astronomy_analytics_dashboard.png
│       ├── object_distribution.png
│       ├── brightness_distribution.png
│       ├── observation_quality.png
│       └── monthly_trends.png
│
├── main.py                                 # Unified Command-Line Interface (CLI)
├── gui_dashboard.py                        # Native Windows 11 Desktop GUI Application
├── run_project.bat                         # One-click Windows 11 Batch Launcher
├── requirements.txt                        # Dependency specifications (pandas, matplotlib, numpy)
└── README.md                               # Complete documentation and setup guide
```

---

## 💻 Windows 11 Installation & Run Instructions

### Step 1: Open Terminal in Project Directory

Open **PowerShell** or **Command Prompt** and navigate to your workspace folder:
```powershell
cd c:\Users\hmvai\OneDrive\Desktop\AstronmyProject
```

### Step 2: (Optional but Recommended) Create a Virtual Environment

Using the Windows Python launcher (`py`):
```powershell
py -3.11 -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If you are using Command Prompt (`cmd.exe`), run: `venv\Scripts\activate.bat`)*

### Step 3: Install Required Dependencies

```powershell
py -m pip install -r requirements.txt
```
> **Dependencies installed:** `pandas`, `matplotlib`, and `numpy`. `tkinter` comes pre-installed with standard Windows Python installations.

---

## 🚀 Running the Project

You can run the project in three convenient ways:

### Option A: One-Click Windows 11 Batch Launcher (Easiest)
Simply double-click `run_project.bat` in Windows File Explorer, or run:
```cmd
run_project.bat
```
A beginner-friendly menu will appear allowing you to run the pipeline, launch the desktop GUI, open the HTML dashboard, or execute tests.

---

### Option B: Command-Line Interface (CLI)

Run the full end-to-end data pipeline:
```powershell
py main.py
```

Run the pipeline and **automatically open the HTML dashboard in your web browser**:
```powershell
py main.py --open-dashboard
```

Run on a **custom observation CSV file**:
```powershell
py main.py --input "path\to\your_observations.csv"
```

View all command-line options:
```powershell
py main.py --help
```

---

### Option C: Native Windows 11 Desktop GUI Dashboard

Launch the desktop GUI app with interactive search, filters, table viewers, and embedded charts:
```powershell
py main.py --gui
```
*or directly:*
```powershell
py gui_dashboard.py
```

#### Desktop GUI Features:
- **Top KPI Cards:** Live overview of total ingested, valid, rejected, and cataloged objects.
- **Analytics & Charts Tab:** Dropdown switcher to view high-resolution figures.
- **Valid Observations Tab:** Search by target or telescope ID, filter by quality status (Good / Acceptable).
- **Rejected Records Tab:** Full inspection of all 50 flagged records and diagnostic rejection causes.
- **Celestial Objects Tab:** Filter by Stars, Galaxies, Planets, or Other objects.
- **Pipeline Controller Tab:** One-click button to re-run the pipeline on any input file with live terminal output.

---

## 🧪 Automated Testing

A comprehensive unit test suite is included in `tests/test_pipeline.py`. To run all 7 test suites:

```powershell
py -m unittest tests/test_pipeline.py
```

**Test Coverage:**
- `test_01_data_ingestion`: Validates CSV loading and schema integrity.
- `test_02_preprocessing`: Validates whitespace cleaning and duplicate isolation (10 rows).
- `test_03_quality_control_validation`: Validates exact quality counts (720 Good, 230 Acceptable, 50 Rejected).
- `test_04_coordinate_boundaries`: Checks coordinate bounds on RA and Dec.
- `test_05_calibrator`: Tests illustrative bias, dark, and flat-field calculations.
- `test_06_feature_extraction`: Validates object distribution (1,720 Stars, 685 Galaxies, 120 Planets, 320 Other).
- `test_07_visualizer_and_exporter`: Verifies physical generation of all 5 charts, CSVs, JSON, TXT, and HTML deliverables.

---

## 📊 Scientific Deliverables Summary

After execution, examine the generated files in `outputs/`:
- **`cleaned_observations.csv`:** Cleaned dataset containing 950 valid observations with calibrated brightness and SNR values.
- **`rejected_observations.csv`:** Detailed diagnostic file listing the 50 flagged observations alongside clear reasons (e.g. `Invalid Right Ascension (385.20°): must be in [0.0°, 360.0°)`, `Non-positive exposure time (-30.0 s)`, `Duplicate observation record`).
- **`cataloged_objects.csv`:** Registry of all 2,845 celestial objects.
- **`analysis_summary.txt`:** Formatted scientific report suitable for presentation.
- **`dashboard.html`:** Self-contained offline web dashboard.
- **`charts/`:** Publication-grade visualizations at 300 DPI.

---

## 🔧 Windows 11 Troubleshooting

1. **"py: command not found" or "python was not found":**
   - Ensure Python 3.10+ is installed from [python.org](https://www.python.org/).
   - During installation, make sure to check **"Add Python to PATH"** and **"Install launcher for all users"**.
2. **Script Execution Policy (PowerShell):**
   - If activating a virtual environment returns an execution policy error, run PowerShell as Administrator and execute:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```
3. **Unicode / Console Characters:**
   - `main.py` automatically configures UTF-8 safe encoding with fallback replacement to ensure error-free printing on standard Windows consoles.

---

## 📜 License & Acknowledgments

- **Developed for:** Academic Project – *Astronomy Telescope Cataloging*
- **Technology Stack:** Python 3.11, Pandas, Matplotlib, NumPy, Tkinter
- **Author:** Ranjitha
