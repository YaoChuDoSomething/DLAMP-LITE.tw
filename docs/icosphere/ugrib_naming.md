# UGRIB Naming Conventions

UGRIB (Unstructured GRIB) extends GRIB2 conventions to unstructured
grids. This document specifies the **vertex ordering**, **boundary edge
ordering**, and **polygon face numbering** conventions for bulkyball
meshes unfolded into a 2-D planar layout.

## Overview

UGRIB data is stored as sequential arrays. The ordering of vertices,
boundary edges, and faces in these arrays affects:

- **Data locality** — spatially nearby elements should have nearby IDs
- **I/O efficiency** — sequential reads follow the numbering
- **Interoperability** — consistent across implementations
- **Symmetry exploitation** — for point-symmetric layouts, the numbering
  should reflect the symmetry

## 1. Vertices Numbering (頂點編號順序)

### Definition of Vertices

A **vertex** is a node of the mesh graph. In the 2-D unfolded layout,
vertices are points where face corners meet.

### UGRIB Convention (Vertices)

Vertices are numbered in **two phases**:

#### Phase 1 — Boundary vertices

All vertices on the **external boundary** of the unfolded net are numbered
first, in counterclockwise traversal order starting from the
**leftmost-bottommost** vertex (the vertex with the smallest `x` coordinate,
breaking ties by smallest `y` coordinate).

```test
    v0 ─── e0 ─── v1 ─── e1 ─── v2
     │                    │
    e3                   e2
     │                    │
    v3 ─────────────── v4
```

Starting vertex = leftmost-bottommost (here: `v0`). Counterclockwise:
`v0 → v1 → v2 → v4 → v3`.

**Vertex IDs**: `0, 1, 2, 3, 4` for boundary; `5, 6, ...` for interior.

#### Phase 2 — Interior vertices

All vertices **not** on the boundary are numbered second, in
**row-major spatial order** (left-to-right, bottom-to-top, scanning
`y` then `x`).

#### Point-Symmetric Layout Extension (Vertices)

For a layout with point symmetry (centre at origin), the numbering
satisfies:

```test
vertex i ↔ vertex (N - 1 - i)
```

where `N` is the total vertex count. The leftmost-bottommost boundary
vertex (ID 0) maps to the rightmost-topmost vertex (ID `N-1`).

**Implementation** — when the layout is point-symmetric:

1. Number boundary vertices in counterclockwise order from the
   leftmost-bottommost vertex.
2. Number interior vertices in row-major order.
3. The antipodal vertex `v'` of vertex `v` at position `(x, y)` is at
   `(-x, -y)`. Its ID is `N - 1 - id(v)` (if the starting vertex lies
   on a symmetry axis) or `(id(v) + N/2) mod N`.

### Vertices Data Array

In UGRIB, vertex coordinates are stored as:

```text
lat[N], lon[N]   # latitude/longitude of each vertex
x[N], y[N]       # 2-D planar coordinates (for unfolded layout)
```

## 2. Boundary Edges Ordering (邊界稜線的編號順序)

### Definition of Boundary Edges

A **boundary edge** is a dual-graph edge that was **cut** during
unfolding (i.e., an edge of the original polyhedron that does NOT appear
as a shared edge between two faces in the 2-D net). Boundary edges form
the perimeter of the unfolded layout.

### UGRIB Convention (Boundary Edges)

Boundary edges are numbered in **counterclockwise traversal order** along
the perimeter, starting from the leftmost-bottommost boundary vertex.

#### Traversal Rules (Boundary Edges)

1. Start at the leftmost-bottommost boundary vertex.
2. Walk counterclockwise (always turning left at vertices).
3. At each step, the next boundary edge is the one that goes furthest
   left (smallest angle from the incoming direction, measured
   counterclockwise).
4. When two edges have the same angle, take the shorter one.

**Edge ID** = sequential counter, starting at 0.

#### Point-Symmetric Layout Extension (Boundary Edges)

For point-symmetric layouts:

```test
boundary edge j ↔ boundary edge (M - 1 - j)
```

where `M` is the total boundary edge count. This holds because
reflecting the entire layout through the origin reverses the boundary
traversal direction, mapping edge `j` (at position `p`) to edge `M-1-j`
(at position `-p`).

When the starting vertex lies on a symmetry axis (e.g., the
leftmost-bottommost vertex has its antipode also on the boundary), the
pairing is `j ↔ M-1-j`. When no vertex lies on the axis, the pairing is
`j ↔ (j + M/2) mod M`.

#### Boundary Edges Data Array

```text
bnd_v1[M], bnd_v2[M]    # vertex pair for each boundary edge
bnd_face[M]             # face ID on the interior side of each boundary edge
bnd_len[M]              # Euclidean length of each boundary edge
```

## 3. Faces Numbering (多邊形面的編號順序)

### Definition of Faces

A **face** (polygon) is a cell of the mesh — a pentagon or hexagon on
the sphere. In UGRIB, each face carries bulk variables (temperature,
pressure, etc.).

### UGRIB Convention (Faces)

Faces are numbered in **spatial order** within the 2-D unfolded layout:

#### Primary Ordering: Row-Major Spatial Order (Faces)

1. Compute the 2-D axis-aligned bounding box of each face (centroid
   coordinates).
2. Sort faces by `y` coordinate (bottom-to-top), then by `x`
   coordinate (left-to-right) within each row.
3. Assign IDs starting at 0.

```text
Row 0:  f0  f1  f2
Row 1:  f3  f4
Row 2:  f5  f6  f7  f8
```

#### Point-Symmetric Layout Extension (Faces)

For point-symmetric layouts:

```text
face k ↔ face (F - 1 - k)
```

where `F` is the total face count (32 for truncated icosahedron). The
face at the bottom-left corner of the layout (ID 0) maps to the face at
the top-right corner (ID `F-1`).

#### UGRIB Faces Connectivity

```text
nfaces                   # 32 for truncated icosahedron
face_nv[F]               # number of vertices per face (5 or 6)
face_v[F][K]            # vertex IDs for each face (K = max face_nv)
face_data[F][Nvars][Nlev]  # bulk variable data per face
```

### Alternative: 3D Mesh ID Preservation (Faces)

For workflows that remap data between the 3-D spherical mesh and the 2-D
unfolded layout, faces may retain their **3-D mesh IDs**:

- Face IDs follow the order of faces as generated by `find_faces()`.
- This preserves data continuity: a variable value stored at 3-D face `i`
  remains at 2-D face `i` after unfolding.

This alternative is **not** the default UGRIB convention but may be used
when round-trip remapping is required.

## 4. The Complete UGRIB Header Structure

```text
UGRIB Header:
  magic: "UGRB"            # 4-byte magic number
  version: uint32          # format version (1)
  nvertices: uint32        # total vertex count (60)
  nfaces: uint32           # total face count (32)
  nboundary: uint32        # total boundary edge count
  layout_type: uint8       # 0=flat, 1=point-symmetric, 2=reflective

  # Vertices data (Phase 1: boundary, Phase 2: interior)
  lat[nvertices]           # latitude per vertex
  lon[nvertices]           # longitude per vertex
  x_2d[nvertices]          # 2-D x coordinate
  y_2d[nvertices]          # 2-D y coordinate
  is_boundary[nvertices]   # boolean: on boundary?

  # Faces connectivity
  face_nv[nfaces]          # vertex count per face
  face_v_offsets[nfaces]   # offset into face_v array
  face_v[sum(face_nv)]    # flattened vertex IDs

  # Boundary edges
  bnd_v1[nboundary]        # first vertex of each boundary edge
  bnd_v2[nboundary]        # second vertex
  bnd_face[nboundary]      # face on interior side
  bnd_face_edge[nboundary] # edge index within face (local)

  # Bulk data
  nvars: uint32
  nlevels: uint32
  face_data[nfaces][nvars][nlevels]  # data values
```

## 5. Summary of Numbering Relationships

| Element | Ordering | Count | Symmetric Pairing |
| --------- | ---------- | ------- | ------------------- |
| Vertices | Boundary (CCW) → Interior (row-major) | 60 | `i ↔ N-1-i` |
| Boundary edges | CCW from leftmost-bottommost | ~31 | `j ↔ M-1-j` |
| Faces | Row-major (spatial in 2-D) | 32 | `k ↔ F-1-k` |

### Symmetry Pairing Conditions

The pairing `i ↔ N-1-i` (vertices), `j ↔ M-1-j` (boundary edges), and
`k ↔ F-1-k` (faces) holds **exactly** when:

1. The 2-D layout has exact point symmetry (centre at origin).
2. The starting reference point (leftmost-bottommost) lies on a
   symmetry axis.

When the layout is approximately symmetric (e.g., zipper unfolding),
the pairing is approximate. UGRIB consumers should use a tolerance
when testing for symmetry.

### Cross-Reference Consistency

For a correctly numbered point-symmetric net:

- If vertex `i` is at position `(x, y)`, then vertex `N-1-i` is at
  `(-x, -y)`.
- If face `k` has centroid at `(cx, cy)`, then face `F-1-k` has centroid
  at `(-cx, -cy)`.
- The boundary vertex with ID 0 is the leftmost-bottommost; its
  antipode (ID `N-1`) is the rightmost-topmost.

These invariants allow UGRIB consumers to efficiently compute symmetric
counterparts without storing explicit mapping tables.
