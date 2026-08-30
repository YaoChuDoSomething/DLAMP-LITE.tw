# 截角正二十面體展開圖-對偶網格細分之三角網格重心

基本性質：截角正二十面體

- V=60, E=90, F=32
- 五邊形面 12 個
- 六邊形面 20 個

## 前言

收到。先給結論：您的幾何數據完全正確（F=32＝12 五邊形＋20 六邊形、V=60、E=90，V−E+F=2 ✓；對偶確為五角化十二面體 Pentakis Dodecahedron），設計規劃的方向（生成樹展開＋面中心對偶連線）也是對的。但**您貼的程式碼有幾個會導致錯誤結果或無法擴展的問題**，以下先釐清，再給一份可直接執行的完整改進版。

---

## 一、原程式碼的問題盤點

1. **`attach_polygon` 的旋轉對齊推導是錯的（最關鍵）**
   - 以六邊形為例：base 六邊形 `start_angle=0` 時，第 0 條邊的方向角為 120°；代入您的 `rot_angle = edge_angle − π/3` 後，該邊方向變成 `edge_angle + 60°`，**與父邊根本差不共線**。後面 `offset` 只對齊了邊中點，結果是子面以斜交方式穿過父邊，幾何完全錯位。
   - 「貼在外側還是內側」依賴 `normal_angle = edge_angle − π/2` 這條隱含假設：**父多邊形頂點必須是逆時針序**。一旦顺序相反，子面會翻進父面內部造成重疊。
   - 這類「猜旋轉角 → 平移補中點」的寫法每換一種 n 邊形就要重推，非常脆弱。

2. **只蓋了 6 個面**（1 五邊形＋5 六邊形），是局部 patch，不是 32 面的完整展開圖。完整展開需要真正的**面鄰接數據＋生成樹＋重疊檢測**，否則無法保證平面不重叠。

3. **對偶連線是手寫的**（只硬編碼了中心五邊形的 5 輻射與六邊形環），無法擴展到全圖；正確做法是從面鄰接關係自動生成，且**只畫在展開圖中實際黏合的相鄰面對**之間，否則會出現橫跨圖面的「飛線」。

4. **小問題**：`label` 變數定義後未使用；`xlim/ylim` 寫死；matplotlib 未設定中文字型，中文標題在很多環境會變豆腐方塊。

5. 一個觀念釐清：對偶的「五輻放射」是**五邊形面中心 → 相鄰 5 個六邊形面中心**的連線（對偶頂點＝原面中心）；五邊形的「頂點」在對偶中對應的是五角化十二面體的**三角形面**，不是輻射線的起點。

---

## 二、改進設計要點

- **穩健的貼合公式**（不再碰旋轉角）：父面為逆時針序、貼合邊為有向邊 `p1→p2` 時，
  - 外法向 `n_out = (e_y, −e_x)/|e|`（邊向量順時針轉 90°）
  - 新面中心 `C = mid + r·n_out`，其中 `r = L/(2·tan(π/n))`（邊心距）、`R = L/(2·sin(π/n))`（外接圓半徑）
  - 新面頂點直接極座標生成：`θ_k = atan2(n_out) + π/n + 2πk/n`，可保證 `v0 = p1`、`v_{n−1} = p2`（機器精度內），且永遠貼在外側、維持逆時針序。
- **面數據從真實 3D 幾何得來**：用截角二十面體的偶置換座標生成 60 個頂點 → 以最小距離定邊（3-正則圖）→ **half-edge 環繞遍歷**自動找出 32 個面與面鄰接關係，避免手繪出錯。
- **展開 = 面鄰接圖上的隨機生成樹**：根面（五邊形）的 5 個鄰居強制為直接子節點（保證五輻射對偶完整可见），其餘隨機生長；每次展開後用**分離軸定理（SAT）**做凸多邊形重疊檢測，不過就換一棵樹重試，通常數十～數百次內命中。
- **對偶網格自動生成**：相鄰兩面在展開圖中共享邊端點重合（生成樹黏合處，或偶然拼合處）才畫橘色虛線，對應五角化十二面體的對偶邊。

---

## 三、完整可執行程式碼

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截角二十面體 (Truncated Icosahedron, 32 面 = 12 五邊形 + 20 六邊形)
完整二維展開圖 + 對偶（五角化十二面體）網格疊加

流程：
  1. 以偶置換座標在 3D 建構 60 個頂點
  2. half-edge 環繞遍歷求出 32 個面與面鄰接關係
  3. 隨機生成樹展開；子面沿共用邊以「邊中點 + 外法向量」翻平到 2D
  4. SAT（分離軸定理）重疊檢測，不通過即換樹重試
  5. 繪製面 + 對偶邊（僅畫展開圖中實際黏合的相鄰面對）
"""

import itertools
from collections import deque

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as PltPolygon
from matplotlib.lines import Line2D
from matplotlib import font_manager

# ---------------- 中文字型設定（找不到時自動退回英文） ----------------
_CJK = ['PingFang TC', 'Microsoft JhengHei', 'Noto Sans CJK TC',
        'Source Han Sans TC', 'SimHei', 'WenQuanYi Zen Hei']
_have = {f.name for f in font_manager.fontManager.ttflist}
plt.rcParams['font.sans-serif'] = _CJK + ['DejaVu Sans']
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False
USE_CJK = bool(_have & set(_CJK))

def T(zh, en):
    return zh if USE_CJK else en

PENTAGON_COLOR = '#FF9999'   # 五邊形：淡粉紅
HEXAGON_COLOR  = '#E6F2FF'   # 六邊形：淡藍
DUAL_COLOR     = '#FF8C00'   # 對偶網格：亮橙

# ---------------- 2D 幾何工具 ----------------
def create_regular_polygon(sides, radius, center=(0.0, 0.0), start_angle=0.0):
    a = start_angle + 2.0 * np.pi * np.arange(sides) / sides
    return np.column_stack([center[0] + radius * np.cos(a),
                            center[1] + radius * np.sin(a)])

def attach_along_edge(p1, p2, sides):
    """沿有向邊 p1→p2（父多邊形為逆時針序）在外側貼上正 `sides` 邊形。
    傳回 (頂點陣列, 中心)，且 v0 == p1、v[-1] == p2（機器精度內）。"""
    p1 = np.asarray(p1, float); p2 = np.asarray(p2, float)
    e = p2 - p1
    L = np.hypot(e[0], e[1])
    mid = 0.5 * (p1 + p2)
    n_out = np.array([e[1], -e[0]]) / L            # 邊向量順時針轉 90° = 外側
    apothem = L / (2.0 * np.tan(np.pi / sides))    # 邊心距（內切圓半徑）
    radius  = L / (2.0 * np.sin(np.pi / sides))    # 外接圓半徑
    center = mid + apothem * n_out
    theta = np.arctan2(n_out[1], n_out[0])         # 中心 → 邊中點 的方向角
    a = theta + np.pi / sides + 2.0 * np.pi * np.arange(sides) / sides
    verts = center + radius * np.column_stack([np.cos(a), np.sin(a)])
    return verts, center

# ---------------- 3D 截角二十面體 ----------------
def build_truncated_icosahedron():
    """偶置換座標生成 60 頂點；以最小距離定邊（3-正則）。"""
    phi = (1.0 + np.sqrt(5.0)) / 2.0
    pts = []
    for triple in ((0.0, 1.0, 3.0 * phi),
                   (1.0, 2.0 + phi, 2.0 * phi),
                   (phi, 2.0, 2.0 * phi + 1.0)):
        even = [triple, (triple[1], triple[2], triple[0]),
                (triple[2], triple[0], triple[1])]
        n_nonzero = sum(1 for x in triple if x != 0.0)
        for base in even:
            for signs in itertools.product((-1.0, 1.0), repeat=n_nonzero):
                it = iter(signs)
                pts.append([x * next(it) if x != 0.0 else 0.0 for x in base])
    V = np.array(pts)
    assert len(V) == 60

    D = np.linalg.norm(V[:, None, :] - V[None, :, :], axis=2)
    L = D[D > 1e-9].min()                           # 邊長（= 2.0）
    adj = [[int(j) for j in np.where(D[i] < L * 1.01)[0] if j != i]
           for i in range(len(V))]
    assert all(len(a) == 3 for a in adj)
    return V, adj

def find_faces(V, adj):
    """half-edge 遍歷：每個頂點處將鄰居按切平面方位角排序，
    沿「下一條逆時針邊」行走即繞出一個面。回傳 32 個面（外視逆時針）。"""
    cyclic = []
    for v in range(len(V)):
        n = V[v] / np.linalg.norm(V[v])            # 凸多面體：外法向 ≈ 徑向
        ref = np.array([1.0, 0, 0]) if abs(n[0]) < 0.9 else np.array([0.0, 1.0, 0])
        t1 = np.cross(n, ref); t1 /= np.linalg.norm(t1)
        t2 = np.cross(n, t1)
        cyclic.append(sorted(adj[v],
                             key=lambda u: np.arctan2((V[u] - V[v]) @ t2,
                                                      (V[u] - V[v]) @ t1)))
    face_of, faces = {}, []
    for u in range(len(V)):
        for v in adj[u]:
            if (u, v) in face_of:
                continue
            face, a, b = [], u, v
            while (a, b) not in face_of:
                face_of[(a, b)] = len(faces)
                face.append(a)
                lst = cyclic[b]
                a, b = b, lst[(lst.index(a) + 1) % len(lst)]
            faces.append(face)
    assert sorted(map(len, faces)) == [5] * 12 + [6] * 20
    return faces, face_of

def build_face_adjacency(faces, face_of):
    """adj[f][g] = (a, b)：面 f 與面 g 共用邊，(a,b) 為面 f 逆時針序下的有向邊。"""
    adj = [dict() for _ in faces]
    for f, face in enumerate(faces):
        k = len(face)
        for i in range(k):
            a, b = face[i], face[(i + 1) % k]
            adj[f][face_of[(b, a)]] = (a, b)
    return adj

# ---------------- 生成樹展開 + 重疊檢測 ----------------
def random_spanning_tree(adj, root, rng):
    """隨機生長生成樹；根面的所有鄰居強制為直接子節點，
    保證中心五邊形的 5 條對偶輻射完整出現。"""
    parent = {root: None}
    shared = {}
    frontier = [root]
    for n in adj[root]:
        parent[n] = root
        shared[n] = adj[root][n]
        frontier.append(n)
    while len(parent) < len(adj):
        u = frontier.pop(int(rng.integers(len(frontier))))
        for v in [n for n in adj[u] if n not in parent]:
            parent[v] = u
            shared[v] = adj[u][v]
            frontier.append(v)
    return parent, shared

def place_faces(V, faces, parent, shared, root):
    """依生成樹把每個面翻平到 2D，回傳 {face_id: (2D頂點, 對應的3D頂點序)}。"""
    placed = {}
    f0 = faces[root]
    n0 = len(f0)
    L = float(np.linalg.norm(V[f0[0]] - V[f0[1]]))
    placed[root] = (create_regular_polygon(n0, L / (2.0 * np.sin(np.pi / n0)),
                                           start_angle=np.pi / 2), list(f0))
    children = {i: [] for i in range(len(faces))}
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
            idx = next(i for i in range(ku)
                       if v3d_u[i] == a and v3d_u[(i + 1) % ku] == b)
            verts, _ = attach_along_edge(v2d_u[idx], v2d_u[(idx + 1) % ku],
                                         len(faces[ch]))
            j = faces[ch].index(a)                  # 旋轉 3D 序使與 2D 序對齊
            placed[ch] = (verts, faces[ch][j:] + faces[ch][:j])
            dq.append(ch)
    assert len(placed) == len(faces)
    return placed

def _separated(P, Q, eps=1e-4):
    """SAT：任一分離軸上投影區間不重疊（容許 eps 內的邊界接觸）即無重疊。"""
    for poly in (P, Q):
        n = len(poly)
        for i in range(n):
            e = poly[(i + 1) % n] - poly[i]
            axis = np.array([-e[1], e[0]])
            axis /= np.linalg.norm(axis)
            p, q = P @ axis, Q @ axis
            if p.max() <= q.min() + eps or q.max() <= p.min() + eps:
                return True
    return False

def is_valid_net(placed):
    ids = sorted(placed)
    for k in range(len(ids)):
        P = placed[ids[k]][0]
        for l in range(k + 1, len(ids)):
            Q = placed[ids[l]][0]
            if (P[:, 0].max() <= Q[:, 0].min() + 1e-4 or
                Q[:, 0].max() <= P[:, 0].min() + 1e-4 or
                P[:, 1].max() <= Q[:, 1].min() + 1e-4 or
                Q[:, 1].max() <= P[:, 1].min() + 1e-4):
                continue                            # 包圍盒預篩
            if not _separated(P, Q):
                return False
    return True

def find_net(V, faces, adj, root, seed=11, max_tries=6000):
    rng = np.random.default_rng(seed)
    for attempt in range(1, max_tries + 1):
        parent, shared = random_spanning_tree(adj, root, rng)
        placed = place_faces(V, faces, parent, shared, root)
        if is_valid_net(placed):
            return placed, parent, attempt
    raise RuntimeError(T('找不到不重疊展開圖，請提高 max_tries 或更換 seed',
                         'No overlap-free net found; raise max_tries or seed'))

def dual_segments(placed, adj):
    """對偶邊：僅當兩相鄰面的共用邊端點在展開圖中實際重合才連線，
    避免非黏合面對之間出現飛線。"""
    vmap, cent = {}, {}
    for f, (v2d, v3d) in placed.items():
        vmap[f] = {v3d[i]: v2d[i] for i in range(len(v3d))}
        cent[f] = v2d.mean(axis=0)
    segs, seen = [], set()
    for f in placed:
        for g, (a, b) in adj[f].items():
            if (g, f) in seen:
                continue
            seen.add((f, g))
            if (np.linalg.norm(vmap[f][a] - vmap[g][a]) < 1e-6 and
                    np.linalg.norm(vmap[f][b] - vmap[g][b]) < 1e-6):
                segs.append((cent[f], cent[g]))
    return segs, cent

# ---------------- 繪圖 ----------------
def draw_local_patch():
    """圖一：1 五邊形 + 5 六邊形局部塊，驗證貼合公式與五輻射對偶。"""
    R5 = 1.0 / (2.0 * np.sin(np.pi / 5))
    root = create_regular_polygon(5, R5, start_angle=np.pi / 2)
    polys = [(5, root)]
    cents = [root.mean(axis=0)]
    for i in range(5):
        v, _ = attach_along_edge(root[i], root[(i + 1) % 5], 6)
        polys.append((6, v)); cents.append(v.mean(axis=0))
    dual = [(cents[0], cents[i + 1]) for i in range(5)]                  # 五輻射
    dual += [(cents[i + 1], cents[(i + 1) % 5 + 1]) for i in range(5)]   # 六邊形環

    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_aspect('equal'); ax.axis('off')
    for (n, v), _ in zip(polys, cents):
        ax.add_patch(PltPolygon(v, closed=True,
                                facecolor=PENTAGON_COLOR if n == 5 else HEXAGON_COLOR,
                                edgecolor='black', linewidth=2.0, alpha=0.85, zorder=2))
    for p1, p2 in dual:
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=DUAL_COLOR,
                linestyle='--', linewidth=2.5, zorder=3)
    for (n, _), c in zip(polys, cents):
        ax.plot(c[0], c[1], 'o', color='#C0392B' if n == 5 else '#1F618D',
                markersize=7, zorder=4)
    pts = np.vstack([v for _, v in polys])
    ax.set_xlim(pts[:, 0].min() - 0.9, pts[:, 0].max() + 0.9)
    ax.set_ylim(pts[:, 1].min() - 1.6, pts[:, 1].max() + 0.9)
    ax.set_title(T('局部對偶結構：正五邊形與 5 個相鄰六邊形（五角化十二面體的 5 輻射星）',
                   'Local dual: one pentagon with its 5 neighbouring hexagons'),
                 fontsize=14, fontweight='bold')
    ax.text(0, pts[:, 1].min() - 1.15,
            T('橘色虛線＝對偶邊：五邊形中心向外輻射 5 條，連接周圍六邊形中心；'
              '六邊形中心之間亦有對偶邊（原多面體中兩者共用一條邊）',
              'Orange dashed = dual edges between face centroids'),
            ha='center', fontsize=11,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

def draw_net(placed, segs, cent, tries):
    fig, ax = plt.subplots(figsize=(13, 11))
    ax.set_aspect('equal'); ax.axis('off')
    for f, (v2d, v3d) in placed.items():
        ax.add_patch(PltPolygon(v2d, closed=True,
                                facecolor=PENTAGON_COLOR if len(v3d) == 5 else HEXAGON_COLOR,
                                edgecolor='#222222', linewidth=1.8, alpha=0.9, zorder=2))
    for p1, p2 in segs:
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=DUAL_COLOR, linestyle='--',
                linewidth=2.2, zorder=3, solid_capstyle='round')
    for f, c in cent.items():
        n = len(placed[f][1])
        ax.plot(c[0], c[1], 'o', markersize=6.5,
                color='#C0392B' if n == 5 else '#1F618D', zorder=4)
    pts = np.vstack([v2d for v2d, _ in placed.values()])
    m = 1.2
    ax.set_xlim(pts[:, 0].min() - m, pts[:, 0].max() + m)
    ax.set_ylim(pts[:, 1].min() - m, pts[:, 1].max() + m)
    ax.set_title(T('截角二十面體完整展開圖（12 五邊形＋20 六邊形）疊加五角化十二面體對偶網格',
                   'Full net of the truncated icosahedron with pentakis dual overlay'),
                 fontsize=14, fontweight='bold')
    handles = [
        mpatches.Patch(facecolor=PENTAGON_COLOR, edgecolor='#222',
                       label=T('五邊形面（12）', 'Pentagon faces (12)')),
        mpatches.Patch(facecolor=HEXAGON_COLOR, edgecolor='#222',
                       label=T('六邊形面（20）', 'Hexagon faces (20)')),
        Line2D([0], [0], color=DUAL_COLOR, ls='--', lw=2.2,
               label=T('對偶邊（僅黏合處）', 'Dual edges (glued pairs only)')),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='#C0392B', ms=8,
               label=T('五邊形中心＝對偶 5 配位頂點', 'Pentagon centres (dual degree-5)')),
        Line2D([0], [0], marker='o', color='none', markerfacecolor='#1F618D', ms=8,
               label=T('六邊形中心＝對偶 6 配位頂點', 'Hexagon centres (dual degree-6)')),
    ]
    ax.legend(handles=handles, loc='upper right', fontsize=9, framealpha=0.9)
    ax.text(0.01, 0.01,
            T(f'生成樹嘗試次數：{tries}\nV=60　E=90　F=32（V−E+F=2）',
              f'spanning-tree attempts: {tries}\nV=60  E=90  F=32'),
            transform=ax.transAxes, fontsize=10, va='bottom',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

# ---------------- 主程式 ----------------
def main():
    draw_local_patch()                              # 圖一：局部對偶塊

    V, adj_v = build_truncated_icosahedron()        # 圖二：完整展開
    faces, face_of = find_faces(V, adj_v)
    adj_f = build_face_adjacency(faces, face_of)
    root = next(i for i, f in enumerate(faces) if len(f) == 5)   # 以五邊形為根

    placed, parent, tries = find_net(V, faces, adj_f, root, seed=11)
    segs, cent = dual_segments(placed, adj_f)

    n5 = sum(1 for f in faces if len(f) == 5)
    print(f'faces = {len(faces)}（五邊形 {n5}、六邊形 {len(faces) - n5}）、'
          f'V = {len(V)}、E = {sum(len(f) for f in faces) // 2}、'
          f'第 {tries} 次生成樹嘗試找到不重疊展開圖')
    draw_net(placed, segs, cent, tries)
    plt.show()

if __name__ == '__main__':
    main()
```

---

## 四、預期輸出與驗證點

- **主控台**：`faces = 32（五邊形 12、六邊形 20）、V = 60、E = 90、第 N 次生成樹嘗試找到不重疊展開圖`。程式內建三個 assert（60 頂點、3-正則、12×5＋20×6 面），幾何數據有錯會直接掛掉，可作為自動驗證。
- **圖一**：您原意的局部塊——粉紅五邊形＋5 個淡藍六邊形，橘色虛線呈五輻射星＋外環，對應五角化十二面體中「12 個 5 配位頂點」之一的局部結構。
- **圖二**：完整 32 面不重疊展開圖；每個紅點（五邊形中心）發出 5 條橘色虛線、每個藍點發出 6 條——正是 Pentakis Dodecahedron 的頂點配位特徵。執行時間通常數秒內（隨機樹重試＋SAT 檢測都很輕量；`seed` 可換，結果可重現）。

## 五、可再接續的擴展

1. **對偶三角形面**：原多面體每個頂點是 5.6.6 頂點組態，對應對偶的一個三角形；可在「三面兩兩黏合」處填上半透明橘色三角形，把 Pentakis 的 60 個三角面直接畫出來。
2. **3D 對偶體渲染**：把各面中心沿外法向抬升到對偶頂點高度，用 `mpl_toolkits.mplot3d` 畫出五角化十二面體與原體的疊合。
3. **折疊動畫**：沿生成樹邊把 2D 面逐幀旋轉回 3D（旋轉軸＝共用邊），可做成展開↔折疊的雙向動畫。
4. **枚舉比較**：把重試過程中所有有效網格存下來，比較包圍盒緊湊度，挑「最美」的展開樣式輸出 SVG/PDF。

如果需要我把上述任一擴展（尤其是 3D 對偶疊合或折疊動畫）實作出來，告訴我即可。
