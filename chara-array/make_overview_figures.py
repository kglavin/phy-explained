"""Generate the figures used by 00_overview.md.

Run from the chara-array directory:
    .venv/bin/python make_overview_figures.py
"""
import csv
import io
import itertools
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.optimize import curve_fit
from scipy.special import j1, jv

OUT = Path("figures/00_overview")
RAD_TO_MAS = 180 / np.pi * 3600 * 1000
MAS_TO_RAD = 1 / RAD_TO_MAS
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

# Telescope positions (east, north, up) in metres relative to S1, ten Brummelaar et al. (2005)
STATIONS = {
    "S1": (0.000, 0.000, 0.000),
    "S2": (-5.748, 33.581, 0.637),
    "E1": (125.333, 305.928, -5.919),
    "E2": (70.389, 269.715, -2.803),
    "W1": (-175.068, 216.327, -10.798),
    "W2": (-69.085, 199.342, 0.471),
}
LATITUDE = np.radians(34.2244)
H_BAND = 1.65e-6


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, bbox_inches="tight")
    plt.close(fig)
    print("wrote", OUT / name)


def project(enu, hour_angle, dec):
    e, n, up = enu
    x = -np.sin(LATITUDE) * n + np.cos(LATITUDE) * up
    z = np.cos(LATITUDE) * n + np.sin(LATITUDE) * up
    u = np.sin(hour_angle) * x + np.cos(hour_angle) * e
    v = -np.sin(dec) * np.cos(hour_angle) * x + np.sin(dec) * np.sin(hour_angle) * e + np.cos(dec) * z
    w = np.cos(dec) * np.cos(hour_angle) * x - np.cos(dec) * np.sin(hour_angle) * e + np.sin(dec) * z
    return u, v, w


def baseline(a, b):
    return np.subtract(STATIONS[b], STATIONS[a])


def star_sizes():
    stars = {"Betelgeuse": 44.0, "Arcturus": 21.0, "Sirius A": 6.0, "Vega": 3.3,
             "Polaris": 3.1, "Proxima Cen": 1.0, "Sun at 10 pc": 0.93}
    limits = {"Atmospheric blur (~1\")": 1000, "One 1 m CHARA telescope": 1.22 * H_BAND / 1.0 * RAD_TO_MAS,
              "Hubble (2.4 m, visible)": 1.22 * 0.5e-6 / 2.4 * RAD_TO_MAS,
              "Keck (10 m, infrared)": 1.22 * H_BAND / 10 * RAD_TO_MAS,
              "CHARA array, infrared": H_BAND / (2 * 331) * RAD_TO_MAS,
              "CHARA array, visible": 0.5e-6 / (2 * 331) * RAD_TO_MAS}
    rows = sorted([(v, k, "star") for k, v in stars.items()] +
                  [(v, k, "chara" if "array" in k else "single") for k, v in limits.items()])
    style = {"star": dict(color=BLUE, marker="o", label="Star size"),
             "single": dict(color=GREY, marker="s", label="Single telescope or atmosphere limit"),
             "chara": dict(color=ORANGE, marker="D", label="CHARA array limit")}
    fig, ax = plt.subplots(figsize=(8, 5))
    for kind, st in style.items():
        pts = [(v, i) for i, (v, _, k) in enumerate(rows) if k == kind]
        ax.scatter(*zip(*pts), s=55, zorder=3, **st)
    ax.set_yticks(range(len(rows)), [name for _, name, _ in rows])
    ax.set_xscale("log")
    ax.set_xlabel("Angular size (milliarcseconds, log scale)")
    ax.set_title("Stars are smaller than any single telescope can see")
    ax.legend(fontsize=8, loc="lower right")
    ax.grid(axis="y", visible=False)
    save(fig, "01_star_sizes.png")


def aperture_fringes():
    n, dx = 1024, 0.05
    axis = (np.arange(n) - n / 2) * dx
    px, py = np.meshgrid(axis, axis)
    disk = lambda cx: (np.hypot(px - cx, py) <= 0.5).astype(float)
    pix_mas = H_BAND / (n * dx) * RAD_TO_MAS
    half = 120
    crop = slice(n // 2 - half, n // 2 + half)
    fig, axes = plt.subplots(2, 2, figsize=(8, 7.5))
    for row, (pupil, name) in enumerate([(disk(0), "One mirror"), (disk(-2.5) + disk(2.5), "Two mirrors 5 m apart")]):
        axes[row, 0].imshow(pupil, extent=[axis[0], axis[-1]] * 2, origin="lower", cmap="gray")
        axes[row, 0].set_xlim(-6, 6)
        axes[row, 0].set_ylim(-6, 6)
        axes[row, 0].set_title(name, fontsize=10)
        axes[row, 0].set_xlabel("m")
        field = np.fft.fftshift(np.fft.fft2(np.fft.ifftshift(pupil)))
        image = (np.abs(field) ** 2)[crop, crop]
        image /= image.max()
        extent = half * pix_mas
        axes[row, 1].imshow(image ** 0.4, extent=[-extent, extent] * 2, origin="lower", cmap="inferno")
        axes[row, 1].set_title("Image of a single star", fontsize=10)
        axes[row, 1].set_xlabel("milliarcseconds")
        for ax in axes[row]:
            ax.grid(False)
    save(fig, "02_aperture_fringes.png")


def wavefront_and_packet():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1.1, 1]})
    b, theta = 331.0, np.radians(30)
    t1, t2 = np.array([-b / 2, 0]), np.array([b / 2, 0])
    toward = np.array([np.sin(theta), np.cos(theta)])
    along = np.array([np.cos(theta), -np.sin(theta)])
    ax1.axhline(0, color=GREY, lw=1)
    ax1.scatter(*zip(t1, t2), s=110, marker="s", color=BLUE, zorder=3)
    for t, label in ((t1, "T1"), (t2, "T2")):
        ax1.annotate(label, t, xytext=(0, -16), textcoords="offset points", ha="center")
        ax1.annotate("", xy=t, xytext=t + 1.1 * b * toward, arrowprops=dict(arrowstyle="->", color=GREY))
    front = np.array([t2 - 0.9 * b * along, t2 + 0.9 * b * along])
    ax1.plot(front[:, 0], front[:, 1], color=GREY, ls="--", lw=1.2, label="wavefront from the star")
    foot = t1 + b * np.sin(theta) * toward
    ax1.plot([t1[0], foot[0]], [t1[1], foot[1]], color=ORANGE, lw=3,
             label=f"extra path to T1: {b * np.sin(theta):.0f} m")
    ax1.set_aspect("equal")
    ax1.set_xlim(-1.1 * b, 1.1 * b)
    ax1.set_ylim(-0.15 * b, 0.95 * b)
    ax1.set_xlabel("m")
    ax1.set_title("A star 30° from overhead, 331 m baseline", fontsize=10)
    ax1.legend(fontsize=8, loc="upper left")

    wavelengths = np.linspace(1.5, 1.8, 301)
    opd = np.linspace(-25, 25, 3001)
    packet = (1 + np.cos(2 * np.pi * opd[None, :] / wavelengths[:, None])).mean(axis=0)
    ax2.plot(opd, packet, color=BLUE)
    ax2.set_xlabel("Path difference after the delay line (µm)")
    ax2.set_ylabel("Detected brightness")
    ax2.set_title("Fringes appear only when paths match to a few µm", fontsize=10)
    save(fig, "03_path_difference.png")


def sky_ruler():
    n, fov = 256, 8.0
    axis = (np.arange(n) - n / 2) * (fov / n)
    x, y = np.meshgrid(axis, axis)
    b = 200.0
    stripes = 1 + np.cos(2 * np.pi * b * x * MAS_TO_RAD / H_BAND)
    fig, axes = plt.subplots(2, 3, figsize=(10, 6.6))
    for row, diameter in enumerate((0.6, 2.2)):
        star = (np.hypot(x, y) <= diameter / 2).astype(float)
        vis = abs((star * np.exp(-2j * np.pi * b * x * MAS_TO_RAD / H_BAND)).sum() / star.sum())
        panels = [(star, f"Star {diameter} mas across", "inferno"),
                  (stripes, f"Fringe stripes ({H_BAND / b * RAD_TO_MAS:.1f} mas apart)", "gray"),
                  (star * stripes / 2, f"Star × stripes: contrast V = {vis:.2f}", "inferno")]
        for ax, (img, title, cmap) in zip(axes[row], panels):
            ax.imshow(img, extent=[-fov / 2, fov / 2] * 2, origin="lower", cmap=cmap, vmin=0, vmax=img.max())
            ax.set_title(title, fontsize=9)
            ax.set_xlabel("mas")
            ax.grid(False)
    save(fig, "04_sky_ruler.png")


def delta_cep_fit():
    data_dir = Path("data/delta_cep")
    if not (data_dir / ".complete").exists():
        query = ("SELECT access_url FROM oidb WHERE facility_name = 'CHARA' AND data_rights = 'public' "
                 "AND calib_level = 3 AND target_name = 'HD213306'")
        params = urllib.parse.urlencode({"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv",
                                         "QUERY": query}).encode()
        with urllib.request.urlopen("https://tap.jmmc.fr/vollt/tap/sync", data=params, timeout=60) as r:
            rows = list(csv.DictReader(io.StringIO(r.read().decode())))
        data_dir.mkdir(parents=True, exist_ok=True)

        def fetch(row):
            url = urllib.parse.urljoin("https://oidb.jmmc.fr", row["access_url"])
            target = data_dir / Path(urllib.parse.urlparse(url).path).name
            if not target.exists():
                urllib.request.urlretrieve(url, target)

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(fetch, rows))
        (data_dir / ".complete").touch()

    sf, v2, err = [], [], []
    for path in sorted(data_dir.glob("*.oifits")):
        with fits.open(path) as hdul:
            wl = hdul["OI_WAVELENGTH"].data["EFF_WAVE"][0]
            for row in hdul["OI_VIS2"].data:
                if not row["FLAG"]:
                    sf.append(np.hypot(row["UCOORD"], row["VCOORD"]) / wl)
                    v2.append(row["VIS2DATA"])
                    err.append(row["VIS2ERR"])
    sf, v2, err = map(np.array, (sf, v2, err))

    def model(s, theta, u=0.6):
        xx = np.pi * theta * MAS_TO_RAD * np.maximum(s, 1e-9)
        num = (1 - u) * j1(xx) / xx + u * np.sqrt(np.pi / 2) * jv(1.5, xx) / xx ** 1.5
        return (num / ((1 - u) / 2 + u / 3)) ** 2

    (theta,), _ = curve_fit(model, sf, v2, p0=[1.5], sigma=err)
    curve = np.linspace(1e6, 210e6, 400)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.errorbar(sf / 1e6, v2, yerr=err, fmt="o", ms=3, color=BLUE, ecolor="#9ec5f4",
                label="CHARA/VEGA measurements")
    ax.plot(curve / 1e6, model(curve, theta), color=ORANGE, label=f"best-fit star disk: {theta:.2f} mas")
    ax.set_ylim(-0.05, 1.05)
    ax.set_xlabel("Baseline ÷ wavelength (millions of wavelengths)")
    ax.set_ylabel("Fringe contrast squared, V²")
    ax.set_title("δ Cephei: fringe contrast falls as baselines get longer", fontsize=10)
    ax.legend(fontsize=8)
    save(fig, "05_delta_cep.png")
    return theta


def uv_coverage():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))
    for a, b in itertools.combinations(STATIONS, 2):
        (e1, n1, _), (e2, n2, _) = STATIONS[a], STATIONS[b]
        ax1.plot([e1, e2], [n1, n2], color="#c3c2b7", lw=0.8)
    for name, (e, n, _) in STATIONS.items():
        ax1.scatter(e, n, s=110, marker="s", color=BLUE, zorder=3)
        ax1.annotate(name, (e, n), xytext=(8, 6), textcoords="offset points")
    ax1.set_aspect("equal")
    ax1.set_xlabel("East (m)")
    ax1.set_ylabel("North (m)")
    ax1.set_title("Six telescopes, 15 baselines", fontsize=10)

    dec = np.radians(40)
    ha = np.radians(15 * np.linspace(-3, 3, 300))
    for a, b in itertools.combinations(STATIONS, 2):
        u, v, _ = project(baseline(a, b), ha, dec)
        ax2.plot(u, v, color=BLUE, lw=1.5)
        ax2.plot(-u, -v, color=BLUE, lw=1.5, alpha=0.45)
    ax2.set_aspect("equal")
    ax2.set_xlim(-340, 340)
    ax2.set_ylim(-340, 340)
    ax2.set_xlabel("East-west (m)")
    ax2.set_ylabel("North-south (m)")
    ax2.set_title("Baselines seen from the star over 6 hours (uv coverage)", fontsize=10)
    save(fig, "06_uv_coverage.png")


def delay_over_night():
    dec = np.radians(40)
    hours = np.linspace(-4, 4, 400)
    ha = np.radians(15 * hours)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    for (a, b), colour in zip([("S1", "E1"), ("E1", "W1"), ("S1", "S2")], [ORANGE, BLUE, AQUA]):
        _, _, w = project(baseline(a, b), ha, dec)
        rate = np.gradient(w, hours * 3600) * 1000  # mm/s
        ax1.plot(hours, w, color=colour, label=f"{a}-{b}")
        ax2.plot(hours, rate, color=colour, label=f"{a}-{b}")
    ax1.set_xlabel("Hours from the star's highest point")
    ax1.set_ylabel("Delay to add (m)")
    ax1.set_title("Path difference the delay lines must cancel", fontsize=10)
    ax1.legend(fontsize=8)
    ax2.set_xlabel("Hours from the star's highest point")
    ax2.set_ylabel("Speed (mm/s)")
    ax2.set_title("How fast the delay must change", fontsize=10)
    ax2.legend(fontsize=8)
    save(fig, "07_delay_lines.png")


def closure_phase():
    rng = np.random.default_rng(3)
    t = np.linspace(0, 2, 400)  # seconds
    # Atmospheric delay above each telescope, as a random walk in radians of fringe phase
    piston = np.cumsum(rng.normal(0, 0.35, (3, len(t))), axis=1)
    true = np.array([40.0, -25.0, -5.0])  # true phases of baselines 1-2, 2-3, 3-1 (degrees)
    measured = np.degrees([piston[0] - piston[1], piston[1] - piston[2], piston[2] - piston[0]])
    measured += true[:, None]
    wrap = lambda p: (p + 180) % 360 - 180
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 5.6), sharex=True)
    for row, colour, label in zip(wrap(measured), [BLUE, ORANGE, AQUA], ["T1-T2", "T2-T3", "T3-T1"]):
        ax1.scatter(t, row, s=3, color=colour, label=label)
    ax1.set_ylim(-185, 185)
    ax1.set_yticks([-180, 0, 180])
    ax1.set_ylabel("Phase (°)")
    ax1.set_title("Each baseline's fringe phase: scrambled by the atmosphere", fontsize=10)
    ax1.legend(fontsize=8, loc="upper right", markerscale=3)
    ax2.plot(t, wrap(measured.sum(axis=0)), color=BLUE)
    ax2.set_ylim(-185, 185)
    ax2.set_yticks([-180, 0, 180])
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Phase (°)")
    ax2.set_title(f"Sum around the triangle (closure phase): steady at {true.sum():.0f}°", fontsize=10)
    save(fig, "08_closure_phase.png")


def binary_image():
    stars = [(-0.6, -0.6, 1.0), (1.0, 1.0, 0.5)]  # x (mas), y (mas), flux
    dec = np.radians(40)
    ha = np.radians(15 * np.linspace(-3, 3, 36))
    us, vs = [], []
    for a, b in itertools.combinations(STATIONS, 2):
        u, v, _ = project(baseline(a, b), ha, dec)
        us += [u, -u]
        vs += [v, -v]
    u, v = np.concatenate(us) / H_BAND, np.concatenate(vs) / H_BAND
    vis = sum(f * np.exp(-2j * np.pi * (u * x + v * y) * MAS_TO_RAD) for x, y, f in stars) / 1.5
    axis = np.linspace(-4, 4, 161)
    ex = np.exp(2j * np.pi * np.outer(axis * MAS_TO_RAD, u))
    ey = np.exp(2j * np.pi * np.outer(axis * MAS_TO_RAD, v))
    dirty = np.real((ey * vis) @ ex.T) / len(u)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.5, 4.6))
    ax1.set_facecolor("black")
    for x, y, f in stars:
        ax1.scatter(x, y, s=260 * f, color="#f7f2a0")
    ax1.set_xlim(-4, 4)
    ax1.set_ylim(-4, 4)
    ax1.set_aspect("equal")
    ax1.set_title("True sky: a binary star", fontsize=10)
    ax1.set_xlabel("mas")
    ax1.grid(False)
    lim = np.abs(dirty).max()
    ax2.imshow(dirty, extent=[-4, 4, -4, 4], origin="lower", cmap="RdBu_r", vmin=-lim, vmax=lim)
    ax2.set_title("Raw image from 6 telescopes, 6 hours", fontsize=10)
    ax2.set_xlabel("mas")
    ax2.grid(False)
    save(fig, "09_binary_image.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    star_sizes()
    aperture_fringes()
    wavefront_and_packet()
    sky_ruler()
    print(f"δ Cep diameter {delta_cep_fit():.3f} mas")
    uv_coverage()
    delay_over_night()
    closure_phase()
    binary_image()
