"""
Generates tiny synthetic input files for the F1D pipeline E2E tests.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import zipfile


def generate_synthetic_inputs(root_dir: Path):
    inputs_dir = root_dir / "inputs"
    inputs_dir.mkdir(parents=True, exist_ok=True)

    # 1. Earnings Calls (Unified-info.parquet)
    ec_dir = inputs_dir / "Earnings_Calls_Transcripts"
    ec_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "file_name": ["1000000_T", "1000001_T", "2000000_T"],
            "date": pd.to_datetime(["2010-01-15", "2011-01-15", "2010-02-15"]),
            "company_name": ["Corp A", "Corp A", "Corp B"],
            "company_ticker": ["A", "A", "B"],
            "event_type": ["Earnings", "Earnings", "Earnings"],
        }
    ).to_parquet(ec_dir / "Unified-info.parquet")

    # 2. Execucomp
    ex_dir = inputs_dir / "Execucomp"
    ex_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "gvkey": ["001000", "001000", "002000"],
            "exec_fullname": ["Jane Doe", "Jane Doe", "John Smith"],
            "execid": ["E1", "E1", "E2"],
            "becameceo": pd.to_datetime(["2009-01-01", "2009-01-01", "2009-01-01"]),
            "leftofc": pd.to_datetime([None, None, None]),
            "ceoann": ["CEO", "CEO", "CEO"],
            "year": [2010, 2011, 2010],
        }
    ).to_parquet(ex_dir / "comp_execucomp.parquet")

    # 3. CCM
    ccm_dir = inputs_dir / "CRSPCompustat_CCM"
    ccm_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "gvkey": ["001000", "002000"],
            "LPERMNO": [10000, 20000],
            "LINKDT": pd.to_datetime(["2000-01-01", "2000-01-01"]),
            "LINKENDDT": ["E", "E"],
            "LINKTYPE": ["LU", "LU"],
            "LINKPRIM": ["P", "P"],
        }
    ).to_parquet(ccm_dir / "CRSPCompustat_CCM.parquet")

    # 4. Compustat
    comp_dir = inputs_dir / "comp_na_daily_all"
    comp_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "gvkey": ["001000", "001000", "002000"],
            "datadate": pd.to_datetime(["2010-12-31", "2011-12-31", "2010-12-31"]),
            "fyearq": [2010, 2011, 2010],
            "fqtr": [4, 4, 4],
            "sic": [1000, 1000, 2000],
            "atq": [100.0, 110.0, 200.0],
            "ceqq": [50.0, 55.0, 100.0],
            "cshoq": [10.0, 10.0, 20.0],
            "prccq": [15.0, 16.0, 25.0],
            "ltq": [50.0, 55.0, 100.0],
            "niq": [5.0, 6.0, 10.0],
            "epspxq": [0.5, 0.6, 0.5],
            "actq": [20.0, 22.0, 40.0],
            "lctq": [10.0, 11.0, 20.0],
            "xrdq": [1.0, 1.1, 2.0],
            "cheq": [5.0, 5.5, 10.0],
            "capxy": [2.0, 2.2, 4.0],
            "dvy": [1.0, 1.1, 2.0],
            "oancfy": [10.0, 11.0, 20.0],
            "saley": [50.0, 55.0, 100.0],
            "saleq": [12.0, 13.0, 25.0],
            "xrdy": [4.0, 4.4, 8.0],
            "aqcy": [0.0, 0.0, 0.0],
            "sppey": [0.0, 0.0, 0.0],
            "dvpspq": [0.1, 0.11, 0.1],
            "req": [10.0, 11.0, 20.0],
            "seqq": [50.0, 55.0, 100.0],
        }
    ).to_parquet(comp_dir / "comp_na_daily_all.parquet")

    # 5. IBES
    ibes_dir = inputs_dir / "tr_ibes"
    ibes_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "TICKER": ["A", "A", "B"],
            "STATPERS": pd.to_datetime(["2010-01-14", "2011-01-14", "2010-02-14"]),
            "MEASURE": ["EPS", "EPS", "EPS"],
            "FISCALP": ["QTR", "QTR", "QTR"],
            "MEANEST": [0.5, 0.6, 0.5],
            "STDEV": [0.05, 0.06, 0.05],
            "NUMEST": [5, 6, 5],
            "ACTUAL": [0.51, 0.61, 0.49],
        }
    ).to_parquet(ibes_dir / "tr_ibes.parquet")

    # 6. SDC
    sdc_dir = inputs_dir / "SDC"
    sdc_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "Target_Cusip": ["A", "B"],
            "Date_Announced": pd.to_datetime(["2015-01-01", "2015-01-01"]),
            "Deal_Status": ["Completed", "Withdrawn"],
            "Deal_Attitude": ["Friendly", "Hostile"],
        }
    ).to_parquet(sdc_dir / "sdc-ma-merged.parquet")

    # 7. CRSP DSF
    crsp_dir = inputs_dir / "CRSP_DSF"
    crsp_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "PERMNO": [10000] * 20 + [20000] * 20,
            "DATE": pd.date_range("2010-01-01", periods=20).tolist()
            + pd.date_range("2010-01-01", periods=20).tolist(),
            "RET": [0.01] * 40,
            "VWRETD": [0.01] * 40,
            "PRC": [15.0] * 40,
            "VOL": [1000] * 40,
            "ASKHI": [15.1] * 40,
            "BIDLO": [14.9] * 40,
        }
    ).to_parquet(crsp_dir / "CRSP_DSF_2010_Q1.parquet")

    # 8. FirmLevelRisk
    risk_dir = inputs_dir / "FirmLevelRisk"
    risk_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "gvkey": ["001000", "002000"],
            "date": ["2010q4", "2010q4"],
            "PRisk": [1.5, 2.0],
        }
    ).to_csv(risk_dir / "firmquarter_2022q1.csv", index=False)

    # 9. CCCL Instrument
    cccl_dir = inputs_dir / "CCCL_instrument"
    cccl_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(
        {
            "year": [2010, 2010],
            "ff48": [1000, 2000],
            "shift_intensity_mkvalt": [0.5, 0.6],
        }
    ).to_parquet(cccl_dir / "instrument_shift_intensity_2005_2022.parquet")

    # 10. FF12 and FF48 zips
    ff_dir = inputs_dir / "FF1248"
    ff_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ff_dir / "Siccodes12.zip", "w") as z:
        z.writestr("Siccodes12.txt", "1 NoDur  Consumer Nondurables\n  0100-0999\n")
    with zipfile.ZipFile(ff_dir / "Siccodes48.zip", "w") as z:
        z.writestr("Siccodes48.txt", "1 Agric  Agriculture\n  0100-0999\n")

    # 11. LM Dictionary
    lm_dir = inputs_dir / "Loughran-McDonald_MasterDictionary_1993-2024.csv"
    pd.DataFrame(
        {
            "Word": ["GOOD", "BAD", "MAYBE"],
            "Negative": [0, 2009, 0],
            "Positive": [2009, 0, 0],
            "Uncertainty": [0, 0, 2009],
            "Litigious": [0, 0, 0],
            "Strong_Modal": [0, 0, 0],
            "Weak_Modal": [0, 0, 2009],
            "Constraining": [0, 0, 0],
        }
    ).to_csv(lm_dir, index=False)


if __name__ == "__main__":
    import sys

    generate_synthetic_inputs(Path(sys.argv[1]))
