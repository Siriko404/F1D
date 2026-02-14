#!/usr/bin/env python3
"""
================================================================================
Script: 2.3_Report.py
ID: 2.3
Description: Generates an HTML Verification Report consolidating execution stats,
             vagueness metrics, and data samples.
Inputs:
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/<timestamp>/*.parquet (resolved via get_latest_output_dir)
    - config/project.yaml
Outputs:
    - 4_Outputs/2.3_Report/YYYY-MM-DD_HHMMSS/report.html
Deterministic: true
Dependencies:
    - Requires: Step 2.2
    - Uses: pandas, markdown

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import argparse
import datetime
import glob
import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio
import yaml
from jinja2 import Template

from f1d.shared.logging import configure_script_logging, get_logger

# Add script directory to path to import shared modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from shared.observability_utils import DualWriter
from shared.path_utils import get_latest_output_dir


def parse_arguments():
    """Parse command-line arguments for 2.3_Report.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 2.3: Generate Verification Report

Generates an HTML verification report consolidating execution stats,
vagueness metrics, and data samples from Step 2.2 output.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(root):
    """Validate all required inputs and prerequisite steps exist."""
    from shared.dependency_checker import validate_prerequisites

    required_files = {}

    # Validate Step 2.2 output exists (uses timestamp-based resolution internally)
    required_steps = {
        "2.2_ConstructVariables": "linguistic_variables.parquet",
    }

    validate_prerequisites(required_files, required_steps)


def setup_logging(output_dir):
    log_dir = os.path.join("3_Logs", "2.3_Report")
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_file = os.path.join(log_dir, f"{timestamp}.log")

    # redirect stdout/stderr to dual writer
    sys.stdout = DualWriter(log_file)
    sys.stderr = sys.stdout  # Redirect stderr to same dual writer

    # Configure structured logging
    configure_script_logging(script_name="2.3_Report", log_level="INFO")
    return log_file


def main():
    # Configure logging first
    logger = get_logger(__name__)

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
    logger.info("starting_report_generation", step_id=step_id, output_dir=output_dir)

    # 3. Find Input Data (Step 2.2 Variables) using timestamp-based resolution
    variables_base = (
        Path(config["paths"]["outputs"]) / "2_Textual_Analysis" / "2.2_Variables"
    )
    input_base = str(variables_base)  # Default for error reporting
    try:
        input_dir = get_latest_output_dir(
            variables_base,
            required_file="linguistic_variables_2002.parquet",
        )
        input_base = str(input_dir)
        parquet_files = glob.glob(os.path.join(input_base, "*.parquet"))
    except FileNotFoundError as e:
        logger.error("no_valid_output_directory", error=str(e))
        parquet_files = []

    if not parquet_files:
        logger.error("no_input_parquet_files")
        sys.exit(1)

    logger.info("found_parquet_files", count=len(parquet_files))

    # 4. Load Data
    try:
        df_list = []
        for f in parquet_files:
            logger.info("reading_parquet_file", file=os.path.basename(f))
            df_list.append(pd.read_parquet(f))

        df = pd.concat(df_list, ignore_index=True)
        logger.info("data_loaded_successfully", rows=len(df))
    except Exception as e:
        logger.error("failed_to_load_data", error=str(e))
        sys.exit(1)

    # 5. Analyze Data
    # Key metric: Manager_QA_Uncertainty_pct (as per F1D focus on clarity)
    target_col = "Manager_QA_Uncertainty_pct"
    if target_col not in df.columns:
        logger.warning("target_column_not_found", column=target_col)
        numeric_cols = df.select_dtypes(include=["float", "int"]).columns
        # Try to find something similar
        alternatives = [c for c in numeric_cols if "Uncertainty" in c]
        if alternatives:
            target_col = alternatives[0]
        elif len(numeric_cols) > 0:
            target_col = numeric_cols[0]
        else:
            logger.error("no_numeric_columns_found")
            sys.exit(1)

    logger.info("using_target_column", column=target_col)

    stats = df[target_col].describe().to_dict()
    logger.info("calculated_statistics", column=target_col)

    # 6. Generate Plots
    try:
        logger.info("generating_distribution_plot")
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
        logger.error("plot_generation_failed", error=str(e))
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
        logger.info("rendering_html_template")
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

        logger.info("report_generated_successfully", output_file=output_file)
    except Exception as e:
        logger.error("html_generation_failed", error=str(e))
        sys.exit(1)

    logger.info("execution_complete")


if __name__ == "__main__":
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        print("All prerequisites validated")
        sys.exit(0)

    check_prerequisites(root)
    main()
