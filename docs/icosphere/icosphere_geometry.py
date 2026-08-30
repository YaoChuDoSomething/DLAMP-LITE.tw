#!/usr/bin/env python3
"""Core geometry for truncated icosahedron net generation.

Constructs a truncated icosahedron (32 faces = 12 pentagons + 20
hexagons) from even-permutation coordinates, finds all faces via
half-edge traversal, unfolds into a 2D net using a random spanning
tree, validates with SAT overlap checks, and computes the dual-graph
(pentakis dodecahedron) edges.

No matplotlib dependency — pure numpy.
"""

from __future__ import annotations

import itertools
from collections import deque

import numpy as np

# --- type aliases ----------------------------------------------------------
Face = list[int]
PlacedFace = tuple[np.ndarray, list[int]]
FaceAdj = list[dict[int, tuple[int, int]]]


# --- 2D geometry utilities -------------------------------------------------
def create_regular_polygon(
    sides: int,
    radius: float,
    center: tuple[float, float] = (0.0, 0.0),
    start_angle: float = 0.0,
) -> np.ndarray:
    """Create vertex coordinates of a regular polygon.

    Args:
        sides: Number of sides.
        radius: Circumradius.
        center: Polygon center (cx, cy).
        start_angle: Starting angle in radians.

    Returns:
        Array of shape (sides, 2).
    """
    angles = start_angle + 2.0 * np.pi * np.arange(sides) / sides
    return np.column_stack([center[0] + radius * np.cos(angles), center[1] + radius * np.sin(angles)])


def attach_along_edge(p1, p2, sides):
    """Attach a regular *sides*-gon along directed edge ``p1 -> p2``.

    The new polygon is placed on the exterior (right) side of the
    directed edge.  Guarantees ``v[0] == p1`` and ``v[-1] == p2``
    to machine precision, and maintains counter-clockwise winding
    when the parent polygon is counter-clockwise.

    Args:
        p1: First edge endpoint (2-D).
        p2: Second edge endpoint (2-D).
        sides: Number of sides of the polygon to attach.

    Returns:
        (vertices (sides, 2), center (2,))
    """
    p1 = np.asarray(p1, float)
    p2 = np.asarray(p2, float)
    edge = p2 - p1
    length = np.hypot(edge[0], edge[1])
    mid = 0.5 * (p1 + p2)
    # 邊向量順時針旋轉 90° 得外向法向量
    n_out = np.array([edge[1], -edge[0]]) / length
    apothem = length / (2.0 * np.tan(np.pi / sides))
    radius = length / (2.0 * np.sin(np.pi / sides))
    center = mid + apothem * n_out
    # n_out 為外向法向量；中心→邊中點為 -n_out 方向
    # theta 必為中心指向邊中點的角度，否剉 v[0]≠p1 且 v[-1]≠p2
    theta = np.arctan2(-n_out[1], -n_out[0])
    angles = theta + np.pi / sides + 2.0 * np.pi * np.arange(sides) / sides
    verts = center + radius * np.column_stack([np.cos(angles), np.sin(angles)])
    return verts, center


# --- 3D truncated icosahedron ---------------------------------------------
def build_truncated_icosahedron():
    """Build 60 vertices and 3-adjacency of a truncated icosahedron.

    Uses the standard even-permutation coordinate sets with all
    sign-variants.

    Returns:
        (V (60, 3), adj) where adj[i] is a list of 3 neighbour
        indices.
    """
    phi = (1.0 + np.sqrt(5.0)) / 2.0
    pts: list[list[float]] = []
    for triple in (
        (0.0, 1.0, 3.0 * phi),
        (1.0, 2.0 + phi, 2.0 * phi),
        (phi, 2.0, 2.0 * phi + 1.0),
    ):
        even = [
            triple,
            (triple[1], triple[2], triple[0]),
            (triple[2], triple[0], triple[1]),
        ]
        n_nonzero = sum(1 for x in triple if x != 0.0)
        for base in even:
            for signs in itertools.product((-1.0, 1.0), repeat=n_nonzero):
                it = iter(signs)
                pts.append([x * next(it) if x != 0.0 else 0.0 for x in base])
    V = np.array(pts)
    if len(V) != 60:
        raise ValueError(f"Expected 60 vertices, got {len(V)}")

    # 最小距雃 = 邊長；距離 < 1.01 * L 的點即為鄰點
    D = np.linalg.norm(V[:, None, :] - V[None, :, :], axis=2)
    L = float(D[D > 1e-9].min())  # 邊長
    adj = [[int(j) for j in np.where(D[i] < L * 1.01)[0] if j != i] for i in range(len(V))]
    if not all(len(a) == 3 for a in adj):
        raise ValueError("Adjacency is not 3-regular")
    return V, adj


def find_faces(V, adj):
    """Find all 32 faces via half-edge (next-counterclockwise) traversal.

    At each vertex the 3 neighbours are sorted by azimuthal angle in
    the tangent plane (normal approx. radial for a convex polyhedron).
    Walking the *next* neighbour at every step traces out one face.

    Args:
        V: (N, 3) vertex array.
        adj: Adjacency list, ``adj[i]`` = list of neighbour indices.

    Returns:
        (faces, face_of) where *faces* is a list of vertex-index lists
        and *face_of* maps a directed edge ``(a, b)`` to its face
        index.
    """
    cyclic: list[list[int]] = []
    for v in range(len(V)):
        n = V[v] / np.linalg.norm(V[v])  # 凸多面體：外法向 ≈ 徑向
        ref = np.array([1.0, 0.0, 0.0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
        t1 = np.cross(n, ref)
        t1 /= np.linalg.norm(t1)
        t2 = np.cross(n, t1)
        cyclic.append(
            sorted(
                adj[v],
                key=lambda u: np.arctan2(
                    float((V[u] - V[v]) @ t2),
                    float((V[u] - V[v]) @ t1),
                ),
            )
        )

    face_of: dict[tuple[int, int], int] = {}
    faces: list[Face] = []
    for u in range(len(V)):
        for v in adj[u]:
            if (u, v) in face_of:
                continue
            face: Face = []
            a, b = u, v
            while (a, b) not in face_of:
                face_of[(a, b)] = len(faces)
                face.append(a)
                lst = cyclic[b]
                a, b = b, lst[(lst.index(a) + 1) % len(lst)]
            faces.append(face)

    counts = sorted(len(f) for f in faces)
    if counts != [5] * 12 + [6] * 20:
        raise ValueError(f"Expected 12 pentagons + 20 hexagons, got {counts}")
    return faces, face_of


def build_face_adjacency(faces, face_of):
    """Build per-face adjacency from the ``face_of`` mapping.

    ``adj_f[f][g] = (a, b)`` means face *f* shares directed edge
    ``a -> b`` with face *g*.

    Args:
        faces: List of faces (vertex-index lists).
        face_of: Directed-edge -> face-index mapping.

    Returns:
        List of dicts, one per face.
    """
    adj_f: FaceAdj = [{} for _ in faces]
    for f, face in enumerate(faces):
        k = len(face)
        for i in range(k):
            a, b = face[i], face[(i + 1) % k]
            g = face_of[(b, a)]
            adj_f[f][g] = (a, b)
    return adj_f


# --- Unfolding: random spanning tree + placement --------------------------
def random_spanning_tree(adj_f, root, rng):
    """Generate a random spanning tree of the face-adjacency graph.

    The root face's neighbours are forced as direct children so the
    central pentagon's 5 dual spokes always appear in the net.

    Args:
        adj_f: Face adjacency list.
        root: Root face index.
        rng: ``np.random.Generator``.

    Returns:
        (parent, shared) dicts.  ``parent[f]`` is the parent face
        index (or ``None`` for root); ``shared[f] = (a, b)`` is the
        directed edge of the parent shared with child *f*.
    """
    parent: dict[int, int | None] = {root: None}
    shared: dict[int, tuple[int, int]] = {}
    frontier: list[int] = [root]
    for nb in adj_f[root]:
        parent[nb] = root
        shared[nb] = adj_f[root][nb]
        frontier.append(nb)
    while len(parent) < len(adj_f):
        u = frontier.pop(int(rng.integers(len(frontier))))
        for v in adj_f[u]:
            if v not in parent:
                parent[v] = u
                shared[v] = adj_f[u][v]
                frontier.append(v)
    return parent, shared


def place_faces(V, faces, parent, shared, root):
    """Unfold every face into 2-D using the spanning tree.

    The root face is laid out as a regular polygon.  Each child is
    attached along its shared edge with the parent via
    :func:`attach_along_edge`.

    Args:
        V: 3-D vertex array.
        faces: List of faces.
        parent: Parent dict from the spanning tree.
        shared: Shared-edge dict.
        root: Root face index.

    Returns:
        Dict mapping face index to ``(2d_vertices, 3d_vertex_indices)``.
    """
    placed: dict[int, PlacedFace] = {}
    f0 = faces[root]
    n0 = len(f0)
    edge_len = float(np.linalg.norm(V[f0[0]] - V[f0[1]]))
    placed[root] = (
        create_regular_polygon(
            n0,
            edge_len / (2.0 * np.sin(np.pi / n0)),
            start_angle=np.pi / 2,
        ),
        list(f0),
    )

    children: dict[int, list[int]] = {i: [] for i in range(len(faces))}
    for ch, par in parent.items():
        if par is not None:
            children[par].append(ch)

    dq = deque([root])
    while dq:
        u = dq.popleft()
        v2d_u, v3d_u = placed[u]
        ku = len(v3d_u)
        for ch in children[u]:
            a, b = shared[ch]
            # 找到父面中邊 a->b 對應的 2-D 索引
            idx = next(i for i in range(ku) if v3d_u[i] == a and v3d_u[(i + 1) % ku] == b)
            verts, _ = attach_along_edge(v2d_u[idx], v2d_u[(idx + 1) % ku], len(faces[ch]))
            # 旋轉 3D 序使 a 排第一，使其與 2D 多邊形序對齊
            j = faces[ch].index(a)
            placed[ch] = (verts, faces[ch][j:] + faces[ch][:j])
            dq.append(ch)

    if len(placed) != len(faces):
        raise ValueError("Not all faces were placed")
    return placed


# --- Overlap detection (SAT) -----------------------------------------------
def _separated(P, Q, eps=1e-4):
    """SAT: return ``True`` if convex polygons *P* and *Q* are separated.

    Projections on every face normal are tested; a gap on any axis
    (within *eps*) means no overlap.

    Args:
        P: (N, 2) polygon.
        Q: (M, 2) polygon.
        eps: Contact tolerance.

    Returns:
        True if the polygons do not overlap.
    """
    for poly in (P, Q):
        n = len(poly)
        for i in range(n):
            edge = poly[(i + 1) % n] - poly[i]
            axis = np.array([-edge[1], edge[0]])
            axis /= np.linalg.norm(axis)
            p_proj = P @ axis
            q_proj = Q @ axis
            if p_proj.max() <= q_proj.min() + eps or q_proj.max() <= p_proj.min() + eps:
                return True
    return False


def is_valid_net(placed):
    """Check that no two face polygons in the net overlap (SAT).

    Uses a bounding-box pre-filter before the full SAT test.

    Args:
        placed: Face-placement dict.

    Returns:
        True if the net is overlap-free.
    """
    ids = sorted(placed)
    for k in range(len(ids)):
        P = placed[ids[k]][0]
        for l in range(k + 1, len(ids)):
            Q = placed[ids[l]][0]
            # 包圍盒預篩 — 明顯分開則跳過 SAT
            if (
                P[:, 0].max() <= Q[:, 0].min() + 1e-4
                or Q[:, 0].max() <= P[:, 0].min() + 1e-4
                or P[:, 1].max() <= Q[:, 1].min() + 1e-4
                or Q[:, 1].max() <= P[:, 1].min() + 1e-4
            ):
                continue
            if not _separated(P, Q):
                return False
    return True


def find_net(V, faces, adj_f, root, seed=11, max_tries=6000):
    """Find a non-overlapping net by trial-and-error on random trees.

    Args:
        V: 3-D vertex array.
        faces: List of faces.
        adj_f: Face adjacency list.
        root: Root face index.
        seed: RNG seed for reproducibility.
        max_tries: Maximum spanning-tree attempts.

    Returns:
        (placed, parent, attempts).

    Raises:
        RuntimeError: if no valid net is found within *max_tries*.
    """
    rng = np.random.default_rng(seed)
    for attempt in range(1, max_tries + 1):
        parent, shared = random_spanning_tree(adj_f, root, rng)
        placed = place_faces(V, faces, parent, shared, root)
        if is_valid_net(placed):
            return placed, parent, attempt
    raise RuntimeError("No overlap-free net found; raise max_tries or change seed")


# --- Dual-graph edges ------------------------------------------------------
def dual_segments(placed, adj_f):
    """Compute dual edges that are physically glued in the 2-D net.

    For each pair of adjacent faces, the shared vertices must
    coincide in 2-D for the dual edge to be drawn — this avoids
    spurious "flying" lines across the unfolded sheet.

    Args:
        placed: Face-placement dict.
        adj_f: Face adjacency list.

    Returns:
        (segments, centroids) where *segments* is a list of
        ``(centroid_f, centroid_g)`` pairs and *centroids* maps
        face index to centroid.
    """
    vmap: dict[int, dict[int, np.ndarray]] = {}
    cent: dict[int, np.ndarray] = {}
    for f, (v2d, v3d) in placed.items():
        vmap[f] = {v3d[i]: v2d[i] for i in range(len(v3d))}
        cent[f] = v2d.mean(axis=0)
    segs: list[tuple[np.ndarray, np.ndarray]] = []
    seen: set[tuple[int, int]] = set()
    for f in placed:
        for g, (a, b) in adj_f[f].items():
            if (g, f) in seen:
                continue
            seen.add((f, g))
            if np.linalg.norm(vmap[f][a] - vmap[g][a]) < 1e-6 and np.linalg.norm(vmap[f][b] - vmap[g][b]) < 1e-6:
                segs.append((cent[f], cent[g]))
    return segs, cent


__all__ = [
    "attach_along_edge",
    "build_face_adjacency",
    "build_truncated_icosahedron",
    "create_regular_polygon",
    "dual_segments",
    "find_faces",
    "find_net",
    "is_valid_net",
    "place_faces",
    "random_spanning_tree",
]
