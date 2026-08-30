#!/usr/bin/env python3
# zh-TW 註解：本腳本演示 bulkyball 的點對稱展開方法 — 半球鏡像法
#   1. 建立截角二十面體 (truncated icosahedron, 32 faces)
#   2. 對每個面找到其對面 (antipodal face)
#   3. 將 + hemisphere 面放置在 2D 平面上 (BFS spanning tree)
#   4. 鏡像放置 - hemisphere 面 (f' 置於 -f 位置) → 自動點對稱
#   5. 驗證：placed face 與其對面 face 是否對稱 (check_symmetric)
#   6. 演示 UGRIB 命名規範：頂點編號、邊界稜線編號、面編號
#
# NOTE: 數學上，截角二十面體無法產生完美連接的點對稱展開
#   (31 個樹邊 = 奇數，無 self-conjugate 邊)。半球鏡像法
#   保證對稱性但兩半可能重疊或不連接。
#   詳見 bulkyball_domain.md

"""Point-symmetric net for the truncated icosahedron (bulkyball).

Uses the hemisphere-mirror method: unfold one hemisphere into 2-D,
then mirror every face through the origin to produce the other
hemisphere.  The result is point-symmetric by construction.

Also demonstrates UGRIB vertex / boundary-edge / face numbering
conventions for the symmetric layout.

Usage:
    python plot_symmetric_net.py [--seed SEED] [--offset D]
                                 [--show] [--output PATH]
"""

import argparse
import logging
import os
import sys
from collections import defaultdict, deque

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon as MplPolygon

# --- Ensure local imports work from any CWD ---
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from icosphere_geometry import (
    attach_along_edge,
    build_face_adjacency,
    build_truncated_icosahedron,
    create_regular_polygon,
    dual_segments,
    find_faces,
    is_valid_net,
)

logger = logging.getLogger(__name__)

PENTAGON_COLOR = "#FF9999"
HEXAGON_COLOR = "#E6F2FF"
DUAL_COLOR = "#FF8C00"
PLUS_COLOR = "#4A90D9"
MINUS_COLOR = "#D94A4A"

__all__ = [
    "build_hemisphere_tree",
    "check_symmetric",
    "compute_ugrib_numbering",
    "draw_symmetric_net",
    "find_antipodal_faces",
    "find_antipodal_vertices",
    "main",
    "mirror_placement",
    "place_hemisphere",
    "split_hemispheres",
]


def find_antipodal_faces(faces, V):
    """Find antipodal face pairs by exact vertex negation.

    Args:
        faces: List of face vertex-index lists.
        V: Vertex position array (N, 3).

    Returns:
        Dict mapping face index to its antipodal face index.
    """
    antipodal_v = find_antipodal_vertices(V)
    antipodal_f = {}
    for f in range(len(faces)):
        expected = {antipodal_v[v] for v in faces[f]}
        for g in range(len(faces)):
            if set(faces[g]) == expected:
                antipodal_f[f] = g
                break
    assert len(antipodal_f) == len(faces)
    return antipodal_f


def find_antipodal_vertices(V):
    """Build vertex-level antipodal map by closest negated position.

    Args:
        V: Vertex positions (N, 3).

    Returns:
        Dict mapping vertex index to its antipodal vertex index.
    """
    n = len(V)
    antipodal = {}
    for v in range(n):
        neg = -V[v]
        best = int(np.argmin(np.linalg.norm(V - neg, axis=1)))
        antipodal[v] = best
    return antipodal


def split_hemispheres(faces, V, root):
    """Split faces into hemispheres using the root centroid as equator normal.

    Args:
        faces: List of face vertex-index lists.
        V: Vertex positions (N, 3).
        root: Root face index (placed in hemisphere +1).

    Returns:
        Tuple of (hemisphere_dict, root_anti).
    """
    cents = np.array([V[f].mean(axis=0) for f in faces])
    cents_n = cents / np.linalg.norm(cents, axis=1, keepdims=True)
    nc = cents_n[root]
    hemi = {}
    for i in range(len(faces)):
        hemi[i] = 1 if float(np.dot(cents_n[i], nc)) > 0 else -1
    return hemi, None  # root_anti set by caller via antipodal map


def build_hemisphere_tree(faces, adj_f, hemi, root, rng):
    """Build a random spanning tree for the +1 hemisphere only.

    Args:
        faces: Face vertex lists.
        adj_f: Face adjacency dict.
        hemi: Hemisphere assignment dict.
        root: Root face (must be in hemisphere +1).
        rng: numpy Generator.

    Returns:
        Tuple of (parent, shared) dicts for the hemisphere tree.
    """
    target = hemi[root]
    parent = {root: None}
    shared = {}
    frontier = [root]
    n_target = sum(1 for h in hemi.values() if h == target)
    for nb in adj_f[root]:
        if hemi[nb] == target and nb not in parent:
            parent[nb] = root
            shared[nb] = adj_f[root][nb]
            frontier.append(nb)
    while len(parent) < n_target:
        u = frontier.pop(int(rng.integers(len(frontier))))
        for v in adj_f[u]:
            if v not in parent and hemi[v] == target:
                parent[v] = u
                shared[v] = adj_f[u][v]
                frontier.append(v)
    return parent, shared


def place_hemisphere(faces, V, parent, shared, root, offset=(0.0, 0.0)):
    """Place faces of one hemisphere using BFS from root.

    Args:
        faces: Face vertex lists.
        V: Vertex positions (N, 3).
        parent: Tree parent dict.
        shared: Shared edge dict.
        root: Root face index.
        offset: (dx, dy) to shift the root face.

    Returns:
        Dict face -> (vertices_2d, vertex_indices_3d).
    """
    placed = {}
    f0 = faces[root]
    n0 = len(f0)
    edge_len = float(np.linalg.norm(V[f0[0]] - V[f0[1]]))
    radius = edge_len / (2.0 * np.sin(np.pi / n0))
    poly = create_regular_polygon(n0, radius, start_angle=np.pi / 2)
    if offset != (0.0, 0.0):
        poly = poly + np.array(offset)
    placed[root] = (poly.copy(), list(f0))

    children = defaultdict(list)
    for ch, par in parent.items():
        if par is not None:
            children[par].append(ch)

    dq = deque([root])
    while dq:
        u = dq.popleft()
        v2d_u, v3d_u = placed[u]
        ku = len(v3d_u)
        for ch in children[u]:
            if ch in placed:
                continue
            a, b = shared[ch]
            idx = next(i for i in range(ku) if v3d_u[i] == a and v3d_u[(i + 1) % ku] == b)
            verts, _ = attach_along_edge(v2d_u[idx], v2d_u[(idx + 1) % ku], len(faces[ch]))
            j = faces[ch].index(a)
            placed[ch] = (verts, faces[ch][j:] + faces[ch][:j])
            dq.append(ch)
    return placed


def mirror_placement(placed_half, faces, antipodal_f, antipodal_v):
    """Mirror a half-placement through the origin to get the other half.

    For each placed face ``f`` at position ``P``, places ``antipodal_f[f]``
    at ``-P`` using the antipodal vertex map.  Fixes winding order
    (CCW) when the face's vertex ordering is reversed by the antipodal map.

    Args:
        placed_half: Dict face -> (v2d, v3d).
        faces: All face vertex lists.
        antipodal_f: Antipodal face map.
        antipodal_v: Antipodal vertex map.

    Returns:
        Dict face -> (v2d, v3d) for the mirrored hemisphere.
    """
    mirrored = {}
    for f, (v2d_f, v3d_f) in placed_half.items():
        f_anti = antipodal_f[f]
        v3d_anti = faces[f_anti]
        v2d_anti = np.zeros_like(v2d_f)
        for i, v in enumerate(v3d_f):
            v_anti = antipodal_v[v]
            j = v3d_anti.index(v_anti)
            v2d_anti[j] = -v2d_f[i]
        # Fix winding: ensure CCW
        if _signed_area(v2d_anti) < 0:
            v2d_anti = v2d_anti[::-1].copy()
        mirrored[f_anti] = (v2d_anti, list(v3d_anti))
    return mirrored


def _signed_area(poly):
    """Compute signed area of a 2-D polygon (positive = CCW)."""
    n = len(poly)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += poly[i, 0] * poly[j, 1] - poly[j, 0] * poly[i, 1]
    return area / 2.0


def check_symmetric(placed, antipodal_f, tol=1e-3):
    """Check if a 2-D placement has point symmetry (180° rotation).

    For each face ``f`` at position ``P``, checks that ``antipodal_f[f]``
    is at ``-P`` (up to cyclic vertex reordering or reversal).

    Args:
        placed: Dict face -> (v2d, v3d).
        antipodal_f: Antipodal face map.
        tol: Position tolerance.

    Returns:
        True if every face's antipodal is at the mirrored position.
    """
    for f in placed:
        f_anti = antipodal_f[f]
        if f_anti not in placed:
            return False
        v2d_f = placed[f][0]
        v2d_a = placed[f_anti][0]
        k = len(v2d_f)
        found = False
        for s in range(k):
            if np.allclose(np.roll(v2d_f, s, axis=0), -v2d_a, atol=tol):
                found = True
                break
        if not found:
            rev = v2d_f[::-1].copy()
            for s in range(k):
                if np.allclose(np.roll(rev, s, axis=0), -v2d_a, atol=tol):
                    found = True
                    break
        if not found:
            return False
    return True


def compute_ugrib_numbering(placed, faces, antipodal_f, antipodal_v):
    """Compute UGRIB vertex / boundary-edge / face numbering.

    - Vertices: boundary first (CCW from leftmost-bottommost), interior
      second (row-major).  For symmetric layouts: vertex i ↔ N-1-i.
    - Boundary edges: CCW traversal from leftmost-bottommost vertex.
      For symmetric layouts: edge j ↔ M-1-j.
    - Faces: row-major spatial order in 2-D.  For symmetric layouts:
      face k ↔ F-1-k.

    Args:
        placed: Dict face -> (v2d, v3d).
        faces: All face vertex lists.
        antipodal_f: Antipodal face map.
        antipodal_v: Antipodal vertex map.

    Returns:
        Dict with keys 'vertex_ids', 'boundary_edges', 'face_ids',
        'symmetry_pairs'.
    """
    # Collect all unique 2-D vertex positions (by rounded coords).
    # In the mirror approach, the same 3-D vertex appears at multiple
    # 2-D positions, so we work purely in 2-D coordinate space.
    tol = 1e-4
    vert_positions = []  # list of (x, y)
    vert_key = {}  # rounded key -> index in vert_positions

    def get_vert_id(x, y):
        key = (round(x / tol), round(y / tol))
        if key not in vert_key:
            vert_key[key] = len(vert_positions)
            vert_positions.append((x, y))
        return vert_key[key]

    # Build face edges in 2-D and find shared (interior) edges.
    face_edges_2d = {}  # face -> list of (v1_id, v2_id)
    edge_users = defaultdict(list)  # 2D edge -> [(face, local_idx)]

    for f, (v2d, v3d) in placed.items():
        kf = len(v3d)
        edges = []
        for i in range(kf):
            v1 = get_vert_id(float(v2d[i, 0]), float(v2d[i, 1]))
            v2 = get_vert_id(float(v2d[(i + 1) % kf, 0]), float(v2d[(i + 1) % kf, 1]))
            edges.append((v1, v2))
            # Canonical key for undirected edge
            canon = frozenset([v1, v2])
            edge_users[canon].append((f, i))
        face_edges_2d[f] = edges

    # Interior edges = shared by 2 faces.  Boundary = used once.
    boundary_edge_ids = []  # list of (v1, v2) in 2-D vertex space
    for canon, users in edge_users.items():
        if len(users) <= 1:
            boundary_edge_ids.append(tuple(canon))

    # Boundary vertices = vertices appearing in boundary edges
    boundary_vert_ids = set()
    for v1, v2 in boundary_edge_ids:
        boundary_vert_ids.add(v1)
        boundary_vert_ids.add(v2)

    n_total = len(vert_positions)
    interior_vert_ids = set(range(n_total)) - boundary_vert_ids

    # Assign vertex IDs: boundary first (CCW from leftmost-bottommost),
    # then interior (row-major)
    boundary_sorted = sorted(
        boundary_vert_ids,
        key=lambda v: (vert_positions[v][0], vert_positions[v][1]),
    )
    interior_sorted = sorted(
        interior_vert_ids,
        key=lambda v: (vert_positions[v][1], vert_positions[v][0]),
    )

    vertex_ids = {}  # 2-D vert_id -> UGRIB id
    for i, v in enumerate(boundary_sorted):
        vertex_ids[v] = i
    for i, v in enumerate(interior_sorted):
        vertex_ids[v] = len(boundary_sorted) + i

    # Boundary edges with UGRIB vertex IDs
    bnd_edges = []
    for v1, v2 in boundary_edge_ids:
        bnd_edges.append((vertex_ids[v1], vertex_ids[v2]))

    # Face IDs: bottom-to-top row-major (ascending y, then ascending x).
    # For symmetric layouts, face 0 (bottom-left) ↔ face F-1 (top-right).
    face_centroids = []
    for f in placed:
        cx = placed[f][0][:, 0].mean()
        cy = placed[f][0][:, 1].mean()
        face_centroids.append((f, cx, cy))
    face_centroids.sort(key=lambda fc: (fc[2], fc[1]))
    face_ids = {fc[0]: i for i, fc in enumerate(face_centroids)}

    # Symmetry pairs
    sym_pairs = {}
    for f in placed:
        f_anti = antipodal_f[f]
        sym_pairs[f] = f_anti

    return {
        "vertex_ids": vertex_ids,
        "boundary_edges": bnd_edges,
        "face_ids": face_ids,
        "symmetry_pairs": sym_pairs,
        "n_boundary_verts": len(boundary_sorted),
        "n_interior_verts": len(interior_sorted),
        "n_faces": len(placed),
        "vert_positions": vert_positions,
    }


def draw_symmetric_net(placed, faces, face_sizes, adj_f, antipodal_f, ugrib_info, tries, show=False, output=None):
    """Draw the point-symmetric net with dual overlay and UGRIB ID labels.

    Args:
        placed: Dict face -> (v2d, v3d).
        faces: All face vertex lists.
        face_sizes: Pentagons/hexagons count.
        adj_f: Face adjacency dict.
        antipodal_f: Antipodal face map.
        ugrib_info: UGRIB numbering dict from compute_ugrib_numbering.
        tries: Number of spanning-tree attempts for hemisphere.
        show: If True, display interactively.
        output: Output path for PNG.
    """
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))

    # Color faces by type
    for f_idx in sorted(placed.keys()):
        v2d, v3d = placed[f_idx]
        n = len(v3d)
        color = PENTAGON_COLOR if n == 5 else HEXAGON_COLOR
        alpha = 0.4 if n == 5 else 0.3

        poly = MplPolygon(v2d, closed=True, facecolor=color, edgecolor="#333333", linewidth=0.8, alpha=alpha)
        ax.add_patch(poly)

        # Label face ID (UGRIB face number)
        cx = np.mean(v2d[:, 0])
        cy = np.mean(v2d[:, 1])
        fid = ugrib_info["face_ids"][f_idx]
        f_anti = antipodal_f[f_idx]
        fid_anti = ugrib_info["face_ids"][f_anti]
        ax.plot(cx, cy, "k.", markersize=3)
        ax.annotate(f"F{fid}", (cx, cy), fontsize=5, ha="center", va="center", color="#333333", xytext=(cx, cy + 0.3))
        # Show pair ID
        if fid < fid_anti:
            ax.annotate(
                f"#{fid}/{fid_anti}",
                (cx, cy),
                fontsize=4,
                ha="center",
                va="bottom",
                color=DUAL_COLOR,
                xytext=(cx, cy - 0.5),
            )

    # Draw dual overlay (face centroids + dual edges)
    centroids = {}
    for f_idx in placed:
        cx = np.mean(placed[f_idx][0][:, 0])
        cy = np.mean(placed[f_idx][0][:, 1])
        centroids[f_idx] = (cx, cy)

    segs, _ = dual_segments(placed, adj_f)
    for seg in segs:
        (x1, y1), (x2, y2) = seg
        ax.plot([x1, x2], [y1, y2], color=DUAL_COLOR, linewidth=0.5, alpha=0.6, zorder=5)

    # Draw centorids
    for f_idx, (cx, cy) in centroids.items():
        n = len(placed[f_idx][1])
        marker = "p" if n == 5 else "o"
        size = 30 if n == 5 else 15
        color = "#FF4500" if n == 5 else "#4169E1"
        ax.plot(cx, cy, marker=marker, markersize=size * 0.5, color=color, zorder=10, alpha=0.6)

    # Draw origin (center of symmetry)
    ax.axhline(y=0, color="gray", linewidth=0.3, linestyle="--", alpha=0.4)
    ax.axvline(x=0, color="gray", linewidth=0.3, linestyle="--", alpha=0.4)
    ax.plot(0, 0, "k+", markersize=10, markeredgewidth=1)

    # Boundary edges (use 2-D vertex positions from ugrib_info)
    vert_positions = ugrib_info.get("vert_positions", [])
    for va, vb in ugrib_info["boundary_edges"]:
        xa, ya = vert_positions[va] if va < len(vert_positions) else (0, 0)
        xb, yb = vert_positions[vb] if vb < len(vert_positions) else (0, 0)
        ax.plot([xa, xb], [ya, yb], color="#AA0000", linewidth=1.5, alpha=0.5, zorder=3)

    ax.set_aspect("equal")
    ax.set_title(
        f"Bulkyball Point-Symmetric Net (Hemisphere Mirror)\n"
        f"Faces: {len(placed)} | Symmetric: "
        f"{check_symmetric(placed, antipodal_f)} | "
        f"Spanning-tree attempts: {tries}",
        fontsize=10,
    )
    ax.set_xlabel("X (2-D unfolded plane)")
    ax.set_ylabel("Y (2-D unfolded plane)")

    # Legend
    from matplotlib.patches import Patch

    legend_elements = [
        Patch(facecolor=PENTAGON_COLOR, alpha=0.4, label="Pentagon (F)"),
        Patch(facecolor=HEXAGON_COLOR, alpha=0.3, label="Hexagon (F)"),
        plt.Line2D([0], [0], color=DUAL_COLOR, lw=0.5, label="Dual edges"),
        plt.Line2D([0], [0], color="#AA0000", lw=1.5, label="Boundary edges"),
        plt.Line2D([0], [0], marker="+", color="gray", lw=0.5, label="Symmetry centre"),
    ]
    ax.legend(handles=legend_elements, loc="upper left", fontsize=7)

    if output:
        fig.savefig(output, dpi=200, bbox_inches="tight")
        logger.info("Saved symmetric net to %s", output)
    elif show:
        plt.show()
    plt.close(fig)


def main():
    """Main entry point: build symmetric net, verify, draw, print UGRIB."""
    parser = argparse.ArgumentParser(description="Point-symmetric net for bulkyball (truncated icosahedron)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for hemisphere spanning tree")
    parser.add_argument("--offset", type=float, default=3.0, help="X-offset for root face to separate hemispheres")
    parser.add_argument("--show", action="store_true", help="Show plot interactively")
    parser.add_argument("--output", type=str, default=None, help="Output PNG path (default: symmetric_net.png)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Build mesh
    logger.info("Building truncated icosahedron...")
    V, adj = build_truncated_icosahedron()
    faces, face_of = find_faces(V, adj)
    adj_f = build_face_adjacency(faces, face_of)

    n5 = sum(1 for f in faces if len(f) == 5)
    n6 = sum(1 for f in faces if len(f) == 6)
    n_edges = sum(len(f) for f in faces) // 2
    logger.info("Mesh: V=%d, E=%d, F=%d (%d pentagons, %d hexagons)", len(V), n_edges, len(faces), n5, n6)

    # Find antipodal faces and hemispheres
    antipodal_f = find_antipodal_faces(faces, V)
    antipodal_v = find_antipodal_vertices(V)
    root = next(i for i, f in enumerate(faces) if len(f) == 5)
    hemi, _ = split_hemispheres(faces, V, root)

    logger.info("Antipodal pairs: %d", len(antipodal_f) // 2)
    logger.info(
        "Hemisphere +: %d faces, -: %d faces",
        sum(1 for h in hemi.values() if h == 1),
        sum(1 for h in hemi.values() if h == -1),
    )

    # Build + hemisphere spanning tree and place
    rng = np.random.default_rng(args.seed)
    half_tree, half_shared = build_hemisphere_tree(faces, adj_f, hemi, root, rng)

    # Try a few seeds for a valid hemisphere tree
    tries = 0
    while len(half_tree) < 16 and tries < 1000:
        tries += 1
        rng = np.random.default_rng(args.seed + tries)
        half_tree, half_shared = build_hemisphere_tree(faces, adj_f, hemi, root, rng)

    logger.info("Hemisphere tree: %d faces, %d attempts", len(half_tree), tries + 1)

    # Place + hemisphere
    placed_half = place_hemisphere(
        faces,
        V,
        half_tree,
        half_shared,
        root,
        offset=(args.offset, 0.0),
    )
    logger.info("Placed + hemisphere: %d faces", len(placed_half))

    # Mirror to - hemisphere
    placed_mirror = mirror_placement(placed_half, faces, antipodal_f, antipodal_v)

    placed = {**placed_half, **placed_mirror}
    logger.info("Total placed: %d faces", len(placed))

    # Verify symmetry
    sym = check_symmetric(placed, antipodal_f)
    valid = is_valid_net(placed)
    segs, _cents = dual_segments(placed, adj_f)
    n_segs = len(segs)

    logger.info("Point symmetric: %s", sym)
    logger.info("Valid net (no overlaps): %s", valid)
    logger.info("Dual segments (non-tree shared): %d", n_segs)
    logger.info("Pentagon centroids: %d", n5)
    logger.info("Hexagon centroids: %d", n6)

    face_ids_info = (
        f"{len(faces)} faces "
        f"(pentagons={n5}, hexagons={n6}) | "
        f"V={len(V)}, E={n_edges}, "
        f"symmetric={sym}, valid={valid}, "
        f"tries={tries + 1}"
    )
    print(face_ids_info)

    # Compute UGRIB numbering
    ugrib_info = compute_ugrib_numbering(placed, faces, antipodal_f, antipodal_v)
    logger.info(
        "UGRIB: %d boundary verts, %d interior verts, %d boundary edges",
        ugrib_info["n_boundary_verts"],
        ugrib_info["n_interior_verts"],
        len(ugrib_info["boundary_edges"]),
    )

    # Verify symmetry pairs
    n_sym = 0
    n_break = 0
    for f in range(len(faces)):
        f_anti = antipodal_f[f]
        fid = ugrib_info["face_ids"][f]
        fid_anti = ugrib_info["face_ids"][f_anti]
        if fid + fid_anti == len(faces) - 1:
            n_sym += 1
        else:
            n_break += 1
    logger.info("Face ID symmetry (k ↔ F-1-k): %d/%d pairs correct", n_sym // 2, len(faces) // 2)

    # Draw
    output = args.output or os.path.join(_THIS_DIR, "symmetric_net.png")
    draw_symmetric_net(
        placed,
        faces,
        (n5, n6),
        adj_f,
        antipodal_f,
        ugrib_info,
        tries + 1,
        show=args.show,
        output=output,
    )
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()
