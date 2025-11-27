import streamlit as st
import pandas as pd
from datetime import datetime, date

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="SRG – Simple CPA Summary",
    page_icon="📈",
    layout="wide",
)

# -------------------------
# Simple dark theme + styling (Google Finance–ish)
# -------------------------
DARK_CSS = """
<style>
:root {
  --bg-color: #050816;
  --bg-elevated: #111827;
  --accent-good: #22c55e;
  --accent-bad: #f97373;
  --accent-pill: rgba(148,163,184,0.25);
  --border-subtle: rgba(148,163,184,0.30);
  --text-main: #e5e7eb;
  --text-muted: #9ca3af;
}

html, body, [data-testid="stAppViewContainer"] {
  background-color: var(--bg-color);
  color: var(--text-main);
}

[data-testid="stSidebar"] {
  background-color: #020617;
}

h1, h2, h3, h4, h5, h6, p, span, div {
  color: var(--text-main);
}

/* Make dataframes sit on dark cards */
[data-testid="stDataFrame"] {
  border-radius: 12px;
  border: 1px solid var(--border-subtle);
  overflow: hidden;
}
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)

# -------------------------
# Helper: metric card component
# -------------------------
def metric_card(label: str, value: str, subtext: str, *, good: bool | None = None):
    if good is True:
        sub_color = "var(--accent-good)"
    elif good is False:
        sub_color = "var(--accent-bad)"
    else:
        sub_color = "var(--text-muted)"

    st.markdown(
        f"""
        <div style="
            background-color: var(--bg-elevated);
            border-radius: 12px;
            padding: 16px 18px;
            border: 1px solid var(--border-subtle);
        ">
            <div style="font-size: 12px; text-transform: uppercase;
                        color: var(--text-muted); letter-spacing: 0.08em;">
                {label}
            </div>
            <div style="font-size: 26px; font-weight: 600; margin-top: 4px;">
                {value}
            </div>
            <div style="font-size: 13px; margin-top: 6px; color: {sub_color};">
                {subtext}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------
# Data loading
# (Replace this with your Google Sheets logic later if you want)
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
# Core CPA calculation logic
# -------------------------
def build_summary(df: pd.DataFrame, start: date, end: date, target_cpa: float) -> dict:
    mask = (df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))
    df_range = df.loc[mask].copy()

    total_cost = df_range["cost"].sum()
    total_conversions = df_range["conversions"].sum()
    actual_cpa = (total_cost / total_conversions) if total_conversions > 0 else 0.0

    cpa_delta = actual_cpa - target_cpa
    over_under_pct = (cpa_delta / target_cpa) * 100 if target_cpa > 0 else 0.0

    return {
        "df_range": df_range,
        "total_cost": total_cost,
        "total_conversions": total_conversions,
        "actual_cpa": actual_cpa,
        "cpa_delta": cpa_delta,
        "over_under_pct": over_under_pct,
    }


# -------------------------
# App layout
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
            st.markdown("### SRG")

    with col_title:
        st.markdown(
            """
            <div style="display:flex; flex-direction:column; justify-content:center; height:100%;">
                <h1 style="margin-bottom:4px;">SRG – Simple CPA Summary (Demo)</h1>
                <p style="margin-top:0; color: var(--text-muted);">
                    Quick, at-a-glance view of cost efficiency over time. Powered by Growth Genie.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Controls row (Target CPA + Date range)
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 2, 1])

    with ctrl_col1:
        target_cpa = st.number_input(
            "Target CPA",
            min_value=0.0,
            value=5.0,
            step=0.5,
            format="%.2f",
        )

    with ctrl_col2:
        start_date, end_date = st.date_input(
            "Date range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )

    with ctrl_col3:
        st.write("")  # spacing
        run = st.button("Run CPA Summary ✅", use_container_width=True)

    if run:
        results = build_summary(df, start_date, end_date, target_cpa)
        df_range = results["df_range"]
        total_cost = results["total_cost"]
        total_conversions = results["total_conversions"]
        actual_cpa = results["actual_cpa"]
        cpa_delta = results["cpa_delta"]
        over_under_pct = results["over_under_pct"]

        # Metrics row (cards)
        m1, m2, m3 = st.columns(3)
        with m1:
            metric_card(
                "Actual CPA",
                f"${actual_cpa:,.2f}",
                f"{'+' if cpa_delta > 0 else ''}{cpa_delta:,.2f} vs target",
                good=(cpa_delta <= 0),
            )
        with m2:
            metric_card(
                "Target CPA",
                f"${target_cpa:,.2f}",
                "SRG efficiency goal",
                good=None,
            )
        with m3:
            conv_change_text = f"{total_conversions:,} conversions in period"
            metric_card(
                "Conversion Volume",
                f"{total_conversions:,}",
                conv_change_text,
                good=True,
            )

        # Small pill indicating date range
        st.markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center;
                        margin-top: 24px; margin-bottom: 8px;">
                <div style="font-size:16px; font-weight:600;">Underlying data (filtered)</div>
                <div style="background: var(--accent-pill); color: var(--text-main);
                            padding:4px 12px; border-radius:999px; font-size:12px;">
                    {start_date.isoformat()} → {end_date.isoformat()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.dataframe(df_range, use_container_width=True)

        # AI-style insight panel (Google Finance "research" vibes)
        if target_cpa > 0:
            if cpa_delta > 0:
                direction = "above"
                good = False
            elif cpa_delta < 0:
                direction = "below"
                good = True
            else:
                direction = "at"
                good = None
        else:
            direction = "n/a"
            good = None

        if good is False:
            lead = "⚠️ CPA is running hot."
            tone_color = "var(--accent-bad)"
        elif good is True:
            lead = "✅ CPA is beating target."
            tone_color = "var(--accent-good)"
        else:
            lead = "ℹ️ CPA is exactly on target."
            tone_color = "var(--text-muted)"

        st.markdown(
            f"""
            <div style="
                margin-top:24px;
                padding:16px 18px;
                border-radius:12px;
                background:linear-gradient(135deg, rgba(56,189,248,0.10), rgba(139,92,246,0.12));
                border:1px solid var(--border-subtle);
            ">
                <div style="font-size:13px; text-transform:uppercase; color:var(--text-muted);
                            letter-spacing:0.08em; margin-bottom:6px;">
                    AI-Style Performance Insight
                </div>
                <div style="font-size:14px; line-height:1.6;">
                    <span style="color:{tone_color}; font-weight:600;">{lead}</span>
                    Current CPA is <b>${actual_cpa:,.2f}</b>, which is
                    <b>{abs(over_under_pct):.1f}%</b> {direction} the target of
                    <b>${target_cpa:,.2f}</b> over this period.
                    Use this as a quick sanity check on whether non-brand budgets
                    are aligned with SRG efficiency goals.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:
        st.info("Set a target CPA and date range, then click **Run CPA Summary ✅** to see results.")


if __name__ == "__main__":
    main()