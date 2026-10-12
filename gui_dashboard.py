"""
Desktop GUI Dashboard for Astronomy Telescope Cataloging.
Built with Python standard library Tkinter (compatible out-of-the-box on Windows 11).
Provides:
- Real-time KPI Metric cards
- Visual chart browser for generated Matplotlib figures
- Tabular browser for Valid Observations (950), Rejected Records (50), and Cataloged Objects (2,845)
- Search and filtering capabilities
- Interactive Pipeline Runner with live console logs
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import webbrowser

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import (
    DATA_DIR, OUTPUTS_DIR, CHARTS_DIR,
    DEFAULT_OBSERVATIONS_FILE, DEFAULT_TELESCOPES_FILE, DEFAULT_OBJECTS_FILE,
    CLEANED_OBSERVATIONS_OUTPUT, REJECTED_OBSERVATIONS_OUTPUT,
    CATALOGED_OBJECTS_OUTPUT, HTML_DASHBOARD_OUTPUT, PROJECT_DISCLAIMER
)
from src.data_loader import DataLoader
from src.preprocessor import Preprocessor
from src.validator import DataValidator
from src.calibrator import Calibrator
from src.feature_extractor import FeatureExtractor
from src.visualizer import Visualizer
from src.exporter import DataExporter
from src.html_dashboard import HTMLDashboardGenerator

import pandas as pd


class AstronomyDashboardApp:
    """Main Tkinter Desktop Dashboard Application."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Astronomy Telescope Cataloging – Scientific Dashboard")
        self.root.geometry("1100x720")
        self.root.minsize(950, 600)

        # Style configurations
        self.style = ttk.Style()
        try:
            self.style.theme_use('vista' if 'vista' in self.style.theme_names() else 'clam')
        except Exception:
            pass

        # Data holders
        self.df_valid = pd.DataFrame()
        self.df_rejected = pd.DataFrame()
        self.df_objects = pd.DataFrame()
        self.val_summary = {}
        self.ana_summary = {}

        self._build_ui()
        self._load_initial_data()

    def _build_ui(self):
        """Constructs the desktop UI layout."""
        # Top Header Frame
        header_frame = tk.Frame(self.root, bg="#0f172a", pady=10, padx=16)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title_lbl = tk.Label(
            header_frame,
            text="🔭 Astronomy Telescope Cataloging System",
            font=("Segoe UI", 16, "bold"),
            fg="#38bdf8",
            bg="#0f172a"
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            header_frame,
            text="Observational Ingestion • Quality Control • Object Cataloging • Scientific Analytics",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#0f172a"
        )
        subtitle_lbl.pack(anchor="w")

        # Disclaimer banner
        disclaimer_frame = tk.Frame(self.root, bg="#fef3c7", pady=4, padx=12)
        disclaimer_frame.pack(side=tk.TOP, fill=tk.X)

        disc_lbl = tk.Label(
            disclaimer_frame,
            text="⚠️ Note: Synthetic illustrative dataset for educational cataloging demonstration; not real telescope measurements.",
            font=("Segoe UI", 8, "italic"),
            fg="#92400e",
            bg="#fef3c7"
        )
        disc_lbl.pack(anchor="w")

        # KPI Metric Cards Frame
        self.kpi_frame = tk.Frame(self.root, bg="#e2e8f0", pady=8, padx=12)
        self.kpi_frame.pack(side=tk.TOP, fill=tk.X)

        self.kpi_cards = {}
        cards_info = [
            ("ingested", "Total Ingested", "1,000", "#1e3a8a"),
            ("valid", "Processed Valid", "950 (95%)", "#166534"),
            ("rejected", "Rejected / Flagged", "50 (5%)", "#991b1b"),
            ("objects", "Cataloged Objects", "2,845", "#581c87"),
            ("telescopes", "Observatories", "5 Active", "#0e7490")
        ]

        for key, title, val, color in cards_info:
            card = tk.Frame(self.kpi_frame, bg="#ffffff", relief=tk.RIDGE, bd=1, padx=12, pady=6)
            card.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

            t_lbl = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#ffffff")
            t_lbl.pack(anchor="w")

            v_lbl = tk.Label(card, text=val, font=("Segoe UI", 13, "bold"), fg=color, bg="#ffffff")
            v_lbl.pack(anchor="w")
            self.kpi_cards[key] = v_lbl

        # Main Notebook (Tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=8)

        # Tab 1: Visual Analytics & Charts
        self.tab_charts = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_charts, text="📊 Analytics & Charts")
        self._build_charts_tab()

        # Tab 2: Valid Observations
        self.tab_valid = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_valid, text="🔭 Valid Observations (950)")
        self._build_valid_obs_tab()

        # Tab 3: Rejected / Flagged Records
        self.tab_rejected = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_rejected, text="⚠️ Rejected Records (50)")
        self._build_rejected_obs_tab()

        # Tab 4: Cataloged Objects
        self.tab_objects = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_objects, text="🌌 Celestial Objects (2,845)")
        self._build_objects_tab()

        # Tab 5: Pipeline Runner & Control
        self.tab_runner = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_runner, text="⚙️ Pipeline Controller")
        self._build_runner_tab()

        # Status Bar
        self.status_var = tk.StringVar(value="System Ready. Running on Windows 11.")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", font=("Segoe UI", 8), bg="#f1f5f9", fg="#475569")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------------- TAB 1: CHARTS ----------------
    def _build_charts_tab(self):
        ctrl_frame = ttk.Frame(self.tab_charts, padding=8)
        ctrl_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(ctrl_frame, text="Select Analytics Chart:", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=6)

        self.chart_var = tk.StringVar(value="Composite Analytics Dashboard (Figure 5.1)")
        chart_options = [
            "Composite Analytics Dashboard (Figure 5.1)",
            "Astronomical Object Distribution",
            "Observation Quality Distribution",
            "Brightness / Magnitude Distribution",
            "Monthly Observation Activity Trends"
        ]
        self.chart_cb = ttk.Combobox(ctrl_frame, textvariable=self.chart_var, values=chart_options, state="readonly", width=42)
        self.chart_cb.pack(side=tk.LEFT, padx=6)
        self.chart_cb.bind("<<ComboboxSelected>>", lambda e: self._display_selected_chart())

        ttk.Button(ctrl_frame, text="🔄 Refresh Charts", command=self._display_selected_chart).pack(side=tk.LEFT, padx=6)
        ttk.Button(ctrl_frame, text="🌐 Open HTML Dashboard in Browser", command=self._open_html_dashboard).pack(side=tk.RIGHT, padx=6)

        # Image display container with scroll
        self.chart_canvas = tk.Canvas(self.tab_charts, bg="#ffffff")
        self.chart_scroll_y = ttk.Scrollbar(self.tab_charts, orient=tk.VERTICAL, command=self.chart_canvas.yview)
        self.chart_scroll_x = ttk.Scrollbar(self.tab_charts, orient=tk.HORIZONTAL, command=self.chart_canvas.xview)
        self.chart_canvas.configure(xscrollcommand=self.chart_scroll_x.set, yscrollcommand=self.chart_scroll_y.set)

        self.chart_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.chart_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.chart_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.current_tk_img = None

    def _display_selected_chart(self):
        chart_map = {
            "Composite Analytics Dashboard (Figure 5.1)": CHARTS_DIR / "astronomy_analytics_dashboard.png",
            "Astronomical Object Distribution": CHARTS_DIR / "object_distribution.png",
            "Observation Quality Distribution": CHARTS_DIR / "observation_quality.png",
            "Brightness / Magnitude Distribution": CHARTS_DIR / "brightness_distribution.png",
            "Monthly Observation Activity Trends": CHARTS_DIR / "monthly_trends.png"
        }
        selected_file = chart_map.get(self.chart_var.get())

        self.chart_canvas.delete("all")
        if selected_file and selected_file.exists():
            try:
                # Load via PhotoImage
                self.current_tk_img = tk.PhotoImage(file=str(selected_file))
                self.chart_canvas.create_image(20, 20, anchor=tk.NW, image=self.current_tk_img)
                self.chart_canvas.config(scrollregion=(0, 0, self.current_tk_img.width() + 40, self.current_tk_img.height() + 40))
                self.status_var.set(f"Displaying: {selected_file.name}")
            except Exception as e:
                self.chart_canvas.create_text(200, 100, text=f"Unable to render image: {e}\n(Try running the pipeline first)", fill="#b91c1c", font=("Segoe UI", 10))
        else:
            self.chart_canvas.create_text(200, 100, text="Chart not yet generated. Please go to 'Pipeline Controller' and click 'Run Pipeline'.", fill="#475569", font=("Segoe UI", 10))

    # ---------------- TAB 2: VALID OBSERVATIONS ----------------
    def _build_valid_obs_tab(self):
        ctrl = ttk.Frame(self.tab_valid, padding=6)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(ctrl, text="Search Target/ID:").pack(side=tk.LEFT, padx=4)
        self.valid_search_var = tk.StringVar()
        self.valid_search_ent = ttk.Entry(ctrl, textvariable=self.valid_search_var, width=18)
        self.valid_search_ent.pack(side=tk.LEFT, padx=4)
        self.valid_search_var.trace_add("write", lambda *a: self._filter_valid_table())

        ttk.Label(ctrl, text="Filter Quality:").pack(side=tk.LEFT, padx=6)
        self.valid_quality_var = tk.StringVar(value="All")
        q_cb = ttk.Combobox(ctrl, textvariable=self.valid_quality_var, values=["All", "Good", "Acceptable"], state="readonly", width=12)
        q_cb.pack(side=tk.LEFT, padx=4)
        q_cb.bind("<<ComboboxSelected>>", lambda e: self._filter_valid_table())

        self.valid_count_lbl = ttk.Label(ctrl, text="Records: 0")
        self.valid_count_lbl.pack(side=tk.RIGHT, padx=6)

        # Treeview table
        cols = ("observation_id", "telescope_id", "observation_date", "target_name", "right_ascension", "declination", "exposure_time", "filter", "brightness", "calibrated_brightness", "quality_status")
        self.valid_tree = ttk.Treeview(self.tab_valid, columns=cols, show='headings', selectmode='browse')

        for c in cols:
            self.valid_tree.heading(c, text=c.replace('_', ' ').title())
            width = 110 if 'name' in c else 85
            self.valid_tree.column(c, width=width, anchor=tk.CENTER)

        v_scroll = ttk.Scrollbar(self.tab_valid, orient=tk.VERTICAL, command=self.valid_tree.yview)
        self.valid_tree.configure(yscrollcommand=v_scroll.set)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.valid_tree.pack(fill=tk.BOTH, expand=True)

    def _filter_valid_table(self):
        if self.df_valid.empty:
            return
        query = self.valid_search_var.get().lower().strip()
        quality = self.valid_quality_var.get()

        df_filtered = self.df_valid.copy()
        if quality != "All":
            df_filtered = df_filtered[df_filtered['quality_status'] == quality]

        if query:
            mask = (
                df_filtered['observation_id'].astype(str).str.lower().str.contains(query) |
                df_filtered['target_name'].astype(str).str.lower().str.contains(query) |
                df_filtered['telescope_id'].astype(str).str.lower().str.contains(query)
            )
            df_filtered = df_filtered[mask]

        self.valid_tree.delete(*self.valid_tree.get_children())
        cols = ("observation_id", "telescope_id", "observation_date", "target_name", "right_ascension", "declination", "exposure_time", "filter", "brightness", "calibrated_brightness", "quality_status")

        for _, row in df_filtered.head(500).iterrows():
            vals = [row.get(c, '') for c in cols]
            self.valid_tree.insert('', tk.END, values=vals)

        self.valid_count_lbl.config(text=f"Showing {len(df_filtered):,} of {len(self.df_valid):,} valid records")

    # ---------------- TAB 3: REJECTED RECORDS ----------------
    def _build_rejected_obs_tab(self):
        ctrl = ttk.Frame(self.tab_rejected, padding=6)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        lbl = ttk.Label(ctrl, text="Flagged / Rejected Observations (50 records identified by Quality Control):", font=("Segoe UI", 9, "bold"))
        lbl.pack(side=tk.LEFT, padx=4)

        self.rejected_count_lbl = ttk.Label(ctrl, text="Records: 0")
        self.rejected_count_lbl.pack(side=tk.RIGHT, padx=6)

        cols = ("observation_id", "telescope_id", "observation_date", "right_ascension", "declination", "exposure_time", "brightness", "quality_status", "rejection_reason")
        self.rejected_tree = ttk.Treeview(self.tab_rejected, columns=cols, show='headings', selectmode='browse')

        for c in cols:
            self.rejected_tree.heading(c, text=c.replace('_', ' ').title())
            if c == "rejection_reason":
                self.rejected_tree.column(c, width=320, anchor=tk.W)
            else:
                self.rejected_tree.column(c, width=90, anchor=tk.CENTER)

        r_scroll = ttk.Scrollbar(self.tab_rejected, orient=tk.VERTICAL, command=self.rejected_tree.yview)
        self.rejected_tree.configure(yscrollcommand=r_scroll.set)
        r_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.rejected_tree.pack(fill=tk.BOTH, expand=True)

    def _populate_rejected_table(self):
        self.rejected_tree.delete(*self.rejected_tree.get_children())
        if self.df_rejected.empty:
            return
        cols = ("observation_id", "telescope_id", "observation_date", "right_ascension", "declination", "exposure_time", "brightness", "quality_status", "rejection_reason")
        for _, row in self.df_rejected.iterrows():
            vals = [str(row.get(c, '')) for c in cols]
            self.rejected_tree.insert('', tk.END, values=vals)
        self.rejected_count_lbl.config(text=f"Total Rejected: {len(self.df_rejected):,}")

    # ---------------- TAB 4: OBJECTS ----------------
    def _build_objects_tab(self):
        ctrl = ttk.Frame(self.tab_objects, padding=6)
        ctrl.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(ctrl, text="Filter Object Type:").pack(side=tk.LEFT, padx=4)
        self.obj_type_var = tk.StringVar(value="All")
        o_cb = ttk.Combobox(ctrl, textvariable=self.obj_type_var, values=["All", "Star", "Galaxy", "Planet", "Other"], state="readonly", width=12)
        o_cb.pack(side=tk.LEFT, padx=4)
        o_cb.bind("<<ComboboxSelected>>", lambda e: self._filter_objects_table())

        self.obj_count_lbl = ttk.Label(ctrl, text="Objects: 0")
        self.obj_count_lbl.pack(side=tk.RIGHT, padx=6)

        cols = ("object_id", "observation_id", "object_type", "right_ascension", "declination", "apparent_magnitude", "estimated_size_arcsec", "description")
        self.obj_tree = ttk.Treeview(self.tab_objects, columns=cols, show='headings', selectmode='browse')

        for c in cols:
            self.obj_tree.heading(c, text=c.replace('_', ' ').title())
            if c == "description":
                self.obj_tree.column(c, width=220, anchor=tk.W)
            else:
                self.obj_tree.column(c, width=100, anchor=tk.CENTER)

        o_scroll = ttk.Scrollbar(self.tab_objects, orient=tk.VERTICAL, command=self.obj_tree.yview)
        self.obj_tree.configure(yscrollcommand=o_scroll.set)
        o_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.obj_tree.pack(fill=tk.BOTH, expand=True)

    def _filter_objects_table(self):
        if self.df_objects.empty:
            return
        o_type = self.obj_type_var.get()
        df_filtered = self.df_objects.copy()
        if o_type != "All":
            df_filtered = df_filtered[df_filtered['object_type'] == o_type]

        self.obj_tree.delete(*self.obj_tree.get_children())
        cols = ("object_id", "observation_id", "object_type", "right_ascension", "declination", "apparent_magnitude", "estimated_size_arcsec", "description")
        for _, row in df_filtered.head(600).iterrows():
            vals = [row.get(c, '') for c in cols]
            self.obj_tree.insert('', tk.END, values=vals)
        self.obj_count_lbl.config(text=f"Showing {len(df_filtered):,} of {len(self.df_objects):,} objects")

    # ---------------- TAB 5: PIPELINE CONTROLLER ----------------
    def _build_runner_tab(self):
        p_frame = ttk.Frame(self.tab_runner, padding=14)
        p_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(p_frame, text="Input Observation CSV Path:", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=4)
        self.input_path_var = tk.StringVar(value=str(DEFAULT_OBSERVATIONS_FILE))
        path_ent = ttk.Entry(p_frame, textvariable=self.input_path_var, width=65)
        path_ent.grid(row=0, column=1, padx=8, pady=4, sticky=tk.W)

        ttk.Button(p_frame, text="Browse...", command=self._browse_input_file).grid(row=0, column=2, padx=4)

        btn_box = ttk.Frame(p_frame)
        btn_box.grid(row=1, column=0, columnspan=3, pady=12, sticky=tk.W)

        self.run_btn = ttk.Button(btn_box, text="🚀 Execute Cataloging Pipeline", command=self._run_pipeline)
        self.run_btn.pack(side=tk.LEFT, padx=4)

        ttk.Button(btn_box, text="🌐 Open HTML Dashboard", command=self._open_html_dashboard).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_box, text="📁 Open Outputs Directory", command=self._open_outputs_dir).pack(side=tk.LEFT, padx=4)

        # Execution Log Text Box
        ttk.Label(self.tab_runner, text="Pipeline Execution Log:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=14)
        self.log_txt = tk.Text(self.tab_runner, height=18, font=("Consolas", 9), bg="#0f172a", fg="#e2e8f0", insertbackground="#ffffff")
        log_scroll = ttk.Scrollbar(self.tab_runner, command=self.log_txt.yview)
        self.log_txt.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 14), pady=(0, 14))
        self.log_txt.pack(fill=tk.BOTH, expand=True, padx=(14, 0), pady=(0, 14))

    def _browse_input_file(self):
        fn = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
        if fn:
            self.input_path_var.set(fn)

    def _log(self, text: str):
        self.log_txt.insert(tk.END, text + "\n")
        self.log_txt.see(tk.END)
        self.root.update_idletasks()

    def _run_pipeline(self):
        self.run_btn.config(state=tk.DISABLED)
        self.log_txt.delete("1.0", tk.END)
        self._log("=== STARTING ASTRONOMY OBSERVATION PIPELINE ===")
        self._log(f"Input file: {self.input_path_var.get()}")

        try:
            # 1. Ingestion
            self._log("[1/6] Ingesting observation dataset...")
            loader = DataLoader()
            df_raw = loader.load_observations(self.input_path_var.get())
            df_telescopes = loader.load_telescopes(DEFAULT_TELESCOPES_FILE)
            df_objects_raw = loader.load_objects(DEFAULT_OBJECTS_FILE)
            self._log(f"      Ingested {len(df_raw):,} observation rows successfully.")

            # 2. Preprocessing
            self._log("[2/6] Preprocessing: cleaning duplicates & whitespace...")
            preprocessor = Preprocessor()
            df_unique, df_dups = preprocessor.preprocess(df_raw)
            self._log(f"      Identified {len(df_dups)} duplicate records. Unique retained: {len(df_unique):,}")

            # 3. Validation & Quality Control
            self._log("[3/6] Quality Control: validating coordinates, exposure, and magnitude...")
            validator = DataValidator()
            df_all, df_valid, df_rejected = validator.validate_and_flag(df_unique, df_dups)
            val_sum = validator.validation_summary
            self._log(f"      Quality Results: Good={val_sum['good_count']} ({val_sum['good_percentage']}%), "
                      f"Acceptable={val_sum['acceptable_count']} ({val_sum['acceptable_percentage']}%), "
                      f"Rejected={val_sum['rejected_count']} ({val_sum['rejected_percentage']}%)")

            # 4. Calibration
            self._log("[4/6] Calibration: applying illustrative bias, dark, and flat-field corrections...")
            calibrator = Calibrator()
            df_valid_calibrated = calibrator.calibrate(df_valid)

            # 5. Feature Extraction
            self._log("[5/6] Feature Extraction: analyzing object categories and monthly trends...")
            extractor = FeatureExtractor()
            ana_sum = extractor.analyze_catalog(df_valid_calibrated, df_objects_raw, df_telescopes)

            # 6. Visualization & Exports
            self._log("[6/6] Generating Matplotlib charts and exporting deliverables...")
            viz = Visualizer()
            chart_paths = viz.generate_all_charts(val_sum, ana_sum, df_valid_calibrated, df_objects_raw)

            exporter = DataExporter()
            exp_paths = exporter.export_all(df_valid_calibrated, df_rejected, df_objects_raw, val_sum, ana_sum)

            html_gen = HTMLDashboardGenerator()
            html_path = html_gen.generate(val_sum, ana_sum)

            self._log("=== PIPELINE EXECUTION COMPLETED SUCCESSFULLY ===")
            self._log(f"Outputs written to: {OUTPUTS_DIR}")
            self._log(f"HTML Dashboard: {html_path}")

            # Update memory & tables
            self.df_valid = df_valid_calibrated
            self.df_rejected = df_rejected
            self.df_objects = df_objects_raw
            self.val_summary = val_sum
            self.ana_summary = ana_sum

            self._update_kpis()
            self._filter_valid_table()
            self._populate_rejected_table()
            self._filter_objects_table()
            self._display_selected_chart()

            self.status_var.set("Pipeline run finished successfully! Deliverables updated.")
            messagebox.showinfo("Success", "Astronomy Cataloging Pipeline finished successfully!\nAll charts, CSVs, and dashboards are ready.")

        except Exception as exc:
            self._log(f"[ERROR] Pipeline failed: {exc}")
            messagebox.showerror("Error", f"Pipeline encountered an error:\n{exc}")
        finally:
            self.run_btn.config(state=tk.NORMAL)

    def _load_initial_data(self):
        """Loads outputs if already existing, or runs initial pipeline."""
        if CLEANED_OBSERVATIONS_OUTPUT.exists() and REJECTED_OBSERVATIONS_OUTPUT.exists():
            try:
                self.df_valid = pd.read_csv(CLEANED_OBSERVATIONS_OUTPUT)
                self.df_rejected = pd.read_csv(REJECTED_OBSERVATIONS_OUTPUT)
                if CATALOGED_OBJECTS_OUTPUT.exists():
                    self.df_objects = pd.read_csv(CATALOGED_OBJECTS_OUTPUT)

                self._filter_valid_table()
                self._populate_rejected_table()
                self._filter_objects_table()
                self._display_selected_chart()
                self.status_var.set("Existing processed catalog loaded.")
                return
            except Exception:
                pass

        # If outputs not yet created, trigger pipeline run
        self._run_pipeline()

    def _update_kpis(self):
        """Refreshes top KPI card numbers."""
        if not self.val_summary:
            return
        self.kpi_cards["ingested"].config(text=f"{self.val_summary.get('total_records', 1000):,}")
        self.kpi_cards["valid"].config(text=f"{self.val_summary.get('valid_records', 950):,} ({self.val_summary.get('good_percentage', 72) + self.val_summary.get('acceptable_percentage', 23):.0f}%)")
        self.kpi_cards["rejected"].config(text=f"{self.val_summary.get('rejected_records', 50):,} ({self.val_summary.get('rejected_percentage', 5):.0f}%)")
        self.kpi_cards["objects"].config(text=f"{self.ana_summary.get('total_objects_cataloged', 2845):,}")

    def _open_html_dashboard(self):
        if HTML_DASHBOARD_OUTPUT.exists():
            webbrowser.open(HTML_DASHBOARD_OUTPUT.resolve().as_uri())
        else:
            messagebox.showwarning("Warning", "HTML dashboard not found. Run pipeline first.")

    def _open_outputs_dir(self):
        if OUTPUTS_DIR.exists():
            if sys.platform == "win32":
                os.startfile(OUTPUTS_DIR)
            else:
                webbrowser.open(OUTPUTS_DIR.resolve().as_uri())


def main():
    root = tk.Tk()
    app = AstronomyDashboardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
