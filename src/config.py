"""
Configuration settings, validation boundaries, and constants for the
Astronomy Telescope Cataloging project.
"""

from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUTS_DIR = BASE_DIR / "outputs"
CHARTS_DIR = OUTPUTS_DIR / "charts"

# Default file paths
DEFAULT_OBSERVATIONS_FILE = DATA_DIR / "sample_observations.csv"
DEFAULT_TELESCOPES_FILE = DATA_DIR / "telescopes.csv"
DEFAULT_OBJECTS_FILE = DATA_DIR / "sample_objects.csv"

# Output files
CLEANED_OBSERVATIONS_OUTPUT = OUTPUTS_DIR / "cleaned_observations.csv"
REJECTED_OBSERVATIONS_OUTPUT = OUTPUTS_DIR / "rejected_observations.csv"
CATALOGED_OBJECTS_OUTPUT = OUTPUTS_DIR / "cataloged_objects.csv"
ANALYSIS_SUMMARY_JSON = OUTPUTS_DIR / "analysis_summary.json"
ANALYSIS_SUMMARY_TXT = OUTPUTS_DIR / "analysis_summary.txt"
HTML_DASHBOARD_OUTPUT = OUTPUTS_DIR / "dashboard.html"

# Required observation columns
REQUIRED_OBS_COLUMNS = [
    "observation_id",
    "telescope_id",
    "observation_date",
    "right_ascension",
    "declination",
    "exposure_time",
    "filter",
    "brightness"
]

# Coordinate validation limits
# Right Ascension: [0.0, 360.0) degrees (standard decimal celestial coordinates)
RA_MIN_DEG = 0.0
RA_MAX_DEG = 360.0

# Declination: [-90.0, +90.0] degrees
DEC_MIN_DEG = -90.0
DEC_MAX_DEG = 90.0

# Exposure time limits (seconds)
EXPOSURE_MIN_SEC = 0.001  # strictly positive
EXPOSURE_MAX_SEC = 7200.0  # 2 hours max single exposure

# Brightness limits (apparent magnitude scale)
# Magnitudes are inversely proportional to flux; -5 (bright Venus) to 30 (deep space telescope limit)
MAG_MIN = -5.0
MAG_MAX = 30.0

# Quality status thresholds
# Signal-to-Noise Ratio (SNR) benchmarks
GOOD_SNR_THRESHOLD = 15.0
ACCEPTABLE_SNR_THRESHOLD = 5.0

# Target scientific object categories
OBJECT_CATEGORIES = ["Star", "Galaxy", "Planet", "Other"]

# Filter transmission factors (illustrative optical weights)
FILTER_TRANSMISSION = {
    "U": 0.65,      # Ultraviolet
    "B": 0.82,      # Blue
    "V": 0.95,      # Visual / Green
    "R": 0.90,      # Red
    "I": 0.78,      # Infrared
    "Clear": 1.00   # Wideband clear
}

# Transparency notice
PROJECT_DISCLAIMER = (
    "DISCLAIMER & TRANSPARENCY NOTICE:\n"
    "This software uses synthetic illustrative astronomical records for educational\n"
    "data engineering, cataloging, and visualization demonstrations.\n"
    "Calibration algorithms represent simplified mathematical models and do NOT\n"
    "claim physical sensor-level CCD pixel reduction or real sky telescope driving."
)
