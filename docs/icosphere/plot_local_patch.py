#!/usr/bin/env python3
"""Figure 1 — local dual patch: one pentagon with 5 neighbouring hexagons.

Validates the ``attach_along_edge`` formula and shows the 5-spoke
dual structure (pentagon-centroid → hexagon-centroid) that
corresponds to one degree-5 vertex of the pentakis dodecahedron.
"""

from __future__ import annotations

import argparse
import os
import sys

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon as PltPolygon

# --- ensure sibling-module imports work regardless of CWD ----------------
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icosphere_geometry import (
    attach_along_edge,
    create_regular_polygon,
)

# --- colours ---------------------------------------------------------------
PENTAGON_COLOR = "#FF9999"  # 淡粉紅 — 五邊形
HEXAGON_COLOR = "#E6F2FF"  # 淡藍 — 六邊形
DUAL_COLOR = "#FF8C00"  # 亮橙 — 對偶邊
PENTAGON_MARKER = "#C0392B"  # 暗紅 — 五邊形中心
HEXAGON_MARKER = "#1F618D"  # 暗藍 — 六邊形中心


def draw_local_patch(fig=None, ax=None):
    """Draw one pentagon surrounded by 5 hexagons with dual spokes.

    Args:
        fig: Optional existing figure.
        ax: Optional existing axes.

    Returns:
        (fig, ax)
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(9, 9))

    # 中心五邊形：外接圓半徑 r = L / (2 sin(π/5))，邊長 L=1
    R5 = 1.0 / (2.0 * np.sin(np.pi / 5))
    root = create_regular_polygon(5, R5, start_angle=np.pi / 2)
    polys = [(5, root)]
    cents = [root.mean(axis=0)]
    for i in range(5):
        v, _ = attach_along_edge(root[i], root[(i + 1) % 5], 6)
        polys.append((6, v))
        cents.append(v.mean(axis=0))

    # 對偶邊：五輻射（中心 → 六邊形） + 六邊形環（相鄰六邊形間）
    dual = [(cents[0], cents[i + 1]) for i in range(5)]
    dual += [(cents[i + 1], cents[(i + 1) % 5 + 1]) for i in range(5)]

    ax.set_aspect("equal")
    ax.axis("off")
    for (n, v), _ in zip(polys, cents):
        ax.add_patch(
            PltPolygon(
                v,
                closed=True,
                facecolor=(PENTAGON_COLOR if n == 5 else HEXAGON_COLOR),
                edgecolor="black",
                linewidth=2.0,
                alpha=0.85,
                zorder=2,
            )
        )
    for p1, p2 in dual:
        ax.plot(
            [p1[0], p2[0]],
            [p1[1], p2[1]],
            color=DUAL_COLOR,
            linestyle="--",
            linewidth=2.5,
            zorder=3,
        )
    for (n, _), c in zip(polys, cents):
        ax.plot(
            c[0],
            c[1],
            "o",
            color=(PENTAGON_MARKER if n == 5 else HEXAGON_MARKER),
            markersize=7,
            zorder=4,
        )

    pts = np.vstack([v for _, v in polys])
    ax.set_xlim(pts[:, 0].min() - 0.9, pts[:, 0].max() + 0.9)
    ax.set_ylim(pts[:, 1].min() - 1.6, pts[:, 1].max() + 0.9)

    # legend
    handles = [
        mpatches.Patch(
            facecolor=PENTAGON_COLOR,
            edgecolor="black",
            label="Pentagon (1)",
        ),
        mpatches.Patch(
            facecolor=HEXAGON_COLOR,
            edgecolor="black",
            label="Hexagon (5)",
        ),
        Line2D(
            [0],
            [0],
            color=DUAL_COLOR,
            ls="--",
            lw=2.5,
            label="Dual edge (face centroids)",
        ),
    ]
    ax.legend(handles=handles, loc="lower right", fontsize=9)

    ax.set_title(
        "Local dual: one pentagon with its 5 neighbouring hexagons",
        fontsize=14,
        fontweight="bold",
    )
    ax.text(
        0,
        pts[:, 1].min() - 1.15,
        (
            "Orange dashed lines connect face centroids of "
            "adjacent polygons — the local star of the "
            "pentakis dodecahedron around one degree-5 vertex."
        ),
        ha="center",
        fontsize=10,
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.5},
    )
    return fig, ax


def main():
    parser = argparse.ArgumentParser(description="Draw local dual patch (pentagon + 5 hexagons).")
    parser.add_argument("--show", action="store_true", help="Show plot interactively.")
    parser.add_argument(
        "--output",
        default=None,
        help="Output PNG path (default: save next to script).",
    )
    args = parser.parse_args()

    fig, _ax = draw_local_patch()

    if args.output:
        out = args.output
    else:
        out = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "local_dual_patch.png",
        )
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")

    if args.show:
        plt.show()
    else:
        plt.close(fig)


if __name__ == "__main__":
    main()
