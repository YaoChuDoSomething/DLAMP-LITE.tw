# 2D 三角形網格拓撲 (2D Triangular Mesh Topology)

## 📖 概述

**2D 三角形網格拓撲** 用於描述由三角形面組成的二維非結構化網格，是 UGRID 中最常見的拓撲型別之一。

典型應用場景：

- 海洋模型 (SCHISM、FVCOM、SELFE)
- 洪水淹沒模型
- 河口與近岸海洋模擬
- 地表水文模型

與 1D 網路相比，2D 三角形網格新增了 **面 (Face)** 這個幾何元素，表示封閉的三角形區域。

## 🏗️ 基本結構

2D 三角形網格包含三種幾何元素：

```
     Node 2
      ●
     /|\
    / | \
   /  |  \
  ●───●───●
Node 0  Node 1  Node 3
  
Face 0 (Node 0, 1, 2)
Face 1 (Node 1, 3, 2)
Edge 2 (Node 1, 2) — 共享邊
```

### 幾何元素

| 元素 | 維度 | 描述 | 必需性 |
|------|------|------|--------|
| Node | 0D | 網格頂點，帶座標 | ✅ 必需 |
| Edge | 1D | 連線兩節點的線段 | ❌ 可選 |
| Face | 2D | 由三個節點圍成的三角形 | ✅ 必需 |

## 📋 必需屬性

### 網格拓撲變數

2D 三角形網格的 `topology_dimension = 2`，並且**必須**提供
`face_node_connectivity`：

| 屬性 | 型別 | 必需性 | 描述 |
| ------ | ------ | -------- | ------ |
| `cf_role` | string | ✅ 必需 | 固定為 `"mesh_topology"` |
| `topology_dimension` | int | ✅ 必需 | 固定為 `2` |
| `node_coordinates` | string | ✅ 必需 | 節點座標變數名（空格分隔） |
| `face_node_connectivity` | string | ✅ 必需 | 面-節點連線性變數名 |

### 可選屬性

| 屬性 | 型別 | 描述 |
|------|------|------|
| `long_name` | string | 描述性名稱 |
| `edge_node_connectivity` | string | 邊-節點連線性變數名 |
| `face_edge_connectivity` | string | 面-邊連線性變數名 |
| `edge_face_connectivity` | string | 邊-面連線性變數名 |
| `face_face_connectivity` | string | 面-相鄰面連線性變數名 |
| `boundary_node_connectivity` | string | 邊界-節點連線性變數名 |
| `face_coordinates` | string | 面特徵座標變數名 |
| `edge_coordinates` | string | 邊特徵座標變數名 |
| `face_dimension` | string | 面維度名 |
| `edge_dimension` | string | 邊維度名 |

## 🔧 連線性變數

### 面-節點連線性 (Face-Node Connectivity) — 必需

描述每個三角形面由哪三個節點構成：

```cdl
int Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
  Mesh2_face_nodes:long_name = "Maps every triangular face to its three corner nodes." ;
  Mesh2_face_nodes:start_index = 0 ;
```

這是一個 **nFaces × 3** 的矩陣，每一行列出三角形的三個節點索引。

### 邊-節點連線性 (Edge-Node Connectivity) — 可選

```cdl
int Mesh2_edge_nodes(nMesh2_edge, Two) ;
  Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
  Mesh2_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;
  Mesh2_edge_nodes:start_index = 0 ;
```

### 面-邊連線性 (Face-Edge Connectivity) — 可選

每個三角形對應三條邊：

```cdl
int Mesh2_face_edges(nMesh2_face, Three) ;
  Mesh2_face_edges:cf_role = "face_edge_connectivity" ;
  Mesh2_face_edges:long_name = "Maps every face to its three edges." ;
  Mesh2_face_edges:start_index = 0 ;
```

### 邊-面連線性 (Edge-Face Connectivity) — 可選

每條邊最多相鄰兩個面（邊界邊只有一個）：

```cdl
int Mesh2_edge_faces(nMesh2_edge, Two) ;
  Mesh2_edge_faces:cf_role = "edge_face_connectivity" ;
  Mesh2_edge_faces:long_name = "Maps every edge to the faces it bounds (one or two)." ;
  Mesh2_edge_faces:start_index = 0 ;
  Mesh2_edge_faces:_FillValue = -999 ;  // 邊界邊缺少第二個面
```

### 面-面連線性 (Face-Face Connectivity) — 可選

每個三角形最多有三個相鄰面：

```cdl
int Mesh2_face_links(nMesh2_face, Three) ;
  Mesh2_face_links:cf_role = "face_face_connectivity" ;
  Mesh2_face_links:long_name = "Indicates which faces are adjacent to each face." ;
  Mesh2_face_links:start_index = 0 ;
  Mesh2_face_links:_FillValue = -999 ;  // 邊界面缺少部分鄰居
```

## 📍 座標變數

### 節點座標 (Node Coordinates) — 必需

```cdl
double Mesh2_node_x(nMesh2_node) ;
  Mesh2_node_x:standard_name = "longitude" ;
  Mesh2_node_x:long_name = "Longitude of 2D mesh nodes." ;
  Mesh2_node_x:units = "degrees_east" ;

double Mesh2_node_y(nMesh2_node) ;
  Mesh2_node_y:standard_name = "latitude" ;
  Mesh2_node_y:long_name = "Latitude of 2D mesh nodes." ;
  Mesh2_node_y:units = "degrees_north" ;
```

### 面座標 (Face Coordinates) — 可選

通常定義在三角形外接圓圓心或幾何中心：

```cdl
double Mesh2_face_x(nMesh2_face) ;
  Mesh2_face_x:standard_name = "longitude" ;
  Mesh2_face_x:long_name = "Characteristic longitude of 2D mesh face (e.g. circumcenter)." ;
  Mesh2_face_x:units = "degrees_east" ;
  Mesh2_face_x:bounds = "Mesh2_face_xbnds" ;

double Mesh2_face_y(nMesh2_face) ;
  Mesh2_face_y:standard_name = "latitude" ;
  Mesh2_face_y:long_name = "Characteristic latitude of 2D mesh face (e.g. circumcenter)." ;
  Mesh2_face_y:units = "degrees_north" ;
  Mesh2_face_y:bounds = "Mesh2_face_ybnds" ;
```

### 面座標邊界 (Face Coordinate Bounds) — 可選

定義三角形三個頂點的座標，供 CF 規範中的 `bounds` 使用：

```cdl
double Mesh2_face_xbnds(nMesh2_face, Three) ;
  Mesh2_face_xbnds:long_name = "Longitude bounds of triangular face (corner nodes)." ;
  Mesh2_face_xbnds:units = "degrees_east" ;

double Mesh2_face_ybnds(nMesh2_face, Three) ;
  Mesh2_face_ybnds:long_name = "Latitude bounds of triangular face (corner nodes)." ;
  Mesh2_face_ybnds:units = "degrees_north" ;
```

## 📄 完整 CDL 示例

以下是一個包含 4 個節點、2 個三角形面的最小 2D 網格示例：

```cdl
// 全域屬性
:Conventions = "CF-1.12" ;
:title = "Example 2D Triangular Mesh" ;
:institution = "Example Institute" ;

// 維度
dimensions:
  nMesh2_node = 4 ;    // 4 個節點
  nMesh2_edge = 5 ;    // 5 條邊
  nMesh2_face = 2 ;    // 2 個三角形面
  Two  = 2 ;
  Three = 3 ;

variables:

  // 網格拓撲變數
  integer Mesh2 ;
    Mesh2:cf_role = "mesh_topology" ;
    Mesh2:long_name = "Topology data of 2D triangular mesh" ;
    Mesh2:topology_dimension = 2 ;
    Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
    Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
    Mesh2:face_edge_connectivity = "Mesh2_face_edges" ;    // 可選
    Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;    // 可選
    Mesh2:edge_face_connectivity = "Mesh2_edge_faces" ;    // 可選
    Mesh2:face_coordinates = "Mesh2_face_x Mesh2_face_y" ; // 可選

  // 面-節點連線性 (必需)
  integer Mesh2_face_nodes(nMesh2_face, Three) ;
    Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
    Mesh2_face_nodes:long_name = "Maps every triangular face to its three corner nodes." ;
    Mesh2_face_nodes:start_index = 0 ;

  // 邊-節點連線性 (可選)
  integer Mesh2_edge_nodes(nMesh2_edge, Two) ;
    Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
    Mesh2_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;
    Mesh2_edge_nodes:start_index = 0 ;

  // 面-邊連線性 (可選)
  integer Mesh2_face_edges(nMesh2_face, Three) ;
    Mesh2_face_edges:cf_role = "face_edge_connectivity" ;
    Mesh2_face_edges:long_name = "Maps every face to its three edges." ;
    Mesh2_face_edges:start_index = 0 ;

  // 邊-面連線性 (可選)
  integer Mesh2_edge_faces(nMesh2_edge, Two) ;
    Mesh2_edge_faces:cf_role = "edge_face_connectivity" ;
    Mesh2_edge_faces:long_name = "Maps every edge to the faces it bounds." ;
    Mesh2_edge_faces:start_index = 0 ;
    Mesh2_edge_faces:_FillValue = -999 ;

  // 節點座標
  double Mesh2_node_x(nMesh2_node) ;
    Mesh2_node_x:standard_name = "longitude" ;
    Mesh2_node_x:units = "degrees_east" ;

  double Mesh2_node_y(nMesh2_node) ;
    Mesh2_node_y:standard_name = "latitude" ;
    Mesh2_node_y:units = "degrees_north" ;

  // 面特徵座標 (可選)
  double Mesh2_face_x(nMesh2_face) ;
    Mesh2_face_x:standard_name = "longitude" ;
    Mesh2_face_x:long_name = "Longitude of face circumcenter." ;
    Mesh2_face_x:units = "degrees_east" ;

  double Mesh2_face_y(nMesh2_face) ;
    Mesh2_face_y:standard_name = "latitude" ;
    Mesh2_face_y:long_name = "Latitude of face circumcenter." ;
    Mesh2_face_y:units = "degrees_north" ;

data:

  Mesh2 = 0 ;

  // 面-節點連線 (0-based 索引)
  //   Face 0: Node 0, 1, 2
  //   Face 1: Node 1, 3, 2
  Mesh2_face_nodes =
    0, 1, 2,
    1, 3, 2 ;

  // 邊-節點連線 (0-based 索引)
  Mesh2_edge_nodes =
    0, 1,   // Edge 0
    1, 2,   // Edge 1
    0, 2,   // Edge 2
    1, 3,   // Edge 3
    2, 3 ;  // Edge 4

  // 面-邊連線
  Mesh2_face_edges =
    0, 1, 2,   // Face 0: Edge 0, 1, 2
    3, 4, 1 ;  // Face 1: Edge 3, 4, 1

  // 邊-面連線 (-999 = 無相鄰面，即邊界邊)
  Mesh2_edge_faces =
    0, -999,  // Edge 0: 僅 Face 0
    0, 1,     // Edge 1: Face 0 和 Face 1 (共享邊)
    0, -999,  // Edge 2: 僅 Face 0
    1, -999,  // Edge 3: 僅 Face 1
    1, -999 ; // Edge 4: 僅 Face 1

  // 節點座標
  Mesh2_node_x = 10.0, 10.5, 10.25, 11.0 ;
  Mesh2_node_y = 40.0, 40.0, 40.5,  40.0 ;

  // 面特徵座標 (幾何中心)
  Mesh2_face_x = 10.25, 10.583 ;
  Mesh2_face_y = 40.167, 40.167 ;
```

## 🎯 資料變數示例

### 定義在面上的資料 (最常見)

```cdl
double Mesh2_waterlevel(time, nMesh2_face) ;
  Mesh2_waterlevel:standard_name = "sea_surface_height_above_geoid" ;
  Mesh2_waterlevel:units = "m" ;
  Mesh2_waterlevel:mesh = "Mesh2" ;
  Mesh2_waterlevel:location = "face" ;
  Mesh2_waterlevel:coordinates = "Mesh2_face_x Mesh2_face_y" ;
  Mesh2_waterlevel:long_name = "Water level at triangle face centers" ;
```

### 定義在邊上的通量資料

```cdl
double Mesh2_edge_flux(time, nMesh2_edge) ;
  Mesh2_edge_flux:standard_name = "water_volume_flux_per_unit_area" ;
  Mesh2_edge_flux:units = "m s-1" ;
  Mesh2_edge_flux:mesh = "Mesh2" ;
  Mesh2_edge_flux:location = "edge" ;
  Mesh2_edge_flux:coordinates = "Mesh2_edge_x Mesh2_edge_y" ;
  Mesh2_edge_flux:long_name = "Normal flux through edges" ;
```

### 定義在節點上的資料

```cdl
double Mesh2_node_depth(nMesh2_node) ;
  Mesh2_node_depth:standard_name = "sea_floor_depth_below_geoid" ;
  Mesh2_node_depth:units = "m" ;
  Mesh2_node_depth:mesh = "Mesh2" ;
  Mesh2_node_depth:location = "node" ;
  Mesh2_node_depth:coordinates = "Mesh2_node_x Mesh2_node_y" ;
  Mesh2_node_depth:long_name = "Water depth at nodes" ;
```

## 📊 節點排序約定

UGRID 未強制規定面節點的排序方向，但建議：

- ✅ **逆時針 (Counter-Clockwise, CCW)**: 大多數有限元工具的慣例
- 明確記錄在 `long_name` 或全域屬性中
- 保持整個網格的一致性

```
CCW 排列（推薦）:
  Node 2
   ●
  /↑\
 /  \
●→→→●
Node 0  Node 1
```

## 🎯 最佳實踐

### 1. 連線性

- ✅ 必須提供 `face_node_connectivity`
- ✅ 建議同時提供 `edge_node_connectivity`（方便計算通量）
- ✅ 為 `edge_face_connectivity` 的邊界缺失值設置 `_FillValue`
- ✅ 明確指定 `start_index`（建議使用 0）

### 2. 面座標選擇

| 座標類型 | 適用場景 |
|----------|----------|
| 幾何中心 (Centroid) | 一般用途，資料視覺化 |
| 外接圓圓心 (Circumcenter) | 有限體積 Delaunay 三角化 |
| 質心 (Barycenter) | 有限元分析 |

### 3. 效能考量

- ✅ 若需要頻繁的面鄰居查詢，提供 `face_face_connectivity`
- ✅ 若模型在邊上計算通量，提供 `edge_node_connectivity`
- ❌ 不必要的連線性增加檔案體積，視需求選擇

## 🔗 相關文件

- [核心概念](../core-concepts.md) — UGRID 基礎
- [命名約定](naming-conventions.md) — 變數命名規則
- [1D 網路拓撲](1d-network.md) — 較簡單的拓撲型別
- [2D 靈活網格](2d-flexible.md) — 支援混合面型別
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/#2d-triangular-mesh-topology)

## 📚 參考資源

- [UGRID 2D Triangular Mesh Topology](https://ugrid-conventions.github.io/ugrid-conventions/#2d-triangular-mesh-topology)
- [CF Conventions — Mesh Topology Variables](https://cfconventions.org/cf-conventions/cf-conventions.html#mesh-topology-variables)

---

*下一步*: [2D 靈活網格](2d-flexible.md) | [3D 分層網格](3d-layered.md)
