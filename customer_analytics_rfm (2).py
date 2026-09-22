"""
Customer Analytics & RFM Action Dashboard
Project: Customer Analytics and Revenue Opportunity Dashboard

Data source:
UCI Machine Learning Repository - Online Retail (Dataset ID 352)
https://archive.ics.uci.edu/dataset/352/online+retail

Run:
    pip install -r requirements.txt
    streamlit run customer_analytics_rfm.py
"""

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from ucimlrepo import fetch_ucirepo


st.set_page_config(
    page_title="Customer Analytics & RFM Dashboard",
    page_icon="📊",
    layout="wide",
)

DATASET_ID = 352


@st.cache_data(show_spinner=True)
def load_data():
    """Load the public UCI Online Retail dataset."""
    dataset = fetch_ucirepo(id=DATASET_ID)
    df = dataset.data.original.copy()

    # Normalize column names
    df.columns = [str(c).strip() for c in df.columns]

    required = [
        "InvoiceNo", "StockCode", "Description", "Quantity",
        "InvoiceDate", "UnitPrice", "CustomerID", "Country"
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Required columns are missing: {missing}")

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    df["CustomerID"] = pd.to_numeric(df["CustomerID"], errors="coerce")

    # Remove unusable records and cancellations for revenue analysis.
    df = df.dropna(subset=["InvoiceDate", "Quantity", "UnitPrice"])
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df = df[~df["InvoiceNo"].str.upper().str.startswith("C")]
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)

    return df


def make_rfm(df):
    """Build customer-level Recency, Frequency and Monetary measures."""
    customer_df = df.dropna(subset=["CustomerID"]).copy()
    if customer_df.empty:
        return pd.DataFrame()

    snapshot = customer_df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = (
        customer_df.groupby("CustomerID")
        .agg(
            Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
            Frequency=("InvoiceNo", "nunique"),
            Monetary=("Revenue", "sum"),
        )
        .reset_index()
    )

    # Rank-based scores avoid hard-coded monetary thresholds.
    for col in ["Recency", "Frequency", "Monetary"]:
        try:
            if col == "Recency":
                rfm[f"{col}_Score"] = pd.qcut(
                    rfm[col].rank(method="first"),
                    5,
                    labels=[5, 4, 3, 2, 1],
                ).astype(int)
            else:
                rfm[f"{col}_Score"] = pd.qcut(
                    rfm[col].rank(method="first"),
                    5,
                    labels=[1, 2, 3, 4, 5],
                ).astype(int)
        except ValueError:
            rfm[f"{col}_Score"] = 3

    rfm["RFM_Score"] = (
        rfm["Recency_Score"].astype(str)
        + rfm["Frequency_Score"].astype(str)
        + rfm["Monetary_Score"].astype(str)
    )

    def segment(row):
        r, f, m = row["Recency_Score"], row["Frequency_Score"], row["Monetary_Score"]
        if r >= 4 and f >= 4 and m >= 4:
            return "Champions"
        if r >= 4 and f >= 3:
            return "Loyal Customers"
        if r >= 3 and f >= 2 and m >= 2:
            return "Potential Loyalists"
        if r <= 2 and f >= 3:
            return "At Risk"
        return "Hibernating"

    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm


def recommendation(segment):
    actions = {
        "Champions": "Reward loyalty, early access, referral offers and premium bundles.",
        "Loyal Customers": "Use cross-sell recommendations and loyalty incentives.",
        "Potential Loyalists": "Nurture with personalized offers and repeat-purchase reminders.",
        "At Risk": "Launch win-back campaigns, service checks and targeted discounts.",
        "Hibernating": "Use low-cost reactivation campaigns; avoid excessive discounts.",
    }
    return actions.get(segment, "Review the segment and test a targeted action.")


def fmt_money(value):
    return f"£{value:,.0f}"


def main():
    st.title("📊 Customer Analytics & RFM Action Dashboard")
    st.caption(
        "Data → Information → Insight → Opportunity → Action | "
        "UCI Online Retail dataset"
    )

    try:
        df = load_data()
    except Exception as exc:
        st.error(
            "Dataset could not be loaded. Check your internet connection and "
            "the dependencies in requirements.txt."
        )
        st.exception(exc)
        st.stop()

    rfm = make_rfm(df)

    # Sidebar filters
    st.sidebar.header("Filters")
    countries = sorted(df["Country"].dropna().unique().tolist())
    selected_country = st.sidebar.multiselect(
        "Country", countries, default=[]
    )
    min_date = df["InvoiceDate"].min().date()
    max_date = df["InvoiceDate"].max().date()
    date_range = st.sidebar.date_input(
        "Invoice date range", (min_date, max_date), min_value=min_date, max_value=max_date
    )

    filtered = df.copy()
    if selected_country:
        filtered = filtered[filtered["Country"].isin(selected_country)]

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
        filtered = filtered[
            (filtered["InvoiceDate"] >= start) & (filtered["InvoiceDate"] < end)
        ]

    # KPI row
    customers = filtered["CustomerID"].nunique()
    transactions = filtered["InvoiceNo"].nunique()
    revenue = filtered["Revenue"].sum()
    units = filtered["Quantity"].sum()
    aov = revenue / transactions if transactions else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Revenue", fmt_money(revenue))
    k2.metric("Customers", f"{customers:,}")
    k3.metric("Transactions", f"{transactions:,}")
    k4.metric("Avg. Order Value", fmt_money(aov))
    k5.metric("Units Sold", f"{units:,.0f}")

    st.divider()

    tab1, tab2, tab3 = st.tabs(
        ["Executive Overview", "Customer & Product Analysis", "Risk & Action"]
    )

    with tab1:
        st.subheader("Revenue Trend")
        monthly = (
            filtered.groupby("Month", as_index=False)["Revenue"]
            .sum()
            .sort_values("Month")
        )
        fig = px.line(
            monthly,
            x="Month",
            y="Revenue",
            markers=True,
            title="Monthly Revenue",
            labels={"Revenue": "Revenue (£)", "Month": "Month"},
        )
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            country_rev = (
                filtered.groupby("Country", as_index=False)["Revenue"]
                .sum()
                .sort_values("Revenue", ascending=False)
                .head(10)
            )
            fig2 = px.bar(
                country_rev,
                x="Revenue",
                y="Country",
                orientation="h",
                title="Top 10 Countries by Revenue",
            )
            st.plotly_chart(fig2, use_container_width=True)

        with c2:
            top_products = (
                filtered.groupby("Description", as_index=False)["Revenue"]
                .sum()
                .sort_values("Revenue", ascending=False)
                .head(10)
            )
            fig3 = px.bar(
                top_products.sort_values("Revenue"),
                x="Revenue",
                y="Description",
                orientation="h",
                title="Top 10 Products by Revenue",
            )
            st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader("Customer and Product Performance")
        if rfm.empty:
            st.warning("CustomerID data is unavailable for RFM analysis.")
        else:
            segment_summary = (
                rfm.groupby("Segment")
                .agg(
                    Customers=("CustomerID", "nunique"),
                    Revenue=("Monetary", "sum"),
                    Avg_Recency=("Recency", "mean"),
                    Avg_Frequency=("Frequency", "mean"),
                )
                .reset_index()
                .sort_values("Revenue", ascending=False)
            )

            c1, c2 = st.columns(2)
            with c1:
                fig4 = px.bar(
                    segment_summary,
                    x="Segment",
                    y="Customers",
                    title="Customers by RFM Segment",
                )
                st.plotly_chart(fig4, use_container_width=True)

            with c2:
                fig5 = px.bar(
                    segment_summary,
                    x="Segment",
                    y="Revenue",
                    title="Revenue by RFM Segment",
                )
                st.plotly_chart(fig5, use_container_width=True)

            st.dataframe(
                segment_summary.style.format(
                    {
                        "Revenue": "£{:,.0f}",
                        "Avg_Recency": "{:,.1f}",
                        "Avg_Frequency": "{:,.1f}",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )

            st.info(
                "RFM interpretation: Recency measures how recently a customer bought, "
                "Frequency measures repeat purchasing, and Monetary measures customer revenue."
            )

    with tab3:
        st.subheader("Risk, Opportunity and Action")
        if rfm.empty:
            st.warning("Customer-level analysis cannot be generated.")
            return

        at_risk = rfm[rfm["Segment"] == "At Risk"].copy()
        champions = rfm[rfm["Segment"] == "Champions"].copy()

        c1, c2, c3 = st.columns(3)
        c1.metric("At-Risk Customers", f"{len(at_risk):,}")
        c2.metric("Champion Customers", f"{len(champions):,}")
        c3.metric("At-Risk Revenue", fmt_money(at_risk["Monetary"].sum()))

        action_table = pd.DataFrame(
            [
                {
                    "Segment": seg,
                    "Business Meaning": meaning,
                    "Recommended Action": recommendation(seg),
                }
                for seg, meaning in [
                    ("Champions", "High-value, recent and frequent customers."),
                    ("Loyal Customers", "Repeat customers with strong engagement."),
                    ("Potential Loyalists", "Customers with room to develop repeat behavior."),
                    ("At Risk", "Previously valuable/frequent customers with weak recency."),
                    ("Hibernating", "Low recent activity and weaker engagement."),
                ]
            ]
        )
        st.dataframe(action_table, use_container_width=True, hide_index=True)

        if not at_risk.empty:
            st.subheader("Priority At-Risk Customers")
            priority = at_risk.sort_values(
                ["Monetary", "Recency"], ascending=[False, True]
            ).head(25)
            st.dataframe(
                priority[
                    ["CustomerID", "Recency", "Frequency", "Monetary", "RFM_Score", "Segment"]
                ].style.format({"Monetary": "£{:,.2f}"}),
                use_container_width=True,
                hide_index=True,
            )

    st.divider()
    st.caption(
        "Project note: This dashboard uses a public UCI dataset and performs "
        "descriptive analytics plus RFM segmentation. It does not claim causal relationships."
    )


if __name__ == "__main__":
    main()
