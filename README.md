# Composition and district geography of the kidney screening judgement in Korea, 2015-2023

Analysis code for the manuscript

> Kim S. *Reduced filtration or proteinuria? Unpacking a kidney screening judgement in Korea.* Manuscript under review.

Archived versions: Zenodo, https://doi.org/10.5281/zenodo.24295187 (v1.0.0, original submission); v1.1.0 (revision) is archived as a new version of the same Zenodo record.

## Contents

This repository contains code only. The processed district-year data (master table, analytic panel, expected counts, result tables, adjacency graph and boundary file) are not included; they are available from the author on reasonable request. All source statistics are public (see Data sources).

| Path | What it is |
|---|---|
| `01_스크립트/` | Analysis scripts (below) |
| `04_분석/KIDC/sets_KIDC_*.json`, `config_KIDC_std3.json` | Covariates, expected directions, forced controls and model settings (principal model `std3`; sensitivity versions `s577`, `s2`, `s8`) |
| `04_분석/KIDC/MS/` | Scripts that read the result tables and write every number, table and figure in the manuscript and supplementary material, including `content_kids.py`, which generates the Methods and Results text (the draft source of the Introduction and Discussion is not included) |

Folder and some column names are in Korean because the source tables are Korean; each script has a header comment describing its inputs and outputs.

## Data sources

All inputs are public, aggregated statistics. No individual-level data are included.

- General health screening examinees with a judgement and examinees judged to have suspected kidney disease by district (KOSIS DT_35007_N098, DT_35007_N103) and nationally by sex and 5-year age group (DT_35007_N099, DT_35007_N104): National Health Insurance Service via KOSIS.
- Distributions of estimated glomerular filtration rate (DT_35007_N128 by province, DT_35007_N129 national) and of dipstick proteinuria (DT_35007_N064 by province, DT_35007_N065 national), 2012-2024, retrieved on 17 November 2026; national distributions by sex and 5-year age group of eGFR (N129), dipstick proteinuria (N065) and serum creatinine (DT_35007_N079), retrieved again on 19 November 2026 for the revision.
- Ministry of Health and Welfare, health screening implementation standards (editions effective 2014, 2017, 2024 and 2026), annexes on judgement criteria and test methods, National Law Information Center (https://www.law.go.kr).
- Population by sex and 5-year age group: Ministry of the Interior and Safety, resident registration statistics (Changwon 2023 corrected; `population_override`).
- District covariates: KOSIS, the Community Health Survey, National Health Insurance Service screening and regional statistics, the census (tertiary education) and public sports facility surveys. Comparison outcomes (people treated for gastric cancer and for infectious diseases) come from National Health Insurance regional statistics.

## Pipeline

Run from the repository root (set `ST_DATA_ROOT` and `ST_FBDZIP_CORRECTED` to the local copies of the public source files). All R fits use one thread and are launched through `01_스크립트/rslot.sh`.

| Step | Script | Output |
|---|---|---|
| 1 | `88K_kidc_definition.py` | Reconciliation of the judgement with published eGFR and dipstick proteinuria distributions (national and provincial) |
| 2 | `99K2_build_Estd3_kids.py` (uses `38_build_Estd_all.py`, `40_region_crosswalk.py`, `50_build_master_panel.py`) | Examinees and judgements by district, expected numbers standardised by sex and age among examinees, resident-based expected numbers (2012-2024; the analysis uses 2015-2023) |
| 3 | `99N_build_E_next10.py`, `99N_screen_next10_prep_gpt.py`, `98_fit_forced.R`, `99N_screen_next10.py` (uses `98_screen_std.py`) | Descriptive spatial screening |
| 4 | `99c_extra_canonical_pool_undx.py`, `99c_extra_canonical_pool_kids.py` | Treated hypertension or diabetes share, tertiary education, basic livelihood security (2021-2023 correction), joined by district code |
| 5 | `80_build_disease_panel_v.py KIDC` (`ST_VER=std3`) | Analytic panel, 2015-2023 |
| 6 | `81_fit_inla.R KIDC` (`ST_VER=std3`, `ST_THREADS=1`; see `04_분석/KIDC/run_std3_chain.sh`) | Principal model, set comparison, 200-subset multiverse, window models |
| 7 | `85_window_maps.R`, `86_yearly_maps_ehsa_kidc.py` (wraps `86_yearly_maps_ehsa.py`), `87_window_grid.py` | Maps and emerging hot spot analysis |
| 8 | `88g_sens_prep.py KIDC std3 INFECT,GCA`, `88g_sens_suite_kidc.R` (`GROUP=1..6`), `88h_ppc_varpart.R`, `88k_struct_kh.R` (nb, struct, review), `88k_struct_kh_kidc.R` with `kh_constraints_kidc.R` (kh), `89g_sens_combine.py` | Sensitivity analyses, comparison outcomes, Knorr-Held models |
| 9 | `88K_kidc_component_panel.py`, `88K_kidc_component_sens.R` | Principal model with provincial eGFR and proteinuria shares added |
| 10 | `04_분석/KIDC/MS/build/run_all.sh` (`build_refs_kids.py`, `figs_kids.py`, `tables_kids.py`, `build_ms.py`, `esm_kids.py`, `check_ms.py`; `rr_kids.py` reads the revision outputs) | Manuscript, supplementary material, figures and checks |
| 11 | `88R_kidc_fetch_N065_age.py`, `88R_kidc_rr_reconcile.py` (revision) | National reconciliation of the judgement by sex and 5-year age group with eGFR, dipstick proteinuria and creatinine distributions; union bounds; direct standardisation |
| 12 | `99K3_kidc_E_uncert.py` then `88g_sens_suite_kidc.R` with `GROUP=7` (revision) | Bias analysis of the estimated examinee age structure: 20 random and 8 exposure-linked perturbations of expected numbers, principal model refitted |

The boundary file is found at `data/boundary/final.shp` by default; set `ST_SHP` to use another path.

## Software

R 4.6.0 with R-INLA 25.10.19, spdep and sf; Python 3.9 with pandas, geopandas, numpy, scipy, statsmodels, matplotlib and python-docx.

## License

MIT (see `LICENSE`).
