"""Generate animated logo GIFs: drift (1), pulse (2), rotation+pulse (2+4)."""
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.animation as animation

from socraticai.visualizations.visualization_util import generate_circle_data

STATIC_DIR = Path(__file__).parent / "static"

N_FRAMES = 60
FPS = 20
DPI = 100
BG = "black"
GREY = 0.7
BASE_ALPHA = 0.2
PULSE_PEAK = 0.85
PULSE_SIGMA = 0.45      # radians — width of the glowing wave front
DRIFT_AMP = 0.04        # max node displacement
LINEWIDTH = 0.3

CIRCLE_KW = dict(num_points=600, circle_radius=1.0, circle_width=0.5, seed=42)
MAX_DIST = 0.25
MAX_NEARBY = 5
LIM = 1.4


# ── Helpers ──────────────────────────────────────────────────────────────────

def _connect(src, tgt, rng, max_dist=MAX_DIST, max_nearby=MAX_NEARBY):
    """Segments [(p1, p2), ...] connecting src points to nearby tgt points."""
    segs = []
    for x, y in src:
        d = np.hypot(tgt[:, 0] - x, tgt[:, 1] - y)
        idx = np.where((d < max_dist) & (d > 0))[0]
        if not len(idx):
            continue
        chosen = rng.choice(idx, size=min(max_nearby, len(idx)), replace=False)
        segs.extend([[(x, y), tuple(tgt[j])] for j in chosen])
    return segs


def _connect_indices(pts, rng, max_dist=MAX_DIST, max_nearby=MAX_NEARBY):
    """Same as _connect but returns (i, j) index pairs instead of coordinates."""
    pairs = []
    for i, (x, y) in enumerate(pts):
        d = np.hypot(pts[:, 0] - x, pts[:, 1] - y)
        idx = np.where((d < max_dist) & (d > 0))[0]
        if not len(idx):
            continue
        chosen = rng.choice(idx, size=min(max_nearby, len(idx)), replace=False)
        pairs.extend([(i, int(j)) for j in chosen])
    return pairs


def _pairs_to_segs(pairs, pts):
    return [[(pts[i, 0], pts[i, 1]), (pts[j, 0], pts[j, 1])] for i, j in pairs]


def _midangles(segs):
    a = np.array(segs)                  # (N, 2, 2)
    mx = (a[:, 0, 0] + a[:, 1, 0]) / 2
    my = (a[:, 0, 1] + a[:, 1, 1]) / 2
    return np.arctan2(my, mx)


def _rgba(n, alpha):
    """(N, 4) grey color array; alpha can be scalar or length-N array."""
    c = np.full((n, 4), GREY)
    c[:, 3] = alpha
    return c


def _pulse_alpha(angles, wave):
    diff = ((angles - wave + np.pi) % (2 * np.pi)) - np.pi
    return BASE_ALPHA + (PULSE_PEAK - BASE_ALPHA) * np.exp(-diff ** 2 / (2 * PULSE_SIGMA ** 2))


def _pulse_color_opaque(angles, wave, base_bright=0.12, peak_bright=1.0):
    """Vary brightness instead of alpha — safe for transparent-background GIFs."""
    diff = ((angles - wave + np.pi) % (2 * np.pi)) - np.pi
    brightness = base_bright + (peak_bright - base_bright) * np.exp(-diff ** 2 / (2 * PULSE_SIGMA ** 2))
    c = np.zeros((len(angles), 4))
    c[:, :3] = brightness[:, np.newaxis]
    c[:, 3] = 1.0
    return c


def _rotate(pts, angle):
    c, s = np.cos(angle), np.sin(angle)
    return pts @ np.array([[c, -s], [s, c]]).T


def _setup_fig():
    fig, ax = plt.subplots(figsize=(5, 5), facecolor=BG)
    ax.set_facecolor(BG)
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def _scatter(ax, pts):
    return ax.scatter(pts[:, 0], pts[:, 1],
                      color=[GREY, GREY, GREY], s=2, alpha=0.6, zorder=3)


def _save(anim, path, fig, transparent=False):
    kwargs = {"savefig_kwargs": {"transparent": True, "facecolor": "none"}} if transparent else {}
    anim.save(path, writer="pillow", fps=FPS, dpi=DPI, **kwargs)
    plt.close(fig)
    print(f"Saved {path}")


# ── 1: Drift ─────────────────────────────────────────────────────────────────

def make_drift_gif(out_path):
    main, outer, inner, rng = generate_circle_data(**CIRCLE_KW)
    pts0 = np.vstack([main, outer, inner])
    n = len(pts0)

    # each node drifts in a fixed random direction with a unique phase
    drift_phase = rng.uniform(0, 2 * np.pi, n)
    drift_dir = rng.uniform(0, 2 * np.pi, n)
    drift_dx = np.cos(drift_dir)
    drift_dy = np.sin(drift_dir)

    fig, ax = _setup_fig()
    sc = _scatter(ax, pts0)

    segs0 = _connect(pts0, pts0, rng)
    lc = LineCollection(segs0, colors=_rgba(len(segs0), BASE_ALPHA + 0.2), linewidths=LINEWIDTH)
    ax.add_collection(lc)

    def update(frame):
        t = frame / N_FRAMES
        d = DRIFT_AMP * np.sin(2 * np.pi * t + drift_phase)
        pts = pts0 + np.column_stack([drift_dx * d, drift_dy * d])
        sc.set_offsets(pts)
        segs = _connect(pts, pts, np.random.default_rng(frame))
        lc.set_segments(segs)
        lc.set_colors(_rgba(len(segs), BASE_ALPHA + 0.2))

    anim = animation.FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 // FPS)
    _save(anim, out_path, fig)


# ── 2: Pulse ──────────────────────────────────────────────────────────────────

def make_pulse_gif(out_path):
    main, outer, inner, rng = generate_circle_data(**CIRCLE_KW)
    pts = np.vstack([main, outer, inner])
    segs = _connect(pts, pts, rng)
    angles = _midangles(segs)

    fig, ax = _setup_fig()
    _scatter(ax, pts)
    lc = LineCollection(segs, colors=_rgba(len(segs), BASE_ALPHA), linewidths=LINEWIDTH)
    ax.add_collection(lc)

    def update(frame):
        wave = 2 * np.pi * frame / N_FRAMES
        lc.set_colors(_rgba(len(segs), _pulse_alpha(angles, wave)))

    anim = animation.FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 // FPS)
    _save(anim, out_path, fig)


# ── 1+2: Drift + Pulse ────────────────────────────────────────────────────────

VARIANTS = {
    # dot_color, edge_base_bright, edge_peak_bright
    "white": ([GREY, GREY, GREY], 0.12, 1.0),
    "black": ([0.0, 0.0, 0.0],   0.78, 0.0),
}

def make_drift_pulse_gif(out_path, variant="white"):
    """Transparent-background animated network. variant='white' for dark bg, 'black' for light bg."""
    dot_color, base_bright, peak_bright = VARIANTS[variant]

    main, outer, inner, rng = generate_circle_data(**CIRCLE_KW)
    pts0 = np.vstack([main, outer, inner])
    n = len(pts0)

    drift_phase = rng.uniform(0, 2 * np.pi, n)
    drift_dir = rng.uniform(0, 2 * np.pi, n)
    drift_dx = np.cos(drift_dir)
    drift_dy = np.sin(drift_dir)

    # fixed topology — same pairs every frame, only coordinates change
    pairs = _connect_indices(pts0, rng)

    fig, ax = plt.subplots(figsize=(5, 5), facecolor="none")
    ax.set_facecolor("none")
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_aspect("equal")
    ax.axis("off")

    sc = ax.scatter(pts0[:, 0], pts0[:, 1], color=dot_color, s=2, alpha=1.0, zorder=3)

    segs0 = _pairs_to_segs(pairs, pts0)
    colors0 = _pulse_color_opaque(_midangles(segs0), 0, base_bright, peak_bright)
    lc = LineCollection(segs0, colors=colors0, linewidths=LINEWIDTH)
    ax.add_collection(lc)

    def update(frame):
        t = frame / N_FRAMES
        d = DRIFT_AMP * np.sin(2 * np.pi * t + drift_phase)
        pts = pts0 + np.column_stack([drift_dx * d, drift_dy * d])
        sc.set_offsets(pts)
        segs = _pairs_to_segs(pairs, pts)
        wave = 2 * np.pi * frame / N_FRAMES
        lc.set_segments(segs)
        lc.set_colors(_pulse_color_opaque(_midangles(segs), wave, base_bright, peak_bright))

    anim = animation.FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 // FPS)
    _save(anim, out_path, fig, transparent=True)


# ── 2+4: Rotation + Pulse ─────────────────────────────────────────────────────

def make_rotation_pulse_gif(out_path):
    main, outer, inner, rng = generate_circle_data(**CIRCLE_KW)

    # main-band connections are fixed; only cross-ring connections rewire
    main_segs = _connect(main, main, rng)
    main_angles = _midangles(main_segs)

    fig, ax = _setup_fig()
    sc = _scatter(ax, np.vstack([main, outer, inner]))

    lc_main = LineCollection(main_segs,
                              colors=_rgba(len(main_segs), BASE_ALPHA),
                              linewidths=LINEWIDTH)
    ax.add_collection(lc_main)

    # placeholder cross-ring LineCollection (updated every frame)
    lc_cross = LineCollection([[(0, 0), (0, 0)]],
                               colors=_rgba(1, BASE_ALPHA),
                               linewidths=LINEWIDTH)
    ax.add_collection(lc_cross)

    def update(frame):
        t = frame / N_FRAMES
        outer_r = _rotate(outer,  2 * np.pi * t)   # CCW full revolution
        inner_r = _rotate(inner, -2 * np.pi * t)   # CW full revolution

        sc.set_offsets(np.vstack([main, outer_r, inner_r]))

        # pulse sweeps around the main band
        wave = 2 * np.pi * frame / N_FRAMES
        lc_main.set_colors(_rgba(len(main_segs), _pulse_alpha(main_angles, wave)))

        # rewire outer→main and inner→main as rings rotate
        frame_rng = np.random.default_rng(frame)
        cross = (_connect(outer_r, main, frame_rng, MAX_DIST, 2)
                 + _connect(inner_r, main, frame_rng, MAX_DIST, 2))
        if cross:
            lc_cross.set_segments(cross)
            lc_cross.set_colors(_rgba(len(cross), BASE_ALPHA + 0.15))

    anim = animation.FuncAnimation(fig, update, frames=N_FRAMES, interval=1000 // FPS)
    _save(anim, out_path, fig)


if __name__ == "__main__":
    STATIC_DIR.mkdir(exist_ok=True)
    print("Generating drift animation...")
    make_drift_gif(STATIC_DIR / "anim_drift.gif")
    print("Generating pulse animation...")
    make_pulse_gif(STATIC_DIR / "anim_pulse.gif")
    print("Generating rotation+pulse animation...")
    make_rotation_pulse_gif(STATIC_DIR / "anim_rotation_pulse.gif")
    print("Generating drift+pulse (whitedots, transparent)...")
    make_drift_pulse_gif(STATIC_DIR / "anim_drift_pulse_whitedots.gif", variant="white")
    print("Generating drift+pulse (blackdots, transparent)...")
    make_drift_pulse_gif(STATIC_DIR / "anim_drift_pulse_blackdots.gif", variant="black")
