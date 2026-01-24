"""
================================================================================
Script: 2.3_Report.py
ID: 2.3
Description: Generates an HTML Verification Report consolidating execution stats,
             vagueness metrics, and data samples.
Inputs:
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/*.parquet
    - config/project.yaml
Outputs:
    - 4_Outputs/2.3_Report/YYYY-MM-DD_HHMMSS/report.html
    - 4_Outputs/2.3_Report/latest/
Deterministic: true
================================================================================
"""

import os
import sys
import yaml
import logging
import pandas as pd
import glob
import datetime
import shutil
import plotly.express as px
import plotly.io as pio
from jinja2 import Template
from pathlib import Path

# Add script directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from shared.symlink_utils import update_latest_link
from shared.observability_utils import DualWriter


def setup_logging(output_dir):
    log_dir = os.path.join("3_Logs", "2.3_Report")
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{timestamp}.log")

    # redirect stdout/stderr to dual writer
    sys.stdout = DualWriter(log_file)
    sys.stderr = sys.stdout  # Redirect stderr to same dual writer

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return log_file


def main():
    # 1. Load Config
    config_path = "config/project.yaml"
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # 2. Setup Output
    step_id = "2.3_Report"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = os.path.join(config["paths"]["outputs"], step_id, timestamp)
    os.makedirs(output_dir, exist_ok=True)

    setup_logging(output_dir)
    logging.info(f"Starting {step_id} - Verification Report Generation")
    logging.info(f"Output Directory: {output_dir}")

    # 3. Find Input Data (Step 2.2 Variables)
    input_base = os.path.join(
        config["paths"]["outputs"], "2_Textual_Analysis", "2.2_Variables", "latest"
    )
    parquet_files = glob.glob(os.path.join(input_base, "*.parquet"))

    if not parquet_files:
        logging.error(f"No parquet files found in {input_base}")
        # Try checking if there is no 'latest' link but there are timestamped folders
        parent_dir = os.path.join(
            config["paths"]["outputs"], "2_Textual_Analysis", "2.2_Variables"
        )
        if os.path.exists(parent_dir):
            subdirs = sorted(
                [
                    d
                    for d in os.listdir(parent_dir)
                    if os.path.isdir(os.path.join(parent_dir, d)) and d != "latest"
                ]
            )
            if subdirs:
                fallback_dir = os.path.join(parent_dir, subdirs[-1])
                logging.info(f"Falling back to most recent directory: {fallback_dir}")
                parquet_files = glob.glob(os.path.join(fallback_dir, "*.parquet"))

    if not parquet_files:
        logging.error("Could not find any input parquet files. Aborting.")
        sys.exit(1)

    logging.info(f"Found {len(parquet_files)} parquet files.")

    # 4. Load Data
    try:
        df_list = []
        for f in parquet_files:
            logging.info(f"Reading {os.path.basename(f)}...")
            df_list.append(pd.read_parquet(f))

        df = pd.concat(df_list, ignore_index=True)
        logging.info(f"Successfully loaded {len(df)} rows.")
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        sys.exit(1)

    # 5. Analyze Data
    # Key metric: Manager_QA_Uncertainty_pct (as per F1D focus on clarity)
    target_col = "Manager_QA_Uncertainty_pct"
    if target_col not in df.columns:
        logging.warning(f"'{target_col}' not found. Searching for alternative...")
        numeric_cols = df.select_dtypes(include=["float", "int"]).columns
        # Try to find something similar
        alternatives = [c for c in numeric_cols if "Uncertainty" in c]
        if alternatives:
            target_col = alternatives[0]
        elif len(numeric_cols) > 0:
            target_col = numeric_cols[0]
        else:
            logging.error("No numeric columns found for analysis.")
            sys.exit(1)

    logging.info(f"Using target column for analysis: {target_col}")

    stats = df[target_col].describe().to_dict()
    logging.info(f"Calculated statistics for {target_col}")

    # 6. Generate Plots
    try:
        logging.info("Generating distribution plot...")
        # Use a simpler theme for compatibility
        fig = px.histogram(
            df,
            x=target_col,
            title=f"Distribution of {target_col}",
            nbins=50,
            template="plotly_white",
            labels={target_col: target_col.replace("_", " ")},
        )
        fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
        plot_html = pio.to_html(fig, full_html=False, include_plotlyjs="cdn")
    except Exception as e:
        logging.error(f"Plot generation failed: {e}")
        plot_html = f"<div class='alert alert-danger'>Plot generation failed: {e}</div>"

    # 7. Generate Tables
    # Ensure we have identification columns
    id_cols = ["file_name", "conm", "start_date", "gvkey"]
    cols_to_show = [c for c in id_cols if c in df.columns] + [target_col]

    top_clarity = df.nsmallest(10, target_col)[cols_to_show]
    bottom_clarity = df.nlargest(10, target_col)[cols_to_show]

    # 8. Render HTML
    template_str = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>F1D Clarity Verification Report</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding: 20px; background-color: #f8f9fa; }
            .container { background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .section { margin-bottom: 40px; }
            h1 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
            h3 { color: #34495e; margin-top: 20px; }
            .metric-card { background: #f1f3f5; padding: 15px; border-radius: 5px; margin-bottom: 10px; }
            .metric-val { font-size: 1.2em; font-weight: bold; }
            table { font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1 class="mb-4">F1D Clarity Verification Report</h1>
            
            <div class="section">
                <h3>Execution Summary</h3>
                <div class="row">
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div>Timestamp</div>
                            <div class="metric-val">{{ timestamp }}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div>Rows Processed</div>
                            <div class="metric-val">{{ rows }}</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="metric-card">
                            <div>Metric Analyzed</div>
                            <div class="metric-val" style="font-size: 1em; overflow-wrap: break-word;">{{ target_col }}</div>
                        </div>
                    </div>
                </div>
                <div class="mt-2 text-muted small">Input Source: {{ input_source }}</div>
            </div>

            <div class="section">
                <h3>Vagueness Distribution</h3>
                <div class="row">
                    <div class="col-md-8">
                        {{ plot_html | safe }}
                    </div>
                    <div class="col-md-4">
                        <div class="card">
                            <div class="card-header">Statistics</div>
                            <div class="card-body p-0">
                                <table class="table table-sm table-striped mb-0">
                                    <tbody>
                                        {% for k, v in stats.items() %}
                                        <tr>
                                            <td>{{ k|title }}</td>
                                            <td class="text-end">{{ "%.4f"|format(v) }}</td>
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h3>Top 10 Clearest (Lowest Uncertainty)</h3>
                <p class="text-muted">These companies have the lowest <code>{{ target_col }}</code> scores.</p>
                <div class="table-responsive">
                    {{ top_table | safe }}
                </div>
            </div>

            <div class="section">
                <h3>Top 10 Least Clear (Highest Uncertainty)</h3>
                <p class="text-muted">These companies have the highest <code>{{ target_col }}</code> scores.</p>
                <div class="table-responsive">
                    {{ bottom_table | safe }}
                </div>
            </div>
            
            <footer class="text-center text-muted small mt-5">
                Generated by 2_Scripts/2.3_Report.py | F1D Project
            </footer>
        </div>
    </body>
    </html>
    """

    try:
        logging.info("Rendering HTML template...")
        template = Template(template_str)
        html_content = template.render(
            timestamp=timestamp,
            rows=len(df),
            input_source=input_base,
            target_col=target_col,
            plot_html=plot_html,
            stats=stats,
            top_table=top_clarity.to_html(
                classes="table table-striped table-hover", index=False
            ),
            bottom_table=bottom_clarity.to_html(
                classes="table table-striped table-hover", index=False
            ),
        )

        output_file = os.path.join(output_dir, "report.html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logging.info(f"Report generated successfully at {output_file}")
    except Exception as e:
        logging.error(f"HTML generation failed: {e}")
        sys.exit(1)

    # Update latest symlink
    try:
        latest_link = Path(config["paths"]["outputs"]) / step_id / "latest"
        update_latest_link(Path(output_dir), latest_link)
        logging.info(f"Updated latest link: {latest_link}")
    except Exception as e:
        logging.warning(f"Failed to update latest link: {e}")

    logging.info("Execution complete.")


if __name__ == "__main__":
    main()
