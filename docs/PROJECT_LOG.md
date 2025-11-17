# Navigate Wealth Advisor Toolkit — Project Log

This log keeps lightweight context so any new collaborator (or future session) knows where we are, what changed, and what’s next.

## Current state (2024-11-17)
- Unified dark sidebar with glassy main canvas, softened gradients, and Inter font.
- Hero/landing with “Broker dashboard” pill, gradient hero panel, and sidebar nav for all calculators; client snapshot feeds defaults.
- Tools refreshed for South African advisory use:
  - Budget: cash-flow map with savings-rate KPIs.
  - Salary Tax: payslip story with PAYE/UIF/medical credit metrics.
  - RA Rebate: deductible cap vs excess with marginal-rate rebate.
  - Retirement: reorganized inputs, KPI trio, modernized charts.
  - Estate Liquidity: liquidity gap KPIs, expanders for assets/liabilities.
  - Everest Wealth: quick quote with gross/net income and broker fee.
  - Advisor Brief: snapshot + ratios + actions; Excel/PDF export; debt snowball helper.
  - Risk Profiler: appetite questionnaire → equity tilt gauge.
  - Life Cover Gap: Life/DI/CI need vs cover (income replacement, debts, education, final expenses).

## What we shipped this session
- Boosted readability: brighter questionnaire radios, higher-contrast risk-profiler card, and darker gauge number/segments.
- Sidebar usability: selected nav item now stays legible on the dark gradient, with clearer active highlight.
- Everest Wealth visuals: added cumulative term line chart, income flow donut, bonus rows, and sharpened bar styling.
- GitHub repo refreshed on `Navigate-Tools-2.1`; Streamlit deploy unblocked via entry-file URL.

## Next session focus
- Confirm Streamlit app is live on `Navigate-Tools-2.1` URL; set custom subdomain if desired.
- Add README refresh (screenshots, deploy note) and tag release.
- Verify SARS tables (2024/25) and update if needed.
- Consider a combined PDF pack (Brief + selected tool outputs).

## Backlog / Ideas
- Launcher overhaul: card design that feels premium/square per user taste.
- Combined PDF pack: Brief + Risk Profiler + selected calculators.
- Budget: preset SA expense templates; toggle fixed vs discretionary.
- Estate: illustrate liquidity gap over time if property is sold vs retained.
- Everest: add sensitivity for tax rates and broker commission variants.
- SARS tables: hook in live config/year selector to reduce manual updates.
- Diagnostics: “Data Room” tab capturing inputs/outputs for compliance notes.

## How to use this log
- Append bullet points under “What we shipped this session” after each work block.
- Park future ideas under “Backlog / Ideas” with short, actionable statements.
- Update “Current state” when a major UX or functional change lands.

## Next session quick start
- Run `streamlit run app.py`.
- Skim “What we shipped this session” for the latest context.
- Pick the top backlog item and move it into “What we shipped…” once done.
