"""
Visualization Module using Pandas and Matplotlib.
Generates publication-quality charts for:
1. Astronomical Object Distribution (Stars, Galaxies, Planets, Other)
2. Brightness / Magnitude Distribution
3. Observation Quality Breakdown (Good, Acceptable, Rejected)
4. Monthly Observation Activity Trends (M1 to M12)
5. Comprehensive Astronomy Analytics Dashboard (Composite 4-in-1 figure)

All charts explicitly include illustrative mock data disclosure notices.
"""

from pathlib import Path
from typing import Dict, Any, List
import matplotlib
matplotlib.use('Agg')  # Headless backend safe for scripts and servers
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.config import CHARTS_DIR


class Visualizer:
    """Creates astronomical analytical visualizations using Matplotlib and Pandas."""

    # Color palette inspired by deep-sky astronomy
    COLORS = {
        'star': '#f59e0b',        # Amber/Gold
        'galaxy': '#3b82f6',      # Deep Blue
        'planet': '#10b981',      # Emerald Green
        'other': '#8b5cf6',       # Violet
        'good': '#10b981',        # Green
        'acceptable': '#f59e0b',  # Amber
        'rejected': '#ef4444',    # Crimson
        'primary': '#1e3a8a',     # Navy
        'accent': '#0284c7',      # Light Blue
        'background': '#f8fafc',  # Off-white
        'text': '#0f172a'         # Dark Slate
    }

    def __init__(self, output_dir: Path | str = CHARTS_DIR):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _apply_theme(self, ax):
        """Applies consistent styling and subtle grid to axes."""
        ax.set_facecolor('#ffffff')
        ax.grid(True, linestyle='--', alpha=0.35, color='#94a3b8')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#cbd5e1')
        ax.spines['bottom'].set_color('#cbd5e1')

    def generate_all_charts(
        self,
        validation_summary: Dict[str, Any],
        analysis_summary: Dict[str, Any],
        df_valid: pd.DataFrame,
        df_objects: pd.DataFrame
    ) -> List[Path]:
        """Generates all 4 individual scientific charts plus the 4-panel dashboard."""
        saved_paths = []
        saved_paths.append(self.plot_object_distribution(analysis_summary))
        saved_paths.append(self.plot_brightness_distribution(df_valid, df_objects))
        saved_paths.append(self.plot_observation_quality(validation_summary))
        saved_paths.append(self.plot_monthly_trends(analysis_summary))
        saved_paths.append(self.plot_composite_dashboard(validation_summary, analysis_summary, df_valid, df_objects))
        return saved_paths

    def plot_object_distribution(self, analysis_summary: Dict[str, Any]) -> Path:
        """Chart 1: Astronomical Object Distribution (Bar & Donut chart)."""
        obj_dist = analysis_summary.get('object_distribution', {})
        categories = list(obj_dist.keys())
        counts = [obj_dist[c]['count'] for c in categories]
        percentages = [obj_dist[c]['percentage'] for c in categories]

        colors = [self.COLORS['star'], self.COLORS['galaxy'], self.COLORS['planet'], self.COLORS['other']]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), facecolor='#ffffff')

        # Subplot 1: Bar Chart
        self._apply_theme(ax1)
        bars = ax1.bar(categories, counts, color=colors, width=0.55, edgecolor='#334155', linewidth=0.8)
        ax1.set_title("Cataloged Objects Count by Type", fontsize=13, fontweight='bold', color=self.COLORS['text'], pad=12)
        ax1.set_ylabel("Number of Objects", fontsize=11, color=self.COLORS['text'])
        ax1.set_xlabel("Object Classification", fontsize=11, color=self.COLORS['text'])

        # Bar value labels
        for bar, count, pct in zip(bars, counts, percentages):
            height = bar.get_height()
            ax1.annotate(f"{count:,}\n({pct:.1f}%)",
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 4), textcoords="offset points",
                         ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1e293b')

        ax1.set_ylim(0, max(counts) * 1.18)

        # Subplot 2: Donut Chart
        wedges, texts, autotexts = ax2.pie(
            counts, labels=categories, autopct='%1.1f%%',
            startangle=140, colors=colors, pctdistance=0.75,
            wedgeprops=dict(width=0.45, edgecolor='#ffffff', linewidth=2)
        )
        for t in texts:
            t.set_fontsize(10.5)
            t.set_fontweight('normal')
        for at in autotexts:
            at.set_fontsize(10)
            at.set_color('#ffffff')
            at.set_fontweight('bold')

        ax2.set_title("Astronomical Object Share (%)", fontsize=13, fontweight='bold', color=self.COLORS['text'], pad=12)

        fig.suptitle(
            "Astronomical Object Type Distribution (Total: 2,845 Objects)\n[Illustrative Synthetic Catalog - For Educational Demonstration]",
            fontsize=13, fontweight='bold', y=1.02, color='#0f172a'
        )

        plt.tight_layout()
        out_path = self.output_dir / "object_distribution.png"
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return out_path

    def plot_brightness_distribution(self, df_valid: pd.DataFrame, df_objects: pd.DataFrame) -> Path:
        """Chart 2: Brightness / Apparent Magnitude Distribution."""
        fig, ax = plt.subplots(figsize=(10, 5.5), facecolor='#ffffff')
        self._apply_theme(ax)

        # Extract magnitudes
        if not df_objects.empty and 'apparent_magnitude' in df_objects.columns:
            mags = pd.to_numeric(df_objects['apparent_magnitude'], errors='coerce').dropna()
            label_text = "Cataloged Celestial Objects"
        else:
            mags = pd.to_numeric(df_valid.get('calibrated_brightness', df_valid['brightness']), errors='coerce').dropna()
            label_text = "Observation Field Brightness"

        # Histogram with KDE curve
        n, bins, patches = ax.hist(mags, bins=28, color='#0284c7', edgecolor='#0369a1', alpha=0.75, density=False)

        # Statistical reference lines
        mean_val = float(mags.mean())
        median_val = float(mags.median())

        ax.axvline(mean_val, color='#ef4444', linestyle='--', linewidth=2, label=f"Mean: {mean_val:.2f} mag")
        ax.axvline(median_val, color='#f59e0b', linestyle=':', linewidth=2, label=f"Median: {median_val:.2f} mag")

        ax.set_title("Brightness (Apparent Magnitude) Distribution\n[Illustrative Synthetic Dataset - For Educational Demonstration]",
                     fontsize=13, fontweight='bold', pad=14, color=self.COLORS['text'])
        ax.set_xlabel("Apparent Magnitude (m) [Higher values represent fainter objects]", fontsize=11, color=self.COLORS['text'])
        ax.set_ylabel("Number of Objects", fontsize=11, color=self.COLORS['text'])
        ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=10)

        plt.tight_layout()
        out_path = self.output_dir / "brightness_distribution.png"
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return out_path

    def plot_observation_quality(self, validation_summary: Dict[str, Any]) -> Path:
        """Chart 3: Observation Quality Breakdown (Good, Acceptable, Rejected)."""
        labels = ['Good Quality', 'Acceptable Quality', 'Rejected / Flagged']
        counts = [
            validation_summary.get('good_count', 720),
            validation_summary.get('acceptable_count', 230),
            validation_summary.get('rejected_count', 50)
        ]
        percentages = [
            validation_summary.get('good_percentage', 72.0),
            validation_summary.get('acceptable_percentage', 23.0),
            validation_summary.get('rejected_percentage', 5.0)
        ]
        colors = [self.COLORS['good'], self.COLORS['acceptable'], self.COLORS['rejected']]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), facecolor='#ffffff')

        # Subplot 1: Horizontal Bar Chart
        self._apply_theme(ax1)
        bars = ax1.barh(labels, counts, color=colors, height=0.5, edgecolor='#334155', linewidth=0.8)
        ax1.set_title("Observations by Quality Category", fontsize=13, fontweight='bold', color=self.COLORS['text'], pad=12)
        ax1.set_xlabel("Number of Records", fontsize=11, color=self.COLORS['text'])
        ax1.invert_yaxis()  # Good on top

        for bar, count, pct in zip(bars, counts, percentages):
            w = bar.get_width()
            ax1.annotate(f" {count:,} ({pct:.1f}%)",
                         xy=(w, bar.get_y() + bar.get_height() / 2),
                         va='center', fontsize=10, fontweight='bold', color='#1e293b')

        ax1.set_xlim(0, max(counts) * 1.25)

        # Subplot 2: Donut Chart
        wedges, texts, autotexts = ax2.pie(
            counts, labels=labels, autopct='%1.1f%%',
            startangle=140, colors=colors, pctdistance=0.75,
            wedgeprops=dict(width=0.45, edgecolor='#ffffff', linewidth=2)
        )
        for t in texts:
            t.set_fontsize(10.5)
            t.set_fontweight('normal')
        for at in autotexts:
            at.set_fontsize(10)
            at.set_color('#ffffff')
            at.set_fontweight('bold')

        ax2.set_title("Quality Proportion (Total: 1,000 Records)", fontsize=13, fontweight='bold', color=self.COLORS['text'], pad=12)

        fig.suptitle(
            "Observation Quality Control Distribution (Table 6.2)\n[Illustrative Synthetic Dataset - For Educational Demonstration]",
            fontsize=13, fontweight='bold', y=1.02, color='#0f172a'
        )

        plt.tight_layout()
        out_path = self.output_dir / "observation_quality.png"
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return out_path

    def plot_monthly_trends(self, analysis_summary: Dict[str, Any]) -> Path:
        """Chart 4: Monthly Observation Trends (M1 to M12)."""
        monthly = analysis_summary.get('monthly_trends', {})
        months = [f"M{m}" for m in range(1, 13)]
        counts = [monthly.get(m, {}).get('observations', 0) for m in months]
        labels = [f"M{m}\n({monthly.get(f'M{m}', {}).get('month_name', '')[:3]})" for m in range(1, 13)]

        fig, ax = plt.subplots(figsize=(12, 5.5), facecolor='#ffffff')
        self._apply_theme(ax)

        bars = ax.bar(months, counts, color='#1e3a8a', width=0.6, edgecolor='#0f172a', linewidth=0.8, label="Monthly Observations")

        # Trend line overlay
        ax.plot(months, counts, color='#f59e0b', marker='o', linewidth=2.5, markersize=7, label="Activity Trend Curve")

        ax.set_title("Monthly Astronomical Observation Activity Trend (12 Months)\n[Illustrative Synthetic Dataset - For Educational Demonstration]",
                     fontsize=13, fontweight='bold', pad=14, color=self.COLORS['text'])
        ax.set_xlabel("Observation Month (M1 to M12)", fontsize=11, color=self.COLORS['text'])
        ax.set_ylabel("Number of Valid Observations", fontsize=11, color=self.COLORS['text'])
        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(labels, fontsize=9.5)

        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.annotate(f"{count}",
                         xy=(bar.get_x() + bar.get_width() / 2, height),
                         xytext=(0, 4), textcoords="offset points",
                         ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1e293b')

        ax.set_ylim(0, max(counts) * 1.18)
        ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=10)

        plt.tight_layout()
        out_path = self.output_dir / "monthly_trends.png"
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return out_path

    def plot_composite_dashboard(
        self,
        validation_summary: Dict[str, Any],
        analysis_summary: Dict[str, Any],
        df_valid: pd.DataFrame,
        df_objects: pd.DataFrame
    ) -> Path:
        """Chart 5: Master 4-panel Astronomy Analytics Dashboard (Figure 5.1 in report)."""
        fig = plt.figure(figsize=(16, 12), facecolor='#f8fafc')

        # 2x2 Grid of subplots
        gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.25)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])

        # Panel 1: Object Distribution
        self._apply_theme(ax1)
        obj_dist = analysis_summary.get('object_distribution', {})
        cat_labels = list(obj_dist.keys())
        cat_counts = [obj_dist[c]['count'] for c in cat_labels]
        obj_colors = [self.COLORS['star'], self.COLORS['galaxy'], self.COLORS['planet'], self.COLORS['other']]
        bars1 = ax1.bar(cat_labels, cat_counts, color=obj_colors, width=0.55, edgecolor='#334155')
        ax1.set_title("(A) Astronomical Object Distribution (2,845 Objects)", fontsize=11.5, fontweight='bold', pad=8)
        ax1.set_ylabel("Count", fontsize=10)
        for b, c in zip(bars1, cat_counts):
            ax1.annotate(f"{c:,}", xy=(b.get_x() + b.get_width()/2, b.get_height()), xytext=(0, 3),
                         textcoords="offset points", ha='center', fontsize=9, fontweight='bold')
        ax1.set_ylim(0, max(cat_counts) * 1.18)

        # Panel 2: Quality Distribution
        self._apply_theme(ax2)
        q_labels = ['Good (72%)', 'Acceptable (23%)', 'Rejected (5%)']
        q_counts = [validation_summary.get('good_count', 720),
                    validation_summary.get('acceptable_count', 230),
                    validation_summary.get('rejected_count', 50)]
        q_colors = [self.COLORS['good'], self.COLORS['acceptable'], self.COLORS['rejected']]
        ax2.pie(q_counts, labels=q_labels, autopct='%1.1f%%', startangle=140, colors=q_colors,
                wedgeprops=dict(width=0.45, edgecolor='#ffffff', linewidth=2))
        ax2.set_title("(B) Observation Quality Status (1,000 Records)", fontsize=11.5, fontweight='bold', pad=8)

        # Panel 3: Brightness Distribution
        self._apply_theme(ax3)
        if not df_objects.empty and 'apparent_magnitude' in df_objects.columns:
            mags = pd.to_numeric(df_objects['apparent_magnitude'], errors='coerce').dropna()
        else:
            mags = pd.to_numeric(df_valid['brightness'], errors='coerce').dropna()
        ax3.hist(mags, bins=25, color='#0284c7', edgecolor='#0369a1', alpha=0.8)
        ax3.axvline(float(mags.mean()), color='#ef4444', linestyle='--', label=f"Mean: {mags.mean():.2f} mag")
        ax3.set_title("(C) Apparent Magnitude Distribution", fontsize=11.5, fontweight='bold', pad=8)
        ax3.set_xlabel("Apparent Magnitude (m)", fontsize=10)
        ax3.set_ylabel("Frequency", fontsize=10)
        ax3.legend(fontsize=9)

        # Panel 4: Monthly Observation Trends
        self._apply_theme(ax4)
        monthly = analysis_summary.get('monthly_trends', {})
        m_keys = [f"M{m}" for m in range(1, 13)]
        m_vals = [monthly.get(m, {}).get('observations', 0) for m in m_keys]
        ax4.bar(m_keys, m_vals, color='#1e3a8a', width=0.6, edgecolor='#0f172a')
        ax4.plot(m_keys, m_vals, color='#f59e0b', marker='o', linewidth=2)
        ax4.set_title("(D) Monthly Observing Trend (12 Months)", fontsize=11.5, fontweight='bold', pad=8)
        ax4.set_xlabel("Month", fontsize=10)
        ax4.set_ylabel("Valid Observations", fontsize=10)

        fig.suptitle(
            "Astronomy Telescope Cataloging – Analytics Dashboard (Figure 5.1)\n[Illustrative Synthetic Dataset - For Educational Demonstration]",
            fontsize=15, fontweight='bold', color='#0f172a', y=0.98
        )

        out_path = self.output_dir / "astronomy_analytics_dashboard.png"
        fig.savefig(out_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        return out_path
