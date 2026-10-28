"""Generate the audio examples in audio/ by running the notebooks' own code.

Run from the integratron directory:
    .venv/bin/python make_audio_examples.py

Takes about a minute. Each notebook's code cells run with figures, sliders and
audio players switched off, then the sounds the notebook plays are written as
16-bit WAV files.
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ipywidgets
import IPython.display
import nbformat
from scipy.io import wavfile

OUT = Path("audio")
AUDIO_RATE = 22050

# Sliders, players and figure windows do nothing when the notebooks run here
ipywidgets.interact = lambda **widgets: (lambda function: function)
IPython.display.display = lambda *args, **kwargs: None
plt.show = lambda *args, **kwargs: None


def run_notebook(path):
    namespace = {}
    for cell in nbformat.read(path, as_version=4).cells:
        if cell.cell_type == "code":
            exec(compile(cell.source.replace("%matplotlib inline", ""), path, "exec"),
                 namespace)
            plt.close("all")
    print("ran", path)
    return namespace


def write(name, samples, normalise=True):
    # normalise=False keeps the notebook's volume setting, so files can be compared
    samples = np.asarray(samples, float)
    if samples.ndim == 2:  # stereo given as (left, right) rows
        samples = samples.T
    if normalise:
        samples = 0.9 * samples / np.abs(samples).max()
    pcm = (np.clip(samples, -1, 1) * 32767).astype(np.int16)
    wavfile.write(OUT / f"{name}.wav", AUDIO_RATE, pcm)
    print(f"  wrote {name}.wav ({len(pcm) / AUDIO_RATE:.1f} s)")


def focusing():
    nb = run_notebook("01_dome_reflections_and_focusing.ipynb")
    for name, file_name in [("at the mirror point", "01_pulse_at_mirror_point"),
                            ("1 m past the mirror point", "01_pulse_1m_past_mirror_point")]:
        write(file_name, nb["recordings"][name] * nb["volume"], normalise=False)


def ringing():
    nb = run_notebook("02_ringing_and_room_modes.ipynb")
    alpha = 0.1
    for sound, file_name in [("click", "click"), ("noise", "noise"),
                             ("slow sweep", "sweep_410_450hz")]:
        dry, _ = nb["dry_sound"](sound)
        if sound != "click":
            write(f"02_{file_name}_dry", dry)
        write(f"02_{file_name}_at_centre", nb["centre_echoes"](dry, alpha))


def whispering_gallery():
    nb = run_notebook("04_whispering_gallery.ipynb")
    for name, file_name in [("next to the source (0°)", "04_whisper_next_to_source"),
                            ("a quarter of the way round (90°)", "04_whisper_90_degrees"),
                            ("opposite wall (180°)", "04_whisper_opposite_wall")]:
        write(file_name, nb["recordings"][name] * nb["volumes"][name], normalise=False)


def singing_bowl():
    nb = run_notebook("05_singing_bowl.ipynb")
    f = nb["BOWL_FUNDAMENTAL_HZ"]
    t = np.arange(0, 4.0, 1 / AUDIO_RATE)
    write("05_bowl_warble_1hz_split",
          np.cos(2 * np.pi * f * t) + np.cos(2 * np.pi * (f + 1.0) * t))
    write("05_bowl_struck", nb["struck_bowl"](f, 20.0)[1])


def listening():
    nb = run_notebook("06_listening_to_the_dome.ipynb")
    for sound, file_name in [("clap", "clap"), ("whisper", "whisper"),
                             ("voice (sung ah)", "voice"), ("singing bowl", "bowl")]:
        write(f"06_dry_{file_name}", nb["DRY"][sound])
    for sound, surface, place, file_name in [
        ("whisper", "smooth", "mirror point", "06_whisper_at_mirror_point"),
        ("whisper", "smooth", "off focus", "06_whisper_off_focus"),
        ("voice (sung ah)", "smooth", "centre: hear yourself", "06_voice_at_centre"),
        ("singing bowl", "smooth", "centre: hear yourself", "06_bowl_at_centre"),
        ("clap", "smooth", "mirror point", "06_clap_mirror_point_smooth_dome"),
        ("clap", "rough", "mirror point", "06_clap_mirror_point_rough_dome"),
    ]:
        write(file_name, nb["in_the_dome"](sound, surface, place, 0), normalise=False)


def two_bowls():
    nb = run_notebook("07_two_crystal_bowls.ipynb")
    bowl, t = nb["crystal_bowl"], nb["T"]
    f1, f2 = nb["BOWL_1_HZ"], nb["BOWL_2_HZ"]
    write("07_one_crystal_bowl", bowl(f1, t))
    for gap, label in [(1.4, "1p4"), (6.0, "6"), (25.0, "25")]:
        write(f"07_two_bowls_{label}hz_apart", bowl(f1, t) + bowl(f1 + gap, t))
    ears = nb["ear_positions"](0.0)
    write("07_two_bowls_in_room_stereo",
          np.vstack([nb["at_ear"](ears["left"]), nb["at_ear"](ears["right"])]))
    write("07_two_bowls_binaural_stereo", np.vstack([bowl(f1, t), bowl(f2, t)]))
    for low, label in [(261.6, "both_in_dip"), (255.8, "one_on_peak")]:
        both = bowl(low, t) + bowl(low + 1.4, t)
        write(f"07_two_bowls_dome_centre_{label}", nb["centre_echoes"](both, 0.1))


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    focusing()
    ringing()
    whispering_gallery()
    singing_bowl()
    listening()
    two_bowls()
