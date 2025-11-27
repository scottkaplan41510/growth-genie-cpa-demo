import streamlit as st
import pandas as pd
import altair as alt
from datetime import date

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="SRG – Simple CPA Summary",
    page_icon="📈",
    layout="wide",
)

# -------------------------
# Sample data loader
# (You can swap this later for Google Sheets)
# -------------------------
def load_data() -> pd.DataFrame:
    data = {
        "date": [
            "2025-11-01","2025-11-02","2025-11-03","2025-11-04","2025-11-05",
            "2025-11-06","2025-11-07","2025-11-08","2025-11-09","2025-11-10",
            "2025-11-11","2025-11-12","2025-11-13","2025-11-14","2025-11-15",
            "2025-11-16","2025-11-17","2025-11-18","2025-11-19","2025-11-20",
            "2025-11-21","2025-11-22","2025-11-23","2025-11-24","2025-11-25",
            "2025-11-26","2025-11-27","2025-11-28","2025-11-29","2025-11-30",
        ],
        "cost": [
            403,431,263,311,548,
            371,445,729,948,796,
            646,789,182,955,251,
            669,523,608,463,629,
            967,139,171,885,554,
            520,301,721,908,579,
        ],
        "conversions": [
            46,46,97,87,97,
            76,90,20,65,83,
            35,69,14,25,69,
            16,17,12,53,75,
            96,58,79,80,92,
            21,72,15,22,38,
        ],
    }
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])
    return df


# -------------------------
# Core summary logic
# -------------------------
def build_summary(
    df: pd.DataFrame, start: date, end: date, target_cpa: float
) -> tuple[pd.DataFrame, pd.DataFrame]:

    mask = (df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))
    df_filtered = df.loc[mask].copy()

    total_cost = df_filtered["cost"].sum()
    total_conversions = df_filtered["conversions"].sum()
    actual_cpa = total_cost / total_conversions if total_conversions > 0 else 0.0

    cpa_delta = actual_cpa - target_cpa
    over_under_pct = (cpa_delta / target_cpa) * 100 if target_cpa > 0 else 0.0

    summary_row = {
        "Start Date": start,
        "End Date": end,
        "Total Cost": total_cost,
        "Total Conversions": total_conversions,
        "Target CPA": target_cpa,
        "Actual CPA": actual_cpa,
        "CPA Delta (Actual - Target)": cpa_delta,
        "% Over/Under Target": over_under_pct,
    }

    summary_df = pd.DataFrame([summary_row])
    return summary_df, df_filtered


# -------------------------
# App
# -------------------------
def main():
    df = load_data()
    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    # Header with SRG logo
    col_logo, col_title = st.columns([1, 6])
    with col_logo:
        try:
            st.image("srg_logo.png", width=120)
        except Exception:
            st.write("SRG")

    with col_title:
        st.title("Simple CPA Summary (Demo)")
        st.caption("Uses sample Date / Cost / Conversions data and compares actual CPA vs target.")

    st.markdown("---")

    # Controls
    ctrl1, ctrl2, ctrl3 = st.columns([1, 2, 1])

    with ctrl1:
        target_cpa = st.number_input(
            "Target CPA",
            min_value=0.0,
            value=5.0,
            step=0.5,
            format="%.2f",
        )

    with ctrl2:
        start_date, end_date = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    with ctrl3:
        st.write("")  # spacing
        run = st.button("Run CPA Summaries ✅", use_container_width=True)

    if not run:
        st.info("Set a Target CPA and Date range, then click **Run CPA Summaries ✅**.")
        return

    # Summary + filtered data
    summary_df, df_filtered = build_summary(df, start_date, end_date, target_cpa)

    st.subheader("Summary")
    st.dataframe(summary_df, use_container_width=True)

    # -------------------------
    # Chart: Cost & Conversions over time
    # -------------------------
    st.subheader("Cost & Conversions Over Time")

    if not df_filtered.empty:
        chart_df = df_filtered.copy()
        chart_df["date"] = pd.to_datetime(chart_df["date"])

        cost_line = (
            alt.Chart(chart_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("cost:Q", title="Cost", axis=alt.Axis(titleColor="#60a5fa")),
                color=alt.value("#60a5fa"),
                tooltip=["date:T", "cost:Q"],
            )
        )

        conv_line = (
            alt.Chart(chart_df)
            .mark_line(point=True)
            .encode(
                x=alt.X("date:T", title="Date"),
                y=alt.Y("conversions:Q", title="Conversions", axis=alt.Axis(titleColor="#22c55e")),
                color=alt.value("#22c55e"),
                tooltip=["date:T", "conversions:Q"],
            )
        )

        chart = alt.layer(cost_line, conv_line).resolve_scale(y="independent")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No data in the selected date range.")

    # Underlying data
    st.subheader("Underlying data (filtered)")
    st.dataframe(df_filtered, use_container_width=True)


if __name__ == "__main__":
    main()