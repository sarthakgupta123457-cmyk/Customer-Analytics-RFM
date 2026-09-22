# Customer Analytics & RFM Action Dashboard

## 1. Project Overview

This project converts online retail transaction data into business insights and recommended actions.

The workflow follows:

**Data → Information → Insight → Opportunity/Risk → Action**

The dashboard focuses on:
- Revenue and transaction KPIs
- Monthly revenue trends
- Country and product performance
- Customer segmentation using RFM analysis
- Identification of at-risk and high-value customers
- Practical business actions for each customer segment

## 2. Problem Statement

Retail transaction data contains large amounts of information about purchases, products, customers and countries. The business needs a simple analytics solution that can identify performance trends, valuable customer groups, customers showing reduced engagement, and actions that can be tested to improve retention and revenue.

## 3. Dataset

**Dataset:** Online Retail  
**Repository:** UCI Machine Learning Repository  
**Dataset ID:** 352  
**Source:** https://archive.ics.uci.edu/dataset/352/online+retail

The UCI repository describes this as transactional data from a UK-based registered non-store online retailer, covering transactions from 01/12/2010 to 09/12/2011. It contains invoice, product, quantity, date, unit price, customer and country fields.

## 4. Main KPIs

- Total revenue
- Unique customers
- Number of transactions
- Average order value
- Units sold
- Monthly revenue trend
- Revenue by country
- Revenue by product
- Customer segment size and value
- At-risk customer revenue

## 5. RFM Method

RFM means:
- **Recency:** how recently a customer purchased
- **Frequency:** how often a customer purchased
- **Monetary:** how much revenue the customer generated

The project creates RFM scores and groups customers into:
- Champions
- Loyal Customers
- Potential Loyalists
- At Risk
- Hibernating

These labels are analytical segments, not predictions of future behavior.

## 6. Recommended Actions

| Segment | Suggested action |
|---|---|
| Champions | Reward loyalty, early access, referral offers and premium bundles. |
| Loyal Customers | Cross-sell relevant products and use loyalty incentives. |
| Potential Loyalists | Personalized offers and repeat-purchase reminders. |
| At Risk | Win-back campaigns, service checks and targeted offers. |
| Hibernating | Low-cost reactivation campaigns and controlled incentives. |

## 7. Project Structure

```text
Customer_Analytics_RFM/
├── customer_analytics_rfm.py
├── requirements.txt
├── README.md
└── Customer_Analytics_Project_Report.docx
```

## 8. Installation

```bash
pip install -r requirements.txt
```

## 9. Run the Dashboard

```bash
streamlit run customer_analytics_rfm.py
```

The application fetches the public UCI dataset through `ucimlrepo`. An internet connection is required when the dataset is first loaded.

## 10. Data Cleaning

The application:
1. Converts dates and numeric columns to usable types.
2. Removes unusable dates/quantities/prices.
3. Excludes cancellation invoices from revenue analysis.
4. Keeps positive quantity and price transactions.
5. Calculates transaction-level revenue as `Quantity × UnitPrice`.
6. Excludes missing CustomerID values only where customer-level RFM analysis is required.

## 11. Limitations

- The dataset represents historical transactions from one online retailer and should not be treated as a current market sample.
- RFM segments are descriptive and do not prove that a particular action will cause higher revenue.
- The project does not use the exact dataset from the internship masterclass; the chosen dataset is the public UCI Online Retail dataset.
- Business recommendations should be tested using controlled experiments before being treated as proven improvements.

## 12. Submission Checklist

Before submitting:
- [ ] `customer_analytics_rfm.py`
- [ ] `requirements.txt`
- [ ] `README.md`
- [ ] `Customer_Analytics_Project_Report.docx`
- [ ] GitHub repository containing these four files
- [ ] Verify that the masterclass dataset was not reused
