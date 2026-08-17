# 2D 靈活網格拓撲 (2D Flexible Mesh Topology)

## 📖 概述

**2D 靈活網格拓撲** 是 2D 三角形網格的廣義版本，允許面 (Face) 由**任意數量的節點**組成。這種彈性使其能夠描述混合型別的網格，包含三角形、四邊形、五邊形、六邊形等不同形狀的面。

典型應用場景：

- 結構化與非結構化混合網格
- Delft3D Flexible Mesh (D-Flow FM)
- 近岸海洋模型（三角形 + 矩形混合）
- 城市洪水模型（道路網格 + 不規則地形）
- 複雜地形的水文模擬

## 🏗️ 基本結構

靈活網格支援混合面型別：

```
三角形面 (3 個節點)    四邊形面 (4 個節點)

   ●                 ●─────────●
  / \                │         │
 /   \               │         │
●─────●              │         │
                     ●─────────●

五邊形面 (5 個節點)   六邊形面 (6 個節點)

   ●                   ●─────●
  / \                 / \   / \
 ●   ●               ●   ● ●   ●
 │   │                \   │   /
 ●───●                 ●─────●
```

### 幾何元素

| 元素 | 維度 | 描述 | 必需性 |
|------|------|------|--------|
| Node | 0D | 網格頂點 | ✅ 必需 |
| Edge | 1D | 連線兩節點的線段 | ❌ 可選 |
| Face | 2D | 由 3 個以上節點圍成的多邊形 | ✅ 必需 |

## 📋 必需屬性

與 2D 三角形網格相同，但面的節點數可變：

| 屬性 | 型別 | 必需性 | 描述 |
| ------ | ------ | -------- | ------ |
| `cf_role` | string | ✅ 必需 | 固定為 `"mesh_topology"` |
| `topology_dimension` | int | ✅ 必需 | 固定為 `2` |
| `node_coordinates` | string | ✅ 必需 | 節點座標變數名 |
| `face_node_connectivity` | string | ✅ 必需 | 面-節點連線性變數名 |

### 關鍵差異：可選的維度屬性

```cdl
integer Mesh2 ;
  Mesh2:cf_role = "mesh_topology" ;
  Mesh2:topology_dimension = 2 ;
  Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
  Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
  Mesh2:face_dimension = "nMesh2_face" ;    // 可選，但建議提供
  Mesh2:edge_dimension = "nMesh2_edge" ;    // 可選，但建議提供
```

## 🔧 連線性變數

### 面-節點連線性 — 核心特點：`_FillValue`

靈活網格的關鍵在於：面的節點數不固定，使用 `_FillValue` 填充較短的行：

```cdl
integer Mesh2_face_nodes(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
  Mesh2_face_nodes:long_name = "Maps every face to its corner nodes." ;
  Mesh2_face_nodes:start_index = 0 ;
  Mesh2_face_nodes:_FillValue = -999 ;
```

其中 `nMaxNodesPerFace` 是整個網格中面的最大節點數。

#### 示例資料（混合三角形 + 四邊形）

| 面 | 節點數 | node_0 | node_1 | node_2 | node_3 |
|----|--------|--------|--------|--------|--------|
| Face 0 (三角形) | 3 | 0 | 1 | 2 | **-999** |
| Face 1 (四邊形) | 4 | 1 | 3 | 4 | 2 |
| Face 2 (三角形) | 3 | 3 | 5 | 4 | **-999** |

```cdl
data:
  Mesh2_face_nodes =
    0, 1, 2, -999,   // Face 0: 三角形
    1, 3, 4,  2,     // Face 1: 四邊形
    3, 5, 4, -999 ;  // Face 2: 三角形
```

### 邊-節點連線性 — 可選

與三角形網格相同，提供邊的端點：

```cdl
integer Mesh2_edge_nodes(nMesh2_edge, Two) ;
  Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
  Mesh2_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;
  Mesh2_edge_nodes:start_index = 0 ;
```

### 面-邊連線性 — 可選

每個面的邊數等於其節點數，同樣使用 `_FillValue`：

```cdl
integer Mesh2_face_edges(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_edges:cf_role = "face_edge_connectivity" ;
  Mesh2_face_edges:long_name = "Maps every face to its edges." ;
  Mesh2_face_edges:start_index = 0 ;
  Mesh2_face_edges:_FillValue = -999 ;
```

### 邊-面連線性 — 可選

```cdl
integer Mesh2_edge_faces(nMesh2_edge, Two) ;
  Mesh2_edge_faces:cf_role = "edge_face_connectivity" ;
  Mesh2_edge_faces:long_name = "Maps every edge to the faces it bounds (one or two)." ;
  Mesh2_edge_faces:start_index = 0 ;
  Mesh2_edge_faces:_FillValue = -999 ;
```

### 面-面連線性 — 可選

鄰居面數等於面的節點數（邊數），使用 `_FillValue`：

```cdl
integer Mesh2_face_links(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_links:cf_role = "face_face_connectivity" ;
  Mesh2_face_links:long_name = "Indicates which faces are adjacent to each face." ;
  Mesh2_face_links:start_index = 0 ;
  Mesh2_face_links:_FillValue = -999 ;
```

## 📍 座標變數

與 2D 三角形網格基本相同，但面邊界座標需要 `nMaxNodesPerFace` 維度：

```cdl
double Mesh2_node_x(nMesh2_node) ;
  Mesh2_node_x:standard_name = "longitude" ;
  Mesh2_node_x:units = "degrees_east" ;

double Mesh2_node_y(nMesh2_node) ;
  Mesh2_node_y:standard_name = "latitude" ;
  Mesh2_node_y:units = "degrees_north" ;

double Mesh2_face_x(nMesh2_face) ;
  Mesh2_face_x:standard_name = "longitude" ;
  Mesh2_face_x:long_name = "Characteristic longitude of face (e.g. centroid)." ;
  Mesh2_face_x:units = "degrees_east" ;
  Mesh2_face_x:bounds = "Mesh2_face_xbnds" ;

double Mesh2_face_y(nMesh2_face) ;
  Mesh2_face_y:standard_name = "latitude" ;
  Mesh2_face_y:long_name = "Characteristic latitude of face (e.g. centroid)." ;
  Mesh2_face_y:units = "degrees_north" ;
  Mesh2_face_y:bounds = "Mesh2_face_ybnds" ;

// 面邊界座標：nMaxNodesPerFace 維度
double Mesh2_face_xbnds(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_xbnds:_FillValue = 9.969209968386869e+36 ;  // CF 標準缺失值

double Mesh2_face_ybnds(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_ybnds:_FillValue = 9.969209968386869e+36 ;
```

## 📄 完整 CDL 示例

包含三角形和四邊形混合面的示例：

```cdl
:Conventions = "CF-1.12" ;
:title = "Example 2D Flexible Mesh (Mixed Triangle + Quad)" ;

dimensions:
  nMesh2_node = 6 ;
  nMesh2_edge = 8 ;
  nMesh2_face = 3 ;        // 3 個面 (2 個三角形 + 1 個四邊形)
  nMaxNodesPerFace = 4 ;   // 最多 4 個節點
  Two = 2 ;

variables:

  integer Mesh2 ;
    Mesh2:cf_role = "mesh_topology" ;
    Mesh2:long_name = "Topology data of 2D flexible mesh" ;
    Mesh2:topology_dimension = 2 ;
    Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
    Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
    Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;
    Mesh2:face_coordinates = "Mesh2_face_x Mesh2_face_y" ;
    Mesh2:face_dimension = "nMesh2_face" ;
    Mesh2:edge_dimension = "nMesh2_edge" ;

  integer Mesh2_face_nodes(nMesh2_face, nMaxNodesPerFace) ;
    Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
    Mesh2_face_nodes:long_name = "Maps every face to its corner nodes." ;
    Mesh2_face_nodes:start_index = 0 ;
    Mesh2_face_nodes:_FillValue = -999 ;

  integer Mesh2_edge_nodes(nMesh2_edge, Two) ;
    Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
    Mesh2_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;
    Mesh2_edge_nodes:start_index = 0 ;

  double Mesh2_node_x(nMesh2_node) ;
    Mesh2_node_x:standard_name = "longitude" ;
    Mesh2_node_x:units = "degrees_east" ;

  double Mesh2_node_y(nMesh2_node) ;
    Mesh2_node_y:standard_name = "latitude" ;
    Mesh2_node_y:units = "degrees_north" ;

  double Mesh2_face_x(nMesh2_face) ;
    Mesh2_face_x:standard_name = "longitude" ;
    Mesh2_face_x:units = "degrees_east" ;

  double Mesh2_face_y(nMesh2_face) ;
    Mesh2_face_y:standard_name = "latitude" ;
    Mesh2_face_y:units = "degrees_north" ;

data:

  Mesh2 = 0 ;

  //         node0  node1  node2  node3
  Mesh2_face_nodes =
    0, 1, 2, -999,  // Face 0: 三角形 (0,1,2)
    1, 3, 4,  2,    // Face 1: 四邊形 (1,3,4,2)
    3, 5, 4, -999 ; // Face 2: 三角形 (3,5,4)

  Mesh2_edge_nodes =
    0, 1,  // Edge 0
    1, 2,  // Edge 1
    0, 2,  // Edge 2
    1, 3,  // Edge 3
    2, 4,  // Edge 4
    3, 4,  // Edge 5
    3, 5,  // Edge 6
    4, 5 ; // Edge 7

  // 節點座標
  Mesh2_node_x = 10.0, 10.5, 10.25, 11.0, 10.75, 11.5 ;
  Mesh2_node_y = 40.0, 40.0, 40.5,  40.0, 40.5,  40.0 ;

  // 面幾何中心
  Mesh2_face_x = 10.25, 10.625, 10.917 ;
  Mesh2_face_y = 40.167, 40.25, 40.167 ;
```

## 🎯 資料變數示例

```cdl
// 定義在混合網格面上的水位資料
double Mesh2_waterlevel(time, nMesh2_face) ;
  Mesh2_waterlevel:standard_name = "sea_surface_height_above_geoid" ;
  Mesh2_waterlevel:units = "m" ;
  Mesh2_waterlevel:mesh = "Mesh2" ;
  Mesh2_waterlevel:location = "face" ;
  Mesh2_waterlevel:coordinates = "Mesh2_face_x Mesh2_face_y" ;
```

## 📊 與 2D 三角形網格的對比

| 特性 | 三角形網格 | 靈活網格 |
|------|------------|----------|
| 面形狀 | 僅三角形 | 混合（三角形、四邊形等）|
| `face_node_connectivity` 第二維 | 固定為 3 | `nMaxNodesPerFace` |
| `_FillValue` 需求 | 不需要 | 連線性和邊界需要 |
| 計算複雜度 | 較低 | 稍高 |
| 靈活性 | 較低 | 較高 |
| 典型工具 | SCHISM、FVCOM | D-Flow FM、ADCIRC |

## 🎯 最佳實踐

### 1. `_FillValue` 選擇

- ✅ 整數連線性變數使用 `-999` 或 `-1`（視 `start_index` 而定）
- ✅ 浮點座標邊界使用 CF 標準缺失值 `9.969209968386869e+36`
- ✅ 明確設置 `_FillValue` 屬性，不依賴 CF 預設值
- ❌ 不要混用不同的 `_FillValue`

### 2. 維度管理

- ✅ 提供 `face_dimension` 和 `edge_dimension` 屬性，幫助工具識別
- ✅ `nMaxNodesPerFace` 通常設為 4（三角形+四邊形混合）或更大

### 3. 面排序

- ✅ 建議逆時針 (CCW) 排列節點
- ✅ 保持整個網格的一致排序方向

## 🔗 相關文件

- [2D 三角形拓撲](2d-triangular.md) — 純三角形版本
- [核心概念](../core-concepts.md) — 連線性定義
- [資料位置](../data-location.md) — 如何在面上定義資料
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/#2d-flexible-mesh-topology)

## 📚 參考資源

- [UGRID 2D Flexible Mesh Topology](https://ugrid-conventions.github.io/ugrid-conventions/#2d-flexible-mesh-topology)
- [Delft3D FM Technical Manual](https://content.oss.deltares.nl/delft3dfm/D-Flow_FM_Technical_Reference_Manual.pdf)

---

*下一步*: [3D 分層網格](3d-layered.md) | [資料位置定義](../data-location.md)
