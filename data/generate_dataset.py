"""
Dataset Generator for Astronomy Telescope Cataloging Project.

Generates illustrative synthetic datasets matching the project report:
- 1,000 observation records (950 valid [720 Good, 230 Acceptable], 50 rejected/flagged)
- 2,845 cataloged astronomical objects (1,720 Stars, 685 Galaxies, 120 Planets, 320 Other)
- 5 telescope profiles

DISCLAIMER: All generated records are synthetic/illustrative mock observations
for educational and software testing purposes, NOT real physical telescope measurements.
"""

import csv
import random
import datetime
from pathlib import Path

# Fix seed for strict reproducibility matching project report numbers
random.seed(42)

DATA_DIR = Path(__file__).resolve().parent

TELESCOPE_IDS = ['TEL-01', 'TEL-02', 'TEL-03', 'TEL-04', 'TEL-05']
FILTERS = ['U', 'B', 'V', 'R', 'I', 'Clear']
OBJECT_TYPES = ['Star', 'Galaxy', 'Planet', 'Other']

TARGET_PRESETS = [
    ('Messier 31 (Andromeda)', 'Galaxy', 10.68, 41.27),
    ('Messier 42 (Orion Nebula)', 'Other', 83.82, -5.39),
    ('Messier 45 (Pleiades)', 'Star', 56.87, 24.11),
    ('Sirius Field', 'Star', 101.29, -16.72),
    ('Betelgeuse Region', 'Star', 88.79, 7.41),
    ('Vega Calibration Field', 'Star', 279.23, 38.78),
    ('Jupiter Opposition Area', 'Planet', 45.12, 16.42),
    ('Saturn Ring System Area', 'Planet', 335.61, -11.28),
    ('Mars Orbit Vicinity', 'Planet', 78.44, 23.15),
    ('Whirlpool Galaxy (M51)', 'Galaxy', 202.47, 47.20),
    ('Sombrero Galaxy (M104)', 'Galaxy', 189.99, -11.62),
    ('Crab Nebula (M1)', 'Other', 83.63, 22.01),
    ('Ring Nebula (M57)', 'Other', 283.40, 33.03),
    ('Omega Centauri Cluster', 'Star', 201.70, -47.48),
    ('Helix Nebula (NGC 7293)', 'Other', 337.41, -20.84),
]

def generate_datasets():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Generate telescopes.csv
    telescopes = [
        {
            'telescope_id': 'TEL-01',
            'telescope_name': 'Himalayan Chandra Optical Telescope',
            'telescope_type': 'Optical',
            'location': 'Hanle, Ladakh, India',
            'aperture_m': 2.01,
            'focal_ratio': 'f/9',
            'detector': 'CCD 2048x2048'
        },
        {
            'telescope_id': 'TEL-02',
            'telescope_name': 'Vainu Bappu Observatory Reflector',
            'telescope_type': 'Optical',
            'location': 'Kavalur, Tamil Nadu, India',
            'aperture_m': 2.34,
            'focal_ratio': 'f/3.25',
            'detector': 'Prime Focus CCD'
        },
        {
            'telescope_id': 'TEL-03',
            'telescope_name': 'Giant Metrewave Radio Telescope',
            'telescope_type': 'Radio',
            'location': 'Pune, Maharashtra, India',
            'aperture_m': 45.00,
            'focal_ratio': 'Parabolic',
            'detector': 'L-Band Receiver'
        },
        {
            'telescope_id': 'TEL-04',
            'telescope_name': 'AstroSat Space Observatory',
            'telescope_type': 'Space',
            'location': 'Low Earth Orbit (650 km)',
            'aperture_m': 0.38,
            'focal_ratio': 'Cassegrain',
            'detector': 'UVIT / LAXPC'
        },
        {
            'telescope_id': 'TEL-05',
            'telescope_name': 'Mount Abu Infra-Red Observatory',
            'telescope_type': 'Optical',
            'location': 'Gurushikhar, Rajasthan, India',
            'aperture_m': 1.20,
            'focal_ratio': 'f/13',
            'detector': 'NICMOS Near-IR'
        }
    ]

    with open(DATA_DIR / 'telescopes.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(telescopes[0].keys()))
        writer.writeheader()
        writer.writerows(telescopes)

    # 2. Generate sample_observations.csv
    # Total: 1,000 records
    # Valid: 950 records (720 Good, 230 Acceptable)
    # Rejected/Flagged: 50 records
    # Spanning 12 months in 2025: 2025-01-01 to 2025-12-31

    obs_records = []
    start_date = datetime.date(2025, 1, 1)

    # Distribution across 12 months (approximate realistic counts matching Figure 6.3 in report)
    # Total monthly observations sum to 950 valid + 40 rejected non-duplicates = 990 + 10 duplicate rows = 1000
    monthly_weights = [85, 78, 92, 70, 65, 55, 48, 62, 80, 105, 115, 135]  # sum is 990 unique dates
    total_months = 12

    def random_timestamp_in_month(month):
        # choose a day between 1 and 28
        day = random.randint(1, 28)
        dt = datetime.date(2025, month, day)
        hour = random.choice([20, 21, 22, 23, 0, 1, 2, 3, 4])
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        return dt.isoformat(), f"{hour:02d}:{minute:02d}:{second:02d}"

    # Generate 720 Good records
    # Good criteria: valid RA [0, 360), valid Dec [-90, +90], exposure 60-1800s, filter present,
    # brightness 6.0 - 20.5 mag, SNR >= 15.0
    for i in range(1, 721):
        obs_id = f"OBS-{i:04d}"
        month = random.choices(range(1, 13), weights=monthly_weights)[0]
        obs_date, obs_time = random_timestamp_in_month(month)
        t_preset = random.choice(TARGET_PRESETS)
        ra = round((t_preset[2] + random.uniform(-2.5, 2.5)) % 360.0, 4)
        dec = round(max(-89.0, min(89.0, t_preset[3] + random.uniform(-2.5, 2.5))), 4)
        exp_time = round(random.uniform(60.0, 1800.0), 1)
        filt = random.choice(FILTERS)
        brightness = round(random.uniform(7.5, 19.5), 2)
        snr = round(random.uniform(18.0, 120.0), 1)
        tel_id = random.choice(TELESCOPE_IDS)
        airmass = round(random.uniform(1.05, 1.85), 2)
        weather = random.choice(['Clear', 'Clear', 'Clear', 'Partly Cloudy'])

        obs_records.append({
            'observation_id': obs_id,
            'telescope_id': tel_id,
            'observation_date': obs_date,
            'observation_time': obs_time,
            'target_name': t_preset[0],
            'primary_object_type': t_preset[1],
            'right_ascension': ra,
            'declination': dec,
            'exposure_time': exp_time,
            'filter': filt,
            'brightness': brightness,
            'snr': snr,
            'airmass': airmass,
            'weather_condition': weather,
            'dataset_note': 'Illustrative mock data for cataloging project'
        })

    # Generate 230 Acceptable records
    # Acceptable criteria: valid RA/Dec, exposure 15-90s, filter present,
    # brightness 14.0 - 21.8 mag, SNR 5.0 - 14.9
    for i in range(721, 951):
        obs_id = f"OBS-{i:04d}"
        month = random.choices(range(1, 13), weights=monthly_weights)[0]
        obs_date, obs_time = random_timestamp_in_month(month)
        t_preset = random.choice(TARGET_PRESETS)
        ra = round((t_preset[2] + random.uniform(-4.0, 4.0)) % 360.0, 4)
        dec = round(max(-89.0, min(89.0, t_preset[3] + random.uniform(-4.0, 4.0))), 4)
        exp_time = round(random.uniform(15.0, 120.0), 1)
        filt = random.choice(FILTERS)
        brightness = round(random.uniform(13.5, 21.8), 2)
        snr = round(random.uniform(5.5, 14.8), 1)
        tel_id = random.choice(TELESCOPE_IDS)
        airmass = round(random.uniform(1.60, 2.40), 2)
        weather = random.choice(['Partly Cloudy', 'Windy', 'High Humidity'])

        obs_records.append({
            'observation_id': obs_id,
            'telescope_id': tel_id,
            'observation_date': obs_date,
            'observation_time': obs_time,
            'target_name': t_preset[0],
            'primary_object_type': t_preset[1],
            'right_ascension': ra,
            'declination': dec,
            'exposure_time': exp_time,
            'filter': filt,
            'brightness': brightness,
            'snr': snr,
            'airmass': airmass,
            'weather_condition': weather,
            'dataset_note': 'Illustrative mock data for cataloging project'
        })

    # Generate 40 distinct invalid/corrupted records (plus 10 duplicate rows below = 50 rejected total)
    # Types of errors:
    # 1. Invalid coordinates (RA > 360 or < 0, Dec > 90 or < -90) -> 10 records
    # 2. Invalid exposure time (<= 0 or extreme) -> 10 records
    # 3. Missing essential fields (empty filter, missing telescope, empty date) -> 10 records
    # 4. Invalid brightness / corrupted signal (brightness > 90 or negative or NaN, snr <= 2.0) -> 10 records
    current_obs_num = 951

    # Error type 1: Invalid coordinates (10 records)
    for _ in range(10):
        obs_id = f"OBS-{current_obs_num:04d}"
        current_obs_num += 1
        month = random.randint(1, 12)
        obs_date, obs_time = random_timestamp_in_month(month)
        t_preset = random.choice(TARGET_PRESETS)
        coord_fault = random.choice(['ra_high', 'ra_neg', 'dec_high', 'dec_low'])
        if coord_fault == 'ra_high':
            ra, dec = round(random.uniform(365.0, 420.0), 4), round(random.uniform(-40, 40), 4)
        elif coord_fault == 'ra_neg':
            ra, dec = round(random.uniform(-50.0, -1.0), 4), round(random.uniform(-40, 40), 4)
        elif coord_fault == 'dec_high':
            ra, dec = round(random.uniform(10, 300), 4), round(random.uniform(91.5, 120.0), 4)
        else:
            ra, dec = round(random.uniform(10, 300), 4), round(random.uniform(-115.0, -91.5), 4)

        obs_records.append({
            'observation_id': obs_id,
            'telescope_id': random.choice(TELESCOPE_IDS),
            'observation_date': obs_date,
            'observation_time': obs_time,
            'target_name': t_preset[0],
            'primary_object_type': t_preset[1],
            'right_ascension': ra,
            'declination': dec,
            'exposure_time': round(random.uniform(60, 300), 1),
            'filter': random.choice(FILTERS),
            'brightness': round(random.uniform(10, 18), 2),
            'snr': round(random.uniform(15, 60), 1),
            'airmass': 1.25,
            'weather_condition': 'Clear',
            'dataset_note': 'Illustrative mock data - deliberately invalid coordinate test'
        })

    # Error type 2: Non-positive / invalid exposure time (10 records)
    for _ in range(10):
        obs_id = f"OBS-{current_obs_num:04d}"
        current_obs_num += 1
        month = random.randint(1, 12)
        obs_date, obs_time = random_timestamp_in_month(month)
        t_preset = random.choice(TARGET_PRESETS)
        exp_time = random.choice([0.0, -30.0, -120.0, -1.5, ''])

        obs_records.append({
            'observation_id': obs_id,
            'telescope_id': random.choice(TELESCOPE_IDS),
            'observation_date': obs_date,
            'observation_time': obs_time,
            'target_name': t_preset[0],
            'primary_object_type': t_preset[1],
            'right_ascension': round(random.uniform(20, 340), 4),
            'declination': round(random.uniform(-60, 60), 4),
            'exposure_time': exp_time,
            'filter': random.choice(FILTERS),
            'brightness': round(random.uniform(10, 18), 2),
            'snr': 18.5,
            'airmass': 1.30,
            'weather_condition': 'Clear',
            'dataset_note': 'Illustrative mock data - invalid exposure time test'
        })

    # Error type 3: Missing essential fields (10 records)
    for _ in range(10):
        obs_id = f"OBS-{current_obs_num:04d}"
        current_obs_num += 1
        month = random.randint(1, 12)
        obs_date, obs_time = random_timestamp_in_month(month)
        t_preset = random.choice(TARGET_PRESETS)
        missing_type = random.choice(['filter', 'telescope_id', 'date'])

        tel_id = '' if missing_type == 'telescope_id' else random.choice(TELESCOPE_IDS)
        filt = '' if missing_type == 'filter' else random.choice(FILTERS)
        dt = '' if missing_type == 'date' else obs_date

        obs_records.append({
            'observation_id': obs_id,
            'telescope_id': tel_id,
            'observation_date': dt,
            'observation_time': obs_time,
            'target_name': t_preset[0],
            'primary_object_type': t_preset[1],
            'right_ascension': round(random.uniform(20, 340), 4),
            'declination': round(random.uniform(-60, 60), 4),
            'exposure_time': round(random.uniform(60, 300), 1),
            'filter': filt,
            'brightness': round(random.uniform(10, 18), 2),
            'snr': 22.0,
            'airmass': 1.35,
            'weather_condition': 'Clear',
            'dataset_note': 'Illustrative mock data - missing metadata test'
        })

    # Error type 4: Corrupt / out-of-range brightness or extreme noise (10 records)
    for _ in range(10):
        obs_id = f"OBS-{current_obs_num:04d}"
        current_obs_num += 1
        month = random.randint(1, 12)
        obs_date, obs_time = random_timestamp_in_month(month)
        t_preset = random.choice(TARGET_PRESETS)
        b_val = random.choice([999.0, -85.0, '', 'CORRUPT_SENSOR'])

        obs_records.append({
            'observation_id': obs_id,
            'telescope_id': random.choice(TELESCOPE_IDS),
            'observation_date': obs_date,
            'observation_time': obs_time,
            'target_name': t_preset[0],
            'primary_object_type': t_preset[1],
            'right_ascension': round(random.uniform(20, 340), 4),
            'declination': round(random.uniform(-60, 60), 4),
            'exposure_time': round(random.uniform(60, 300), 1),
            'filter': random.choice(FILTERS),
            'brightness': b_val,
            'snr': round(random.uniform(0.5, 1.8), 1),
            'airmass': 2.80,
            'weather_condition': 'Overcast Sensor Saturation',
            'dataset_note': 'Illustrative mock data - corrupt brightness test'
        })

    # Duplicate records (10 records)
    # Duplicate existing valid records OBS-0010 to OBS-0019 to test duplicate identification
    for d_idx in range(9, 19):
        dup_row = dict(obs_records[d_idx])
        # Mark as duplicate in note for verification
        dup_row['dataset_note'] = 'Illustrative mock data - deliberate duplicate record'
        obs_records.append(dup_row)

    # Now total obs_records length is exactly:
    # 720 (Good) + 230 (Acceptable) + 40 (Faulty) + 10 (Duplicates) = 1,000 records!
    assert len(obs_records) == 1000, f"Expected 1000 records, got {len(obs_records)}"

    obs_fields = [
        'observation_id', 'telescope_id', 'observation_date', 'observation_time',
        'target_name', 'primary_object_type', 'right_ascension', 'declination',
        'exposure_time', 'filter', 'brightness', 'snr', 'airmass', 'weather_condition',
        'dataset_note'
    ]

    with open(DATA_DIR / 'sample_observations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=obs_fields)
        writer.writeheader()
        writer.writerows(obs_records)

    print(f"Generated data/sample_observations.csv with {len(obs_records)} records.")

    # 3. Generate sample_objects.csv (2,845 cataloged celestial objects matching Table 6.3 in report)
    # Stars: 1,720 (60.46%)
    # Galaxies: 685 (24.08%)
    # Planets: 120 (4.22%)
    # Other objects: 320 (11.25%)
    # Total: 2,845

    objects_list = []
    valid_obs_ids = [f"OBS-{i:04d}" for i in range(1, 951)]

    # Object generator helper
    obj_counter = 1

    def make_object(obj_type, brightness_range, size_range, notes_choices):
        nonlocal obj_counter
        obj_id = f"OBJ-{obj_counter:04d}"
        obj_counter += 1
        parent_obs = random.choice(valid_obs_ids)
        ra = round(random.uniform(0.0, 359.99), 4)
        dec = round(random.uniform(-89.0, 89.0), 4)
        mag = round(random.uniform(*brightness_range), 2)
        size = round(random.uniform(*size_range), 2)
        note = random.choice(notes_choices)
        return {
            'object_id': obj_id,
            'observation_id': parent_obs,
            'object_type': obj_type,
            'right_ascension': ra,
            'declination': dec,
            'apparent_magnitude': mag,
            'estimated_size_arcsec': size,
            'description': note,
            'dataset_note': 'Illustrative mock object'
        }

    # 1,720 Stars
    star_notes = ['Main Sequence Star', 'Red Giant Candidate', 'White Dwarf', 'Binary Star Component', 'Variable Star']
    for _ in range(1720):
        objects_list.append(make_object('Star', (5.5, 18.5), (0.8, 3.2), star_notes))

    # 685 Galaxies
    galaxy_notes = ['Spiral Galaxy Core', 'Elliptical Galaxy', 'Lenticular Galaxy', 'Dwarf Galaxy', 'Interacting Galaxy Pair']
    for _ in range(685):
        objects_list.append(make_object('Galaxy', (12.0, 21.8), (15.0, 180.0), galaxy_notes))

    # 120 Planets
    planet_notes = ['Gas Giant Observation', 'Inner Terrestrial Planet', 'Ice Giant Tracking', 'Planetary Transit Candidate']
    for _ in range(120):
        objects_list.append(make_object('Planet', (3.5, 14.5), (5.0, 48.0), planet_notes))

    # 320 Other objects
    other_notes = ['Diffuse Emission Nebula', 'Open Star Cluster', 'Planetary Nebula', 'Near-Earth Asteroid Track', 'Cometary Coma']
    for _ in range(320):
        objects_list.append(make_object('Other', (9.0, 20.0), (4.0, 95.0), other_notes))

    # Shuffle objects list deterministically so types are naturally distributed
    random.shuffle(objects_list)
    # Re-assign sequential IDs
    for idx, obj in enumerate(objects_list, start=1):
        obj['object_id'] = f"OBJ-{idx:04d}"

    assert len(objects_list) == 2845, f"Expected 2845 objects, got {len(objects_list)}"

    obj_fields = [
        'object_id', 'observation_id', 'object_type', 'right_ascension', 'declination',
        'apparent_magnitude', 'estimated_size_arcsec', 'description', 'dataset_note'
    ]

    with open(DATA_DIR / 'sample_objects.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=obj_fields)
        writer.writeheader()
        writer.writerows(objects_list)

    print(f"Generated data/sample_objects.csv with {len(objects_list)} objects.")
    print("Dataset generation completed successfully.")

if __name__ == '__main__':
    generate_datasets()
