"""Save the matplotlib animations from notebook 07 as GIFs in figures/animations/.

Run from the integratron directory:
    .venv/bin/python make_animations.py

The notebook's code cells run with sliders and players switched off. The
animations they build are then written with Pillow.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ipywidgets
import IPython.display
import nbformat
from matplotlib.animation import PillowWriter

OUT = Path("figures/animations")

ipywidgets.interact = lambda **widgets: (lambda function: function)
IPython.display.display = lambda *args, **kwargs: None
plt.show = lambda *args, **kwargs: None


def run_notebook(path):
    namespace = {}
    for cell in nbformat.read(path, as_version=4).cells:
        if cell.cell_type == "code":
            exec(compile(cell.source.replace("%matplotlib inline", ""), path, "exec"),
                 namespace)
    print("ran", path)
    return namespace


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    nb = run_notebook("07_two_crystal_bowls.ipynb")
    for name, animation, fps, dpi in [("crystal_bowl_vibrating", nb["BOWL_ANIMATION"], 24, 80),
                                 ("two_bowls_beating", nb["BEAT_ANIMATION"], 12, 64)]:
        animation.save(OUT / f"{name}.gif", writer=PillowWriter(fps=fps), dpi=dpi)
        print("wrote", OUT / f"{name}.gif")
