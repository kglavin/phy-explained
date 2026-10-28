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

### [Integratron](integratron/)

How the Integratron, a 16.8 m wooden dome in Landers, California, focuses sound, rings, carries whispers round its wall, and what a sound bath in it sounds like. Start with the overview, which needs no code:

- [00_overview.md](integratron/00_overview.md): the whole story in seven short steps, with pictures.

Then the notebooks, one topic each:

| Topic | Notebook | Audio |
|---|---|---|
| T1 Dome reflections and focusing | [01_dome_reflections_and_focusing.ipynb](integratron/01_dome_reflections_and_focusing.ipynb) | yes |
| T2 Ringing and room modes | [02_ringing_and_room_modes.ipynb](integratron/02_ringing_and_room_modes.ipynb) | yes |
| T3 Focusing in 3D | [03_3d_focusing.ipynb](integratron/03_3d_focusing.ipynb) | |
| T4 Whispering gallery | [04_whispering_gallery.ipynb](integratron/04_whispering_gallery.ipynb) | yes |
| T5 The singing bowl | [05_singing_bowl.ipynb](integratron/05_singing_bowl.ipynb) | yes |
| T6 Listening to the dome | [06_listening_to_the_dome.ipynb](integratron/06_listening_to_the_dome.ipynb) | yes |
| T7 Two crystal bowls | [07_two_crystal_bowls.ipynb](integratron/07_two_crystal_bowls.ipynb) | yes |

WAV files of the notebooks' sounds are in [integratron/audio/](integratron/audio/README.md), so they can be heard without running code.

All results come from models with stated assumptions, such as wall absorption and a perfectly smooth dome. No measurements of the building are used.

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

For the Integratron series, replace `chara-array` with `integratron` in the commands above. It needs no data downloads.
