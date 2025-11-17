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
- Modernized global styling to match user brand direction: added gradient canvas on the main view container, softened hero panel with “Broker dashboard” label, and expanded rounded expanders/cards.
- Restyled inputs/buttons with subtler focus rings and radius; ensured sidebar retains dark gradient while main canvas uses a light gradient wash instead of flat white.
- Tuned workspace tiles to a calmer blue gradient with lighter shadows to reduce visual harshness.

## Next session focus
- Finish card click wiring: ensure hidden buttons render before cards, IDs match, and clicks update `active_tool` without opening new tabs; remove any leftover legacy launcher output.
- Confirm launcher look/feel signed off; otherwise refine spacing/typography and active-state styling.
- Decide on deployment: push to GitHub and repoint Streamlit Cloud.
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
