"""Generate logo circle images with transparent backgrounds into static/."""
from pathlib import Path
import matplotlib.pyplot as plt
from socraticai.visualizations.visualization_util import create_network_circle

STATIC_DIR = Path(__file__).parent / "static"

GENERATE_KWARGS = {
    "num_points": 600,
    "max_connection_distance": 0.25,
    "max_nearby": 5,
    "seed": 42,
    "circle_radius": 1,
    "circle_width": 0.5,
}

def save_circle(output_path, bg_color, point_grey, line_color=None):
    f, ax = plt.subplots(figsize=(5, 5), facecolor=bg_color)
    ax.set_facecolor(bg_color)
    create_network_circle(
        ax=ax,
        points_color=[point_grey] * 3,
        line_color=line_color or "white",
        point_size=2,
        alpha=0.6,
        linewidth=0.25,
        **GENERATE_KWARGS,
    )
    f.savefig(output_path, dpi=400, transparent=True, bbox_inches="tight", pad_inches=0)
    plt.close(f)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    STATIC_DIR.mkdir(exist_ok=True)
    save_circle(STATIC_DIR / "graph_whitedots.png", bg_color="black", point_grey=0.7)
    save_circle(STATIC_DIR / "graph_blackdots.png", bg_color="white", point_grey=0.0, line_color="black")
