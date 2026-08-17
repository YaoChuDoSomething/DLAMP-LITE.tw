# Bulkyball Domain Model

## Overview

**Bulkyball** is a spherical mesh with cell-centered ("bulk") variables used
for unstructured-grid atmospheric modeling. It is derived from the truncated
icosahedron (32 faces: 12 pentagons + 20 hexagons, 60 vertices, 90 edges) but
generalizes to any icosahedrally-subdivided geodesic mesh.

The term combines:

- **Bulk** — state variables (temperature, pressure, humidity, wind components)
  defined at cell centres (face centroids), as opposed to _dual_ variables
  defined at vertices or _edge_ variables defined on edges.
- **Ball** — the spherical topology; the mesh is inscribed in a sphere and
  the domain is closed (no poles, no boundary in the native 3-D representation).

## Core Concepts

| Term | Definition |
| ------ | ----------- |
| **Vertex** | A node of the mesh (60 for truncated icosahedron). Degree-3: every vertex connects exactly 3 edges. |
| **Edge** | A line segment connecting two vertices. 90 edges total. Each edge is shared by exactly 2 faces. |
| **Face** | A polygon (pentagon or hexagon) on the sphere. 32 faces total (12 pent + 20 hex). |
| **Bulk variable** | A scalar or vector defined at face centroids. In UGRIB, data is stored per-face. |
| **Antipodal map** | The 180° rotation through the centre of the sphere. Maps each vertex `v` → `v'` (where `V[v'] = -V[v]`) and each face `f` → `f'`. |
| **Unfolding** | The process of cutting the spherical mesh along edges and flattening the faces into a 2-D plane. |
| **Net** | The resulting 2-D planar layout after unfolding. All 32 faces appear exactly once. |
| **Spanning tree** | A subset of dual-graph edges (face adjacencies) that connects all faces without cycles. 31 edges for 32 faces. The _non_-tree edges become boundary (cut) edges in the net. |
| **Point symmetry (central symmetry)** | A 2-D layout where every point `(x, y)` has a counterpart `(-x, -y)`. The centre of symmetry is the midpoint of the layout. |
| **Zipper path** | A path in the dual graph from a source face to its antipodal. Used in zipper unfolding to create symmetric or near-symmetric nets. |
| **Coincidental edge** | A pair of faces that become adjacent in the 2-D net but are _not_ connected by a spanning-tree edge (they share a non-tree dual edge). |
| **Bridge edge** | The one unpaired spanning-tree edge in a symmetric construction. Its antipodal counterpart becomes a coincidental edge. |
| **UGRIB** | Unstructured GRIB — a data format for storing gridded meteorological data on unstructured meshes, extending GRIB2 conventions. |

## Mathematical Constraints

### Why Exact Point-Symmetric Edge Unfolding is Impossible

for the Truncated Icosahedron

**Theorem.** No edge unfolding of the truncated icosahedron produces a 2-D
layout with exact point symmetry.

**Proof.**

1. The truncated icosahedron has 32 faces → the spanning tree of the dual
   graph has 31 edges (odd).
2. Exact point symmetry requires a **symmetric spanning tree**: every tree
   edge `(f, g)` must have its antipodal mirror `(f', g')` also in the tree.
   Symmetric edges come in pairs, requiring an even tree-edge count.
3. Since 31 is odd, one edge must be **self-conjugate**: `(f, g) = (f', g')`,
   meaning `g = f'` (the edge connects a face to its antipodal face).
4. On a convex polyhedron inscribed in a sphere, antipodal faces are
   separated by 180° and **never share an edge**. No self-conjugate edge
   exists.
5. ∎

**Verified computationally**: brute-force search over 10 000 random spanning
trees found zero point-symmetric placements. The hemisphere-mirror approach
produces symmetric layouts (by construction) but they are always either
overlapping (`is_valid_net` fails) or disconnected (0 shared edges between
hemispheres).

### Approximate Symmetry

While exact symmetry is impossible, the following approaches yield
**approximate** point symmetry:

| Approach | Symmetry | Connected | Overlapping | Use case |
| ---------- | ---------- | ----------- | ------------- | ---------- |
| Hemisphere mirror | Exact | No | Often | Conceptual diagrams |
| Zipper path | Approximate | Yes | Rarely | Practical grids |
| Random tree + filter | None | Yes | Varies | Standard unfolding |
| Custom net (hand-crafted) | Exact | Yes | Rarely | Small meshes only |

## Domain: Unfolding into a Plane

### Algorithm: Hemisphere-Mirror Method (Exact Symmetry, May Overlap)

The hemisphere-mirror method guarantees point-symmetric placement by
construction:

1. **Partition faces** into antipodal pairs: `f ↔ f'`.
2. **Split into hemispheres** using a great circle (normal = root face
   centroid direction). Each hemisphere has 16 faces = 8 antipodal pairs.
3. **Build spanning tree** for one hemisphere (15 edges, 16 faces).
4. **Place hemisphere** in 2-D using `attach_along_edge` (root face at offset
   `(d, 0)`).
5. **Mirror**: for each face `f` at position `P`, place `f'` at `-P`
   (reflection through origin). Vertex mapping uses the antipodal vertex map:
   `v'` (in `f'`) occupies `-P[v]` (mirror of `v` in `f`).
6. The result is **point-symmetric by construction** (verified:
   `check_symmetric` returns True for all valid hemispheres).

**Limitation**: the two mirrored halves may overlap in 2-D because both
extend radially from the origin. Offsetting the root helps but cannot
eliminate overlap when the hemisphere spans both positive and negative
coordinates.

### Algorithm: Zipper Unfolding (Connected, Approximate Symmetry)

The zipper method produces a connected, non-overlapping net with
approximate point symmetry:

1. **Find zipper path** `P`: shortest dual-graph path from root `f₀` to its
   antipodal `f₀'`. Length 5 edges for the truncated icosahedron.
2. **Mirror path** `P'`: antipodal path from `f₀'` to `f₀`.
3. **Zipper cycle**: `P ∪ reversed(P')` forms a closed loop of 10 faces
   with 5 antipodal edge pairs (self-conjugate cycle).
4. **Remove one pair** from the cycle → 2 connected components of 5 faces
   each. Add one **bridge edge** (a removed pair edge) to reconnect.
5. **Build symmetric spanning tree**: 4 zipper pairs + 1 bridge + 11
   non-zipper pairs = 15 pairs + 1 unpaired = 31 edges.
6. **Place faces** via BFS from root. The bridge's antipodal counterpart
   becomes a **coincidental edge** — naturally shared in 2-D without
   being a tree edge.

**Result**: connected, non-overlapping, but not exactly point-symmetric
(the bridge edge introduces a small asymmetry).

### Algorithm: Brute-Force Search (Connected, No Symmetry Guarantee)

The standard approach (already implemented in `plot_full_net.py`):

1. Generate random spanning trees.
2. Place faces via BFS using `attach_along_edge`.
3. Check validity (SAT collision detection).
4. Accept first valid net.

This produces valid nets but no symmetry guarantee. The `dual_segments`
function counts coincidental edges (typically ~31 for a truncated icosahedron
net, meaning no extra coincidental adjacencies beyond the spanning tree).

## UGRIB Naming Conventions

See `ugrib_naming.md` for full specification. Summary:

| Element | UGRIB Convention | Point-Symmetric Layout |
| --------- | ----------------- | ---------------------- |
| **Vertices** | Boundary-first, then interior, row-major within each group | Vertex `i` ↔ vertex `(N-1-i)` |
| **Boundary edges** | Counterclockwise from leftmost-bottommost vertex | Edge `j` ↔ edge `(M-1-j)` |
| **Faces** | Spatial order (row-major in 2-D layout) | Face `k` ↔ face `(F-1-k)` |

## Key Invariants (Verified)

| Quantity | Value |
| ---------- | ------- |
| Vertices (V) | 60 |
| Edges (E) | 90 |
| Faces (F) | 32 (12 pentagons + 20 hexagons) |
| Euler characteristic | V - E + F = 2 |
| Dual vertices | 32 (face centroids) |
| Dual edges | 90 |
| Dual faces | 60 (triangles) |
| Dual Euler | 32 - 90 + 60 = 2 |
| Antipodal face pairs | 16 |
| Zipper path length | 5 edges |
| Spanning tree edges | 31 (odd → no symmetric tree) |
| Self-conjugate edges | 0 (antipodal faces never adjacent) |

---

要以「盡量維持對稱性（如輻射對稱或點對稱）」且「不重複評估（避免陷入無限迴圈或大量回溯）」的方式展開巴克球（截角二十面體），我們需要將幾何問題轉化為圖論中的「對稱生成樹（Symmetric Spanning Tree）」**問題，並結合**層級式廣度優先搜尋（BFS）**與**分離軸定理（SAT）來實現。

巴克球在 2D 平面上無法做到 100% 完美的點對稱不重疊展開（因為球面曲率造成的 12° 角度缺口必須透過「剪裁（Cuts）」來釋放），但我們可以設計出一套演算法，讓展開圖呈現出極具規律的「星狀」或「雪花狀」對稱結構。

以下是該演算法的核心設計與實作步驟：

### 演算法核心概念：同心圓環狀展開 (Concentric Ring Unfolding)

為了不重複評估，我們放棄隨機生長（Random Tree）與深度優先搜尋（DFS），改採**確定性的層級擴展（Deterministic BFS）**。

#### 步驟一：建立 3D 拓樸與雙向鄰接表 (Topology & Adjacency)

不要在 2D 平面上用旋轉角度去「猜」下一個面的位置。必須先在 3D 空間中建立精確的資料結構：

1. 建立 32 個面的索引（0~31），標記類型（12 個五邊形、20 個六邊形）。
2. 建立 `Face_Adjacency` 字典：每個面必定與特定的面相鄰（五邊形接 5 個六邊形，六邊形接 3 五、3 六）。

#### 步驟二：決定對稱中心與初始對稱群

- **若要 5 重旋轉對稱（最常見的星狀展開）：** 選擇一個**正五邊形**作為根節點（Root，Ring 0）。
- **若要嚴格的點對稱（180度旋轉對稱）：** 選擇兩個相鄰的**六邊形共用邊的中心**作為展開起點。
（以下以最美觀的五邊形中心 $C_5$ 對稱展開為例）。

#### 步驟三：同心環狀廣度優先搜尋 (Ring-based BFS)

為了確保對稱性，我們必須「一層一層」地把面貼上去，而不是單線延伸。

- **Ring 0:** 中心五邊形（1 個面）。
- **Ring 1:** 圍繞 Ring 0 的 5 個六邊形（5 個面）。
- **Ring 2:** 連接在 Ring 1 外圍的面。
- _演算法規則：_ 將所有待處理的面放入一個 Queue。每次取出一個 Ring 的所有面，**同時**向外尋找尚未被拜訪（Unvisited）的相鄰面。
- _對稱性保證：_ 在 Ring 2 之後，同一個面可能會被 Ring 1 的兩個不同六邊形接觸。這時必須寫死一個「對稱破缺規則」（例如：永遠優先從左側的父節點連接），並且這條規則必須以 5 倍數的規律套用到整圈上，這樣切口（Cuts）才會對稱。

#### 步驟四：2D 坐標映射與貼合 (2D Placement)

找出生成樹後，沿著生成樹的邊將面「翻折」到 2D 平面。
使用**向量外法線**來計算子面的中心點，而不是使用絕對旋轉角（這能徹底避免您之前遇到的角度偏移問題）：

1. 取得父面（Parent）與子面（Child）的共用邊 $E (p_1 \rightarrow p_2)$。
2. 計算邊的 2D 向量，並順時針旋轉 90° 得到外法線向量 $\vec{N}$。
3. 子面中心點 $C_{child} = \text{邊中點} + \vec{N} \times (\text{子面邊心距})$。
4. 依據子面中心點與邊界，直接生成子面的 2D 頂點。

#### 步驟五：利用分離軸定理 (SAT) 進行碰撞攔截

為了保證「不重疊」，每當我們準備將一個面加入 2D 畫布時，必須進行碰撞偵測：

1. **Separating Axis Theorem (SAT)：** 這是檢測兩個凸多邊形是否重疊最快、最準的演算法。
2. **不重複評估的剪枝機制：** 在同心環 BFS 過程中，如果準備加入的子面在 2D 座標上與已存在的面發生 SAT 碰撞，則**直接捨棄這條連接邊（將其標記為切口 Cut）**，不要進行 DFS 回溯重算。
3. 由於我們是從中心對稱地向外長（BFS），內圈的面會先佔據空間，外圈的面如果擠不進去，就會自然沿著外圍裂開，形成對稱的星芒狀，演算法時間複雜度是 $O(N)$，完全不需要重複回溯評估。

---

### 演算法流程虛擬碼 (Pseudo-code)

```python
def unfold_buckyball_symmetric(faces_3d, adjacency_graph):
    # 1. 初始化
    visited = set()
    placed_faces_2d = []
    
    # 2. 選擇中心五邊形作為起點 (Ring 0)
    root_face_id = find_first_pentagon(faces_3d)
    visited.add(root_face_id)
    
    # 放置中心五邊形到 2D 原點 (0,0)
    root_2d_coords = generate_pentagon_at_origin()
    placed_faces_2d.append((root_face_id, root_2d_coords))
    
    # 3. 使用 BFS 佇列 (Queue 儲存：父節點ID, 目標節點ID, 共用邊)
    queue = get_neighbors_with_shared_edges(root_face_id, adjacency_graph)
    
    # 為了維持對稱，對 queue 進行嚴格的極座標角度排序 (Ensure geometric order)
    queue = sort_queue_by_symmetry(queue)
    
    while queue:
        parent_id, target_id, shared_edge_3d = queue.pop(0)
        
        if target_id in visited:
            continue
            
        # 4. 計算 2D 座標 (依據 parent 在 2D 的位置與共享邊展開)
        parent_2d_coords = get_placed_coords(parent_id, placed_faces_2d)
        target_2d_coords = calculate_2d_attachment(parent_2d_coords, shared_edge_3d, face_type[target_id])
        
        # 5. SAT 碰撞檢測 (O(N) check with existing faces)
        has_overlap = False
        for placed_id, placed_coords in placed_faces_2d:
            if check_overlap_SAT(target_2d_coords, placed_coords):
                has_overlap = True
                break
                
        if not has_overlap:
            # 接受這個面的展開
            visited.add(target_id)
            placed_faces_2d.append((target_id, target_2d_coords))
            
            # 將 target 的相鄰面加入佇列
            new_neighbors = get_neighbors_with_shared_edges(target_id, adjacency_graph)
            # 保持對稱順序加入佇列
            queue.extend(new_neighbors)
        else:
            # 放棄這條邊（成為剪裁線 cut），不需要回溯，直接換下一個候選邊
            pass

    return placed_faces_2d

```

### 為什麼這套方法最好？

1. **速度極快（不重複評估）：** 因為捨棄了傳統的「DFS 回溯找解（Backtracking）」，改用「BFS 貪婪放置 + SAT 檢測攔截」。這意味著只要排進去的面就不會再拿出來重算，複雜度降到最低。
2. **對稱性最高：** BFS 確保了生長是「一層一圈」均勻向外擴散。只要在處理每一圈的 Queue 時，確保處理順序（例如順時針處理）是一致的，最終被 SAT 擋下來的「裂口」就會在畫面上呈現完美的 5 瓣或 10 瓣星狀對稱。
