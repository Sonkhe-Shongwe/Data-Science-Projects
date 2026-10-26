# Rebuild validation report

**Review build date:** 26 October 2026.

## Executed and verified

- Dataset SHA-256: `caa83db2077f8e08ab87e0dd1298c25e698b9c3461b94dad21ab9faad5c72e1b`; matches the source ZIP exactly.
- Jupyter Notebook: **31 cells**, including **15 executed code cells**, with 15 consecutive execution counts and **no error outputs**.
- Code validation: 8 automated tests passed (`python -m pytest tests -q`).
- Visual exports: 8 PNG figures generated through `src/visuals.py` from the input CSV and analytic methods; no figures produced from imaginary or AI-invented data.
- Reports exported: monthly data for all available observations, monthly data for 44-group balanced panel, 44-group comparison rows, JSON metrics manifest.

## Acceptance cautions

- These are descriptive regional/area-unit averages without survey sampling weights or design variances.
- The 'employed share' measure is an implied proxy dependent on compatible unemployment and labour-force definitions.
- The coverage-balanced subsample uses 24 of 28 regions and is not representative by construction.
- The single-month June observation cannot establish durable labour-market recovery.
- Region-cluster resampling is a compositional sensitivity diagnostic rather than a population survey CI.
- Source CSV redistribution terms must be confirmed before wider republication if not already permitted by existing repo/source licence.

## Publication status

**Not published to GitHub.** Requires explicit user approval before replacing project files.
