"""Generate the figures used by 00_overview.md.

Run from the integratron directory:
    .venv/bin/python make_overview_figures.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.optimize import brentq
from scipy.special import j0, lpmv, spherical_jn

OUT = Path("figures/00_overview")
SPEED_OF_SOUND = 343.0
R = 55 * 0.3048 / 2                    # dome radius, 8.38 m
DRUM_HEIGHT = 38 * 0.3048 - R          # wall under the dome, 3.2 m
ROUND_TRIP_S = 2 * R / SPEED_OF_SOUND
BLUE, ORANGE, AQUA, GREY = "#2a78d6", "#eb6834", "#1baf7a", "#8a8a85"
plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.facecolor": "white",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#e4e3df",
    "lines.linewidth": 2,
    "font.size": 10,
})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / name)


def draw_dome(ax, full_circle=False):
    phi = np.linspace(0, np.pi, 200)
    ax.plot(R * np.cos(phi), R * np.sin(phi), color="k", linewidth=2)
    if full_circle:
        ax.plot(R * np.cos(phi), -R * np.sin(phi), color=GREY, linewidth=1.2,
                linestyle="--")
    ax.plot([-R, R], [0, 0], color="k", linewidth=2)
    ax.set_aspect("equal")
    ax.axis("off")


def trace_rays_2d(source, angles, n_bounces):
    # Ray paths inside a circle: (n_rays, n_bounces + 2, 2)
    pos = np.tile(np.asarray(source, float), (len(angles), 1))
    direction = np.column_stack([np.cos(angles), np.sin(angles)])
    points = [pos]
    for _ in range(n_bounces + 1):
        b = np.sum(pos * direction, axis=1)
        c = np.sum(pos ** 2, axis=1) - R ** 2
        pos = pos + (-b + np.sqrt(np.maximum(b ** 2 - c, 0)))[:, None] * direction
        points.append(pos)
        normal = pos / np.linalg.norm(pos, axis=1, keepdims=True)
        direction = direction - 2 * np.sum(direction * normal, axis=1)[:, None] * normal
        direction /= np.linalg.norm(direction, axis=1, keepdims=True)
    return np.stack(points, axis=1)


def dome_and_rays():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    phi = np.linspace(0, np.pi, 200)
    ax1.plot(R * np.cos(phi), DRUM_HEIGHT + R * np.sin(phi), color="k", linewidth=2.5)
    for side in (-R, R):
        ax1.plot([side, side], [0, DRUM_HEIGHT], color="k", linewidth=2.5)
    ax1.plot([-R - 1.5, R + 1.5], [0, 0], color="#b49a6a", linewidth=3)
    ax1.plot([-R, R], [DRUM_HEIGHT, DRUM_HEIGHT], color=BLUE, linewidth=2)
    ax1.text(0, DRUM_HEIGHT + 0.4, "sound room floor", ha="center", color=BLUE)
    for x0 in (-3.5, 1.5):
        ax1.add_patch(plt.Rectangle((x0, DRUM_HEIGHT), 1.8, 0.3, color=ORANGE))
    ax1.text(0, -1.4, f"16.8 m (55 ft) across, 11.6 m (38 ft) tall", ha="center",
             color=GREY)
    ax1.set_aspect("equal")
    ax1.set_ylim(-2, 12.5)
    ax1.set_title("The dome to scale (two people lying on the floor)")
    ax1.axis("off")

    source = np.array([1.0, 0.0])
    angles = np.linspace(0, 2 * np.pi, 120, endpoint=False) + np.pi / 120
    paths = trace_rays_2d(source, angles, 1)
    draw_dome(ax2, full_circle=True)
    ax2.add_collection(LineCollection(paths[:, 0:2], colors=ORANGE, linewidths=0.6,
                                      alpha=0.5))
    ax2.add_collection(LineCollection(paths[:, 1:3], colors=BLUE, linewidths=0.6,
                                      alpha=0.5))
    ax2.scatter(*source, s=70, color=ORANGE, zorder=4, label="source, 1 m from centre")
    ax2.scatter(-1, 0, s=150, marker="*", color=BLUE, zorder=4, label="mirror point")
    ax2.set_xlim(-R * 1.05, R * 1.05)
    ax2.set_ylim(-R * 1.05, R * 1.05)
    ax2.legend(loc="upper right", fontsize=8)
    ax2.set_title("Rays out (orange) and after one reflection (blue)")
    save(fig, "01_dome_and_rays.png")


def wall_sum_2d(source, receivers, freq_hz, n_wall=1600):
    # First reflection from the whole wall in the 2D slice (notebook 01)
    k = 2 * np.pi * freq_hz / SPEED_OF_SOUND
    angle = (np.arange(n_wall) + 0.5) * 2 * np.pi / n_wall
    wall = R * np.column_stack([np.cos(angle), np.sin(angle)])
    to_wall = wall - source
    r1 = np.linalg.norm(to_wall, axis=1)
    from_wall = receivers[:, None, :] - wall
    r2 = np.linalg.norm(from_wall, axis=2)
    inward = -wall / R
    obliquity = (np.sum(to_wall * -inward, axis=1) / r1
                 + np.sum(from_wall * inward, axis=2) / r2) / 2
    terms = (obliquity * 2 * np.pi * R / n_wall * np.sqrt(k / (2 * np.pi))
             / np.sqrt(r1 * r2) * np.exp(1j * (k * (r1 + r2) - np.pi / 4)))
    return terms, wall, r1 + r2


def interference():
    source = np.array([1.0, 0.0])
    freq_hz = 500
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.9),
                                   gridspec_kw={"width_ratios": [1, 1.6]})
    for listener, colour, label in [((-1.0, 0.0), AQUA, "at the mirror point"),
                                    ((-2.0, 0.0), ORANGE, "1 m past it")]:
        terms, wall, _ = wall_sum_2d(source, np.array([listener]), freq_hz)
        chain = np.concatenate([[0], np.cumsum(terms[0])])
        coherence = np.abs(terms.sum()) / np.abs(terms).sum()
        ax1.plot(chain.real, chain.imag, color=colour,
                 label=f"{label}: {coherence:.0%} in step")
        ax1.annotate("", xy=(chain[-1].real, chain[-1].imag), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="-|>", color=colour))
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.legend(fontsize=8, loc="lower left")
    ax1.set_title("Adding the reflections head to tail")

    xs, ys = np.meshgrid(np.linspace(-R, R, 201), np.linspace(0, R, 101))
    inside = xs ** 2 + ys ** 2 < (R - 0.15) ** 2
    points = np.column_stack([xs[inside], ys[inside]])
    field = np.full(xs.shape, np.nan, dtype=complex)
    k = 2 * np.pi * freq_hz / SPEED_OF_SOUND
    direct_r = np.maximum(np.linalg.norm(points - source, axis=1), 0.1)
    values = np.exp(1j * k * direct_r) / np.sqrt(direct_r)
    for start in range(0, len(points), 2000):
        terms, _, _ = wall_sum_2d(source, points[start:start + 2000], freq_hz)
        values[start:start + 2000] += terms.sum(axis=1)
    field[inside] = values
    level = 10 * np.log10(np.abs(field) ** 2)
    level -= np.nanmedian(level)
    image = ax2.imshow(level, origin="lower", extent=[-R, R, 0, R], cmap="magma",
                       vmin=-10, vmax=20)
    draw_dome(ax2)
    ax2.scatter(*source, s=50, color=ORANGE, edgecolor="w", zorder=4)
    ax2.scatter(-1, 0.12, s=120, marker="*", facecolor="none", edgecolor=AQUA, zorder=4)
    fig.colorbar(image, ax=ax2, shrink=0.8, label="dB above room median")
    ax2.set_title("Loudness across the room at 500 Hz")
    save(fig, "02_interference.png")


def echo_and_comb():
    alpha = 0.05
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.6))
    n = np.arange(13)
    amplitude = (-np.sqrt(1 - alpha)) ** n
    colours = np.where(amplitude > 0, BLUE, ORANGE)
    ax1.vlines(n * ROUND_TRIP_S * 1000, 0, amplitude, colors=colours, linewidth=2.5)
    ax1.scatter(n * ROUND_TRIP_S * 1000, amplitude, c=colours, s=20, zorder=3)
    ax1.axhline(0, color=GREY, linewidth=1)
    ax1.set_xlabel("time (ms)")
    ax1.set_ylabel("pulse at the centre")
    ax1.set_title("A clap at the centre returns every 49 ms")

    f = np.linspace(1, 250, 20000)
    response = np.abs(1 / (1 + np.sqrt(1 - alpha)
                           * np.exp(2j * np.pi * f * ROUND_TRIP_S))) ** 2
    ax2.plot(f, 10 * np.log10(response), color=BLUE, linewidth=1.2)
    ax2.set_xlim(0, 250)
    ax2.set_xlabel("frequency (Hz)")
    ax2.set_ylabel("loudness at centre (dB)")
    ax2.set_title("The same echoes as resonances every 20.5 Hz")
    save(fig, "03_echo_and_comb.png")


def bessel_derivative_zero(l, n):
    x = np.linspace(0.01, 60, 12000)
    y = spherical_jn(l, x, derivative=True)
    i = np.flatnonzero(np.sign(y[:-1]) != np.sign(y[1:]))[n - 1]
    return brentq(lambda t: spherical_jn(l, t, derivative=True), x[i], x[i + 1])


def mode_slice(l, m, n, x, y, z):
    kr = bessel_derivative_zero(l, n)
    r = np.sqrt(x ** 2 + y ** 2 + z ** 2)
    cos_theta = np.divide(z, r, out=np.ones_like(r), where=r > 0)
    p = spherical_jn(l, kr / R * r) * lpmv(m, l, cos_theta) * np.cos(m * np.arctan2(y, x))
    p = np.where(r <= R, p, np.nan)
    return p / np.nanmax(np.abs(p)), kr * SPEED_OF_SOUND / (2 * np.pi * R)


def modes():
    sx, sz = np.meshgrid(np.linspace(-R, R, 241), np.linspace(0, R, 121))
    fx, fy = np.meshgrid(np.linspace(-R, R, 201), np.linspace(-R, R, 201))
    fig, axes = plt.subplots(1, 4, figsize=(13, 3.0),
                             gridspec_kw={"width_ratios": [2, 2, 2, 1.1]})
    for ax, (l, m, n, label) in zip(axes[:3], [(1, 1, 1, "slosh"), (0, 0, 3, "breathing"),
                                                (16, 0, 1, "whispering gallery")]):
        p, f = mode_slice(l, m, n, sx, np.zeros_like(sx), sz)
        ax.imshow(p, origin="lower", extent=[-R, R, 0, R], cmap="RdBu_r", vmin=-1, vmax=1)
        draw_dome(ax)
        ax.set_title(f"{label}, {f:.1f} Hz (side)", fontsize=10)
    p, f = mode_slice(16, 16, 1, fx, fy, np.zeros_like(fx))
    axes[3].imshow(p, origin="lower", extent=[-R, R, -R, R], cmap="RdBu_r", vmin=-1, vmax=1)
    phi = np.linspace(0, 2 * np.pi, 300)
    axes[3].plot(R * np.cos(phi), R * np.sin(phi), color="k", linewidth=1.5)
    axes[3].set_aspect("equal")
    axes[3].axis("off")
    axes[3].set_title(f"gallery, {f:.1f} Hz (floor)", fontsize=10)
    save(fig, "04_modes.png")


def focus_3d():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
    f = np.linspace(50, 2000, 400)
    k = 2 * np.pi * f / SPEED_OF_SOUND
    ax1.plot(f, 20 * np.log10(2 * k), color=BLUE, label="full dome (3D)")
    ax1.plot(f, 20 * np.log10(np.sqrt(2 * np.pi * k)), color=GREY, linestyle="--",
             label="2D slice")
    ax1.set_xlabel("frequency (Hz)")
    ax1.set_ylabel("dB above direct sound at 1 m")
    ax1.set_title("Echo of your own voice at the centre")
    ax1.legend()

    x = np.linspace(-1.2, 1.2, 600)  # distance from the focus in wavelengths
    kx = 2 * np.pi * x
    ax2.plot(x, np.sinc(2 * x) ** 2, color=BLUE, label="3D: width 0.44 λ")
    ax2.plot(x, j0(kx) ** 2, color=GREY, linestyle="--", label="2D: width 0.36 λ")
    ax2.axhline(0.5, color=GREY, linewidth=0.8, linestyle=":")
    ax2.set_xlabel("distance from the focus (wavelengths)")
    ax2.set_ylabel("loudness (peak = 1)")
    ax2.set_title("Shape of a perfect focus")
    ax2.legend(fontsize=8)
    save(fig, "05_focus_3d.png")


def whispering_gallery():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax, half_angle in [(ax1, 10), (ax2, 40)]:
        start = np.array([0.0, -(R - 0.3)])
        angles = np.radians(np.linspace(-half_angle, half_angle, 25))
        paths = trace_rays_2d(start, angles, 14)
        phi = np.linspace(0, 2 * np.pi, 300)
        ax.plot(R * np.cos(phi), R * np.sin(phi), color="k", linewidth=2)
        segments = np.concatenate([paths[:, i:i + 2] for i in range(paths.shape[1] - 1)])
        ax.add_collection(LineCollection(segments, colors=BLUE, linewidths=0.6, alpha=0.5))
        ax.scatter(*start, s=60, color=ORANGE, zorder=4)
        ax.set_aspect("equal")
        ax.set_xlim(-R * 1.05, R * 1.05)
        ax.set_ylim(-R * 1.05, R * 1.05)
        ax.axis("off")
        ax.set_title(f"Whisper 0.3 m from the wall, fan ±{half_angle}° (floor view)",
                     fontsize=10)
    save(fig, "06_whispering_gallery.png")


def singing_bowl():
    fig, axes = plt.subplots(1, 4, figsize=(11, 3.0))
    theta = np.linspace(0, 2 * np.pi, 400)
    base = 2 * 3 / np.sqrt(5)
    for ax, n in zip(axes, [2, 3, 4, 5]):
        ratio = n * (n ** 2 - 1) / np.sqrt(n ** 2 + 1) / base
        ax.plot(np.cos(theta), np.sin(theta), color=GREY, linewidth=1, linestyle="--")
        for sign, colour in [(1, BLUE), (-1, ORANGE)]:
            r = 1 + sign * 0.15 * np.cos(n * theta)
            ax.plot(r * np.cos(theta), r * np.sin(theta), color=colour)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(f"n = {n}: {ratio:.2f} × lowest\n{220 * ratio:.0f} Hz for a 220 Hz bowl",
                     fontsize=10)
    save(fig, "07_singing_bowl.png")


def echograms():
    # Ray tracing in the full sphere, as in notebook 06, for one wall absorption
    rng = np.random.default_rng(0)
    alpha, n_rays, seconds, radius = 0.05, 60000, 0.35, 0.2
    places = {"centre: hear yourself": ((0.0, 0.0, 0.0), (0.25, 0.0, 0.0), BLUE),
              "mirror point": ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), AQUA),
              "off focus": ((1.0, 0.0, 0.0), (-1.0, 2.5, 0.0), ORANGE)}
    fig, axes = plt.subplots(3, 1, figsize=(11, 5.6), sharex=True)
    for ax, (name, (source, listener, colour)) in zip(axes, places.items()):
        listener = np.array(listener)
        direction = rng.normal(size=(n_rays, 3))
        direction /= np.linalg.norm(direction, axis=1, keepdims=True)
        pos = np.tile(source, (n_rays, 1))
        travelled = np.zeros(n_rays)
        times, weights = [], []
        for bounce in range(12):
            b = np.sum(pos * direction, axis=1)
            c = np.sum(pos ** 2, axis=1) - R ** 2
            to_wall = -b + np.sqrt(np.maximum(b * b - c, 0))
            w = listener - pos
            along = np.clip(np.sum(w * direction, axis=1), 0, to_wall)
            miss = np.linalg.norm(w - along[:, None] * direction, axis=1)
            hit = miss < radius
            times.append((travelled[hit] + along[hit]) / SPEED_OF_SOUND)
            weights.append(2 * np.sqrt(radius ** 2 - miss[hit] ** 2) * (1 - alpha) ** bounce)
            pos = pos + to_wall[:, None] * direction
            normal = pos / np.linalg.norm(pos, axis=1, keepdims=True)
            pos = normal * R * (1 - 1e-9)
            direction -= 2 * np.sum(direction * normal, axis=1)[:, None] * normal
            travelled += to_wall
        energy, edges = np.histogram(np.concatenate(times) * 1000, bins=np.arange(0, 301, 1.0),
                                     weights=np.concatenate(weights))
        with np.errstate(divide="ignore"):
            level = 10 * np.log10(energy / energy.max())
        ax.vlines(edges[:-1] + 0.5, -80, level, color=colour, linewidth=1.2)
        for n in range(1, 7):
            ax.axvline(n * ROUND_TRIP_S * 1000, color=GREY, linestyle="--", linewidth=0.7)
        ax.set_ylim(-45, 3)
        ax.set_ylabel("dB")
        ax.set_title(name, fontsize=10, loc="left", color=colour)
    axes[-1].set_xlim(0, 300)
    axes[-1].set_xlabel("time after the sound (ms)")
    save(fig, "08_echograms.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    dome_and_rays()
    interference()
    echo_and_comb()
    modes()
    focus_3d()
    whispering_gallery()
    singing_bowl()
    echograms()
