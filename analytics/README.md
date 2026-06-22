# Analytics

This folder contains the **Business Analyst** artifacts for KINZ Secure Commerce Hub.

## Notebooks

- [`kinz_eda.ipynb`](./kinz_eda.ipynb) — Exploratory Data Analysis on the 2023–2024 sales dataset. Produces three business insights:
  1. **Customer Lifetime Value by Channel** — B2B channels deliver 3–4× the CLV of B2C web.
  2. **High-Margin SKU Concentration** — Vegetable Oils lead on margin %; Gift Sets lead on revenue.
  3. **Channel Risk Map** — B2C Instagram is leaking margin (high discount + low basket).

## Charts

After running the notebook, the following PNGs are written to `analytics/charts/`:

| File                       | Insight                                              |
|----------------------------|------------------------------------------------------|
| `clv_by_channel.png`       | Bar chart of CLV per customer by channel             |
| `margin_vs_revenue.png`    | Grouped bars: revenue share % vs. margin % per category |
| `channel_risk.png`         | Scatter: avg basket vs. avg discount, bubble = orders |

## How to run

```bash
# From the repo root
pip install jupyter pandas matplotlib seaborn
jupyter notebook analytics/kinz_eda.ipynb
```

Or headless:

```bash
jupyter nbconvert --to notebook --execute analytics/kinz_eda.ipynb --output analytics/kinz_eda.executed.ipynb
```
