#!/usr/bin/env python3
"""Figure 2 — full 2-D net of the truncated icosahedron with dual overlay.

Builds all 60 vertices of a truncated icosahedron, finds its 32
faces (12 pentagons + 20 hexagons) via half-edge traversal, unfolds
into a non-overlapping planar net using a random spanning tree + SAT
validation, then overlays the dual graph edges that are physically
glued in the net.
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icosphere_geometry import (
    build_face_adjacency,
    build_truncated_icosahedron,
    dual_segments,
    find_faces,
    find_net,
)

# --- colours ---------------------------------------------------------------
PENTAGON_COLOR = "#FF9999"  # 淡粉紅 — 五邊形面
HEXAGON_COLOR = "#E6F2FF"  # 淡藍 — 六邊形面
DUAL_COLOR = "#FF8C00"  # 亮橙 — 對偶邊
PENTAGON_MARKER = "#C0392B"  # 暗紅 — 五邊形中心
HEXAGON_MARKER = "#1F618D"  # 暗藍 — 六邊形中心


def draw_net(placed, segs, cent, tries, fig=None, ax=None):
    """Draw the full unfolded net with dual overlay.

    Args:
        placed: Face-placement dict from ``find_net``.
        segs: Dual-edge segments from ``dual_segments``.
        cent: Face centroids from ``dual_segments``.
        tries: Number of spanning-tree attempts (for annotation).
        fig: Optional existing figure.
        ax: Optional existing axes.

    Returns:
        (fig, ax)
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(13, 11))

    ax.set_aspect("equal")
    ax.axis("off")
    for f, (v2d, v3d) in placed.items():
        ax.add_patch(
            PltPolygon(
                v2d,
                closed=True,
                facecolor=(PENTAGON_COLOR if len(v3d) == 5 else HEXAGON_COLOR),
                edgecolor="#222222",
                linewidth=1.8,
                alpha=0.9,
                zorder=2,
            )
        )
    for p1, p2 in segs:
        ax.plot(
            [p1[0], p2[0]],
            [p1[1], p2[1]],
            color=DUAL_COLOR,
            linestyle="--",
            linewidth=2.2,
            zorder=3,
            solid_capstyle="round",
        )
    for f, c in cent.items():
        n = len(placed[f][1])
        ax.plot(
            c[0],
            c[1],
            "o",
            markersize=6.5,
            color=(PENTAGON_MARKER if n == 5 else HEXAGON_MARKER),
            zorder=4,
        )

    pts = np.vstack([v2d for v2d, _ in placed.values()])
    margin = 1.2
    ax.set_xlim(pts[:, 0].min() - margin, pts[:, 0].max() + margin)
    ax.set_ylim(pts[:, 1].min() - margin, pts[:, 1].max() + margin)

    ax.set_title(
        "Truncated icosahedron net (12 pentagons + 20 hexagons)\nwith pentakis dodecahedron dual overlay",
        fontsize=14,
        fontweight="bold",
    )

    handles = [
        mpatches.Patch(
            facecolor=PENTAGON_COLOR,
            edgecolor="#222",
            label=f"Pentagon ({sum(1 for v in placed.values() if len(v[1]) == 5)})",
        ),
        mpatches.Patch(
            facecolor=HEXAGON_COLOR,
            edgecolor="#222",
            label=f"Hexagon ({sum(1 for v in placed.values() if len(v[1]) == 6)})",
        ),
        Line2D(
            [0],
            [0],
            color=DUAL_COLOR,
            ls="--",
            lw=2.2,
            label="Dual edge (glued pairs only)",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=PENTAGON_MARKER,
            ms=8,
            label="Pentagon centre (dual degree-5)",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor=HEXAGON_MARKER,
            ms=8,
            label="Hexagon centre (dual degree-6)",
        ),
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=9, framealpha=0.9)

    n5 = 12  # 固定：截角二十面體有 12 個五邊形面
    n6 = 20  # 固定：20 個六邊形面
    ax.text(
        0.01,
        0.01,
        (
            f"spanning-tree attempts: {tries}\n"
            f"V={len(placed)} faces  "
            f"E={sum(len(v[1]) for v in placed.values()) // 2} edges  "
            f"F={n5}+{n6}=32  (V-E+F=2)"
        ),
        transform=ax.transAxes,
        fontsize=10,
        va="bottom",
        bbox={"boxstyle": "round", "facecolor": "wheat", "alpha": 0.6},
    )
    return fig, ax


def main():
    parser = argparse.ArgumentParser(description="Draw full truncated-icosahedron net with dual overlay.")
    parser.add_argument(
        "--seed",
        type=int,
        default=11,
        help="RNG seed for spanning-tree search (default: 11).",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Show plot interactively.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output PNG path (default: save next to script).",
    )
    args = parser.parse_args()

    V, adj_v = build_truncated_icosahedron()
    faces, face_of = find_faces(V, adj_v)
    adj_f = build_face_adjacency(faces, face_of)
    root = next(i for i, f in enumerate(faces) if len(f) == 5)  # 五邊形為根

    placed, _parent, tries = find_net(V, faces, adj_f, root, seed=args.seed)
    segs, cent = dual_segments(placed, adj_f)

    n5 = sum(1 for f in faces if len(f) == 5)
    n_edges = sum(len(f) for f in faces) // 2
    print(
        f"faces = {len(faces)} "
        f"(pentagons={n5}, hexagons={len(faces) - n5}), "
        f"V = {len(V)}, E = {n_edges}, "
        f"found valid net after {tries} spanning-tree attempts"
    )

    fig, _ax = draw_net(placed, segs, cent, tries)

    if args.output:
        out = args.output
    else:
        out = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "full_net.png",
        )
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")

    if args.show:
        plt.show()
    else:
        plt.close(fig)


if __name__ == "__main__":
    main()
