import streamlit as st
import pandas as pd
from io import StringIO

# --- sample data (your November example) ---
DATA_CSV = """date,cost,conversions
11/1/2025,403,46
11/2/2025,431,46
11/3/2025,263,97
11/4/2025,311,87
11/5/2025,548,97
11/6/2025,371,76
11/7/2025,445,90
11/8/2025,729,20
11/9/2025,948,65
11/10/2025,796,83
11/11/2025,646,35
11/12/2025,789,69
11/13/2025,182,14
11/14/2025,955,25
11/15/2025,251,69
11/16/2025,669,16
11/17/2025,523,17
11/18/2025,608,12
11/19/2025,463,53
11/20/2025,629,75
11/21/2025,967,96
11/22/2025,139,58
11/23/2025,171,79
11/24/2025,885,80
11/25/2025,554,92
11/26/2025,520,21
11/27/2025,301,72
11/28/2025,721,15
11/29/2025,908,22
11/30/2025,579,38
"""

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(StringIO(DATA_CSV), parse_dates=["date"])
    return df

def build_summary(df: pd.DataFrame, start_date, end_date, target_cpa: float) -> pd.DataFrame:
    mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
    df_range = df.loc[mask]

    total_cost = df_range["cost"].sum()
    total_conv = df_range["conversions"].sum()

    actual_cpa = total_cost / total_conv if total_conv > 0 else None

    row = {
        "Start Date": start_date,
        "End Date": end_date,
        "Total Cost": total_cost,
        "Total Conversions": total_conv,
        "Target CPA": target_cpa,
        "Actual CPA": actual_cpa,
        "CPA Delta (Actual - Target)": None,
        "% Over/Under Target": None,
    }

    if actual_cpa is not None and target_cpa > 0:
        delta = actual_cpa - target_cpa
        pct_over = (delta / target_cpa) * 100
        row["CPA Delta (Actual - Target)"] = delta
        row["% Over/Under Target"] = pct_over

    return pd.DataFrame([row])

def main():
    st.set_page_config(page_title="CPA Summary", layout="centered")
    st.title("🧮 Simple CPA Summary (Demo)")
    st.caption("Uses sample Date / Cost / Conversions data and compares actual CPA vs target.")

    df = load_data()

    # Target CPA input
    target_cpa = st.number_input(
        "Target CPA",
        min_value=0.0,
        value=100.0,
        step=1.0,
        help="Your target cost per acquisition.",
    )

    # Date range picker (default: min→max of data)
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()
    start_date, end_date = st.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    # Button to run summary
    if st.button("Run CPA Summary ✅"):
        summary_df = build_summary(df, start_date, end_date, target_cpa)
        st.write("### Summary")
        st.dataframe(summary_df, use_container_width=True)

        st.write("### Underlying data (filtered)")
        mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
        st.dataframe(df.loc[mask], use_container_width=True)

if __name__ == "__main__":
    main()