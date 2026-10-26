# phy-explained

Physics explained through intuition and interactive simulations, in Jupyter notebooks.

## Series

### [CHARA Array](chara-array/)

How the CHARA Array on Mount Wilson combines six telescopes up to 331 m apart to measure stars at the milliarcsecond scale. Start with the overview, which needs no code:

- [00_overview.md](chara-array/00_overview.md): the whole story in eight short steps, one figure each.

Then the notebooks, one topic each:

| Topic | Notebook | Real data used |
|---|---|---|
| T1 Diffraction and resolution | [01_diffraction_and_resolution.ipynb](chara-array/01_diffraction_and_resolution.ipynb) | |
| T2 Two-telescope interference | [02_two_telescope_interference.ipynb](chara-array/02_two_telescope_interference.ipynb) | |
| T3 van Cittert–Zernike theorem | [03_van_cittert_zernike.ipynb](chara-array/03_van_cittert_zernike.ipynb) | |
| T4 Stellar diameters | [04_stellar_diameters.ipynb](chara-array/04_stellar_diameters.ipynb) | δ Cephei (VEGA) |
| T5 uv coverage | [05_uv_coverage.ipynb](chara-array/05_uv_coverage.ipynb) | δ Cephei (VEGA) |
| T6 Delay lines | [06_delay_lines.ipynb](chara-array/06_delay_lines.ipynb) | CL Lac cart positions (MIRC-X) |
| T7 Atmospheric turbulence and closure phase | [07_atmosphere_and_closure_phase.ipynb](chara-array/07_atmosphere_and_closure_phase.ipynb) | CL Lac (MIRC-X) |
| T8 Binaries and image reconstruction | [08_binaries_and_image_reconstruction.ipynb](chara-array/08_binaries_and_image_reconstruction.ipynb) | CL Lac (MIRC-X) |

Notebook 05 uses the δ Cephei data downloaded by notebook 04, so run 04 first. Notebooks 06 to 08 download their own data.

## Running the notebooks

Each series has its own Python environment. For the CHARA series:

```bash
cd chara-array
uv venv .venv && uv pip install -p .venv -r requirements.txt
```

Open a notebook in VS Code (Jupyter extension) or JupyterLab and select `chara-array/.venv` as the kernel. The sliders need ipywidgets, which is included.

Real data are public calibrated observations from the [JMMC Optical Interferometry Database](https://oidb.jmmc.fr). The notebooks download them into `chara-array/data/` on first run (about 10 MB in total). That folder is not committed.

To regenerate the overview figures:

```bash
cd chara-array
.venv/bin/python make_overview_figures.py
```
