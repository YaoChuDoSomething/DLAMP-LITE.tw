#!/usr/bin/env python3
"""3D rendering of the pentakis dodecahedron (dual) overlaid on the
truncated icosahedron wireframe.

Extension #2 from the code-review document: projects each face
centroid of the truncated icosahedron onto the circumsphere to
obtain the 32 dual vertices, then draws the 90 dual edges (orange)
connecting centroids of adjacent faces.  The 12 hexagon-adjacent
pentagon centroids are degree-5; the 20 hexagon centroids are
degree-6 — the vertex signature of the pentakis dodecahedron.
"""

from __future__ import annotations

import argparse
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  — register 3-D

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icosphere_geometry import (
    build_face_adjacency,
    build_truncated_icosahedron,
    find_faces,
)

# --- colours ---------------------------------------------------------------
DUAL_COLOR = "#FF8C00"  # 亮橙 — 對偶邊
ORIG_EDGE_COLOR = "#AAAAAA"  # 淺灰 — 原 polyhedron 邊
PENTAGON_MARKER = "#C0392B"  # 暗紅 — 五邊形面心（對偶 5-配位）
HEXAGON_MARKER = "#1F618D"  # 暗藍 — 六邊形面心（對偶 6-配位）


# --- 3D dual computation ---------------------------------------------------
def compute_3d_centroids(faces, V):
    """Compute 3-D centroids of every face, projected to the
    circumsphere.

    Args:
        faces: List of face vertex-index lists.
        V: (N, 3) vertex array.

    Returns:
        (M, 3) array of projected centroids, one per face.
    """
    cents = np.array([V[face].mean(axis=0) for face in faces])
    circumradius = float(np.linalg.norm(V[0]))
    norms = np.linalg.norm(cents, axis=1, keepdims=True)
    cents = cents / norms * circumradius
    return cents


def get_original_edges(faces):
    """Collect all unique undirected edges of the polyhedron.

    Args:
        faces: List of face vertex-index lists.

    Returns:
        List of ``(a, b)`` index pairs (a < b).
    """
    edges: set = set()
    for face in faces:
        k = len(face)
        for i in range(k):
            a, b = face[i], face[(i + 1) % k]
            edges.add((min(a, b), max(a, b)))
    return list(edges)


def get_dual_edges(adj_f):
    """Collect all dual edges — one per pair of adjacent faces.

    Args:
        adj_f: Face-adjacency list from ``build_face_adjacency``.

    Returns:
        List of ``(f, g)`` face-index pairs.
    """
    edges: list = []
    seen: set = set()
    for f in range(len(adj_f)):
        for g in adj_f[f]:
            if (g, f) not in seen:
                seen.add((f, g))
                edges.append((f, g))
    return edges


# --- rendering -------------------------------------------------------------
def draw_3d_dual(cents3d, orig_edges, dual_edges, V, faces, fig=None, ax=None):
    """Render the 3-D dual (pentakis dodecahedron) on the original.

    Args:
        cents3d: (M, 3) projected face centroids.
        orig_edges: List of ``(a, b)`` vertex-edge pairs.
        dual_edges: List of ``(f, g)`` face-edge pairs.
        V: (N, 3) vertex array.
        faces: List of faces.
        fig: Optional figure.
        ax: Optional 3-D axes.

    Returns:
        (fig, ax)
    """
    if fig is None or ax is None:
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection="3d")

    ax.set_box_aspect([1, 1, 1])

    # 原多面體邊（淺灰、半透明）
    for a, b in orig_edges:
        ax.plot(
            [V[a, 0], V[b, 0]],
            [V[a, 1], V[b, 1]],
            [V[a, 2], V[b, 2]],
            color=ORIG_EDGE_COLOR,
            linewidth=0.8,
            alpha=0.35,
        )

    # 對偶邊（橘色）
    for f, g in dual_edges:
        ax.plot(
            [cents3d[f, 0], cents3d[g, 0]],
            [cents3d[f, 1], cents3d[g, 1]],
            [cents3d[f, 2], cents3d[g, 2]],
            color=DUAL_COLOR,
            linewidth=1.6,
            alpha=0.85,
        )

    # 對偶頂點標記
    is_pent = [len(faces[f]) == 5 for f in range(len(faces))]
    pent_idx = [i for i, p in enumerate(is_pent) if p]
    hex_idx = [i for i, p in enumerate(is_pent) if not p]

    ax.scatter(
        cents3d[pent_idx, 0],
        cents3d[pent_idx, 1],
        cents3d[pent_idx, 2],
        color=PENTAGON_MARKER,
        s=60,
        label="Pentagon centres (degree-5)",
        zorder=5,
    )
    ax.scatter(
        cents3d[hex_idx, 0],
        cents3d[hex_idx, 1],
        cents3d[hex_idx, 2],
        color=HEXAGON_MARKER,
        s=35,
        label="Hexagon centres (degree-6)",
        zorder=5,
    )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(
        "Pentakis dodecahedron (dual) overlaid\non truncated icosahedron",
        fontsize=14,
        fontweight="bold",
    )
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)

    # 隱藏軸線以更好地顯示形狀
    ax.set_axis_off()
    return fig, ax


def main():
    parser = argparse.ArgumentParser(
        description=("3D render of pentakis dodecahedron (dual) on truncated icosahedron.")
    )
    parser.add_argument(
        "--elev",
        type=float,
        default=20.0,
        help="Elevation angle in degrees (default: 20).",
    )
    parser.add_argument(
        "--azim",
        type=float,
        default=45.0,
        help="Azimuthal angle in degrees (default: 45).",
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
    faces, _face_of = find_faces(V, adj_v)
    adj_f = build_face_adjacency(faces, _face_of)

    cents3d = compute_3d_centroids(faces, V)
    orig_edges = get_original_edges(faces)
    dual_edges = get_dual_edges(adj_f)

    n5 = sum(1 for f in faces if len(f) == 5)
    n_edges = len(orig_edges)
    n_dual = len(dual_edges)
    print(
        f"Truncated icosahedron:\n"
        f"  V = {len(V)}, E = {n_edges}, "
        f"F = {len(faces)} (pentagons={n5}, "
        f"hexagons={len(faces) - n5})\n"
        f"  Euler: V - E + F = {len(V) - n_edges + len(faces)}\n"
        f"Pentakis dodecahedron (dual):\n"
        f"  V_dual = {len(cents3d)}, E_dual = {n_dual}, "
        f"F_dual = {len(V)}"
    )

    fig, ax = draw_3d_dual(cents3d, orig_edges, dual_edges, V, faces)
    ax.view_init(elev=args.elev, azim=args.azim)

    if args.output:
        out = args.output
    else:
        out = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "3d_dual.png",
        )
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")

    if args.show:
        plt.show()
    else:
        plt.close(fig)


if __name__ == "__main__":
    main()
