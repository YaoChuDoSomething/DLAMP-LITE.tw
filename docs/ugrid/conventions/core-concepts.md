# UGRID 核心概念與術語定義

## 📖 概述

UGRID Conventions 建立在一組清晰定義的概念之上。理解這些核心概念是正確使用和實現 UGRID 的基礎。本文件詳細說明了 UGRID 中的所有關鍵術語和概念。

## 🏗️ 基礎概念

### 1. 幾何元素層次 (Geometric Elements Hierarchy)

UGRID 定義了一個四層的幾何元素層次結構，用於描述網格的拓撲：

```text
┌─────────────────────────────────────┐
│           3D - Volume (體積)            │
│   由多個面圍成的三維空間區域           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           2D - Face (面)                │
│   由多個邊圍成的二維平面區域           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           1D - Edge (邊)                │
│   由兩個節點定義的線段                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           0D - Node (節點/頂點)         │
│   基本幾何元素，表示一個座標點           │
└──────────────────────────────────────┘
```

### 2. 正式定義

| 維度 | 名稱 | UGRID 定義 | 同義詞 | 描述 |
| --- | --- | --- | --- | --- |
| 0D | **Node** | 基本元素 | Vertex (頂點) | 座標點，網格的最基本組成單元 |
| 1D | **Edge** | 線段 | Link (連結) | 連線兩個節點的直線或曲線 |
| 2D | **Face** | 平面區域 | Polygon (多邊形), Cell (單元) | 由邊圍成的封閉區域 |
| 3D | **Volume** | 體積 | Cell (單元) | 由面圍成的三維空間 |

⚠️ **重要說明**：

- **Vertex** 這個術語在 UGRID 中已經被 **Node** 取代，以保持一致性
- **Cell** 在社群中有時用於描述 2D 元素，但 UGRID 官方使用 **Face** 來避免混淆
- **Volume** 而不是 Cell 用於描述 3D 元素

## 🎯 網格拓撲 (Mesh Topology)

### 1. 定義

**網格拓撲 (Mesh Topology)** 指的是網格中各種幾何元素之間的互連關係。這是 UGRID 的核心概念，描述了網格的結構和連線性。

> "Inspired by Wikipedia's definition of network topology, we define the mesh topology here as the interconnection of various geometrical elements of the mesh."

### 2. 組成部分

網格拓撲由以下部分組成：

1. **幾何元素**: Nodes, Edges, Faces, Volumes
2. **連線性**: 元素之間的連線關係
3. **屬性**: 描述拓撲特性的後設資料

### 3. 表示方式

UGRID 使用 **網格拓撲變數 (Mesh Topology Variable)** 來儲存拓撲資訊：

```cdl
integer Mesh2 ;
  Mesh2:cf_role = "mesh_topology" ;
  Mesh2:long_name = "Topology data of 2D unstructured mesh" ;
  Mesh2:topology_dimension = 2 ;
  Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
  Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
```

## 🔗 連線性 (Connectivity)

### 1. 定義

**連線性 (Connectivity)** 描述了網格中不同幾何元素之間的連線關係。UGRID 使用 **連線性變數 (Connectivity Variables)** 來儲存這些關係。

### 2. 連線性變數型別

UGRID 定義了多種連線性變數：

#### 節點連線性 (Node Connectivity)

- `edge_node_connectivity`: 邊到節點的對映
- `face_node_connectivity`: 面到節點的對映
- `volume_node_connectivity`: 體積到節點的對映

#### 邊連線性 (Edge Connectivity)

- `face_edge_connectivity`: 面到邊的對映
- `volume_edge_connectivity`: 體積到邊的對映

#### 面連線性 (Face Connectivity)

- `volume_face_connectivity`: 體積到面的對映

#### 相鄰連線性 (Adjacency Connectivity)

- `face_face_connectivity`: 面到相鄰面的對映
- `edge_face_connectivity`: 邊到相鄰面的對映
- `volume_volume_connectivity`: 體積到相鄰體積的對映

### 3. 連線性變數的屬性

所有連線性變數都有：

- `cf_role`: 變數的角色 (如 `edge_node_connectivity`)
- `long_name`: 描述性名稱
- `start_index`: 索引起始值 (0 或 1)
- `_FillValue`: 缺失值標記

### 4. 索引約定

UGRID 支援兩種索引方式：

#### 0-based 索引 (預設)

```cdl
int mesh_face_nodes(nMesh_face, nMaxNodesPerFace) ;
  mesh_face_nodes:start_index = 0 ;  // 可以省略，0 是預設值
```

#### 1-based 索引

```cdl
int mesh_face_nodes(nMesh_face, nMaxNodesPerFace) ;
  mesh_face_nodes:start_index = 1 ;
```

✅ **最佳實踐**: 建議使用 0-based 索引，因為這與 CF 的壓縮約定一致。

## 📍 座標系統 (Coordinate Systems)

### 1. 節點座標 (Node Coordinates)

UGRID 使用 **輔助座標變數 (Auxiliary Coordinate Variables)** 來描述節點的空間位置：

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

### 2. 特徵座標 (Characteristic Coordinates)

除了節點座標，UGRID 還支援定義邊、面、體積的特徵座標：

- **邊座標**: 通常定義在邊的中點
- **面座標**: 通常定義在面的幾何中心 (如外接圓圓心)
- **體積座標**: 通常定義在體積的幾何中心

```cdl
double Mesh2_edge_x(nMesh2_edge) ;
  Mesh2_edge_x:standard_name = "longitude" ;
  Mesh2_edge_x:long_name = "Characteristic longitude of 2D mesh edge (e.g. midpoint of the edge)." ;

double Mesh2_face_x(nMesh2_face) ;
  Mesh2_face_x:standard_name = "longitude" ;
  Mesh2_face_x:long_name = "Characteristics longitude of 2D mesh face (e.g. circumcenter coordinate)." ;
```

### 3. 座標邊界 (Coordinate Bounds)

UGRID 支援使用 `bounds` 屬性來定義座標的邊界：

```cdl
double Mesh2_face_x(nMesh2_face) ;
  Mesh2_face_x:bounds = "Mesh2_face_xbnds" ;

double Mesh2_face_xbnds(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_xbnds:long_name = "Longitude bounds of 2D mesh face" ;
```

## 🎯 資料位置 (Data Location)

### 1. 定義

**資料位置 (Data Location)** 描述了資料變數在網格中的定義位置。UGRID 支援在不同幾何元素上定義資料。

### 2. 位置型別

UGRID 定義了以下位置型別：

| 位置型別 | 描述 | 使用場景 |
| ---------- | ------ | ---------- |
| `node` | 資料定義在節點上 | 點資料，節點值 |
| `edge` | 資料定義在邊上 | 通量資料，邊值 |
| `face` | 資料定義在面上 | 單後設資料，面值 |
| `volume` | 資料定義在體積上 | 3D 單後設資料 |

### 3. 位置屬性

資料變數使用以下屬性來指定位置：

- `mesh`: 指向關聯的網格拓撲變數
- `location`: 指定資料位置型別 (node, edge, face, volume)
- `coordinates`: 指向位置的座標變數

```cdl
double Mesh2_waterlevel(time, nMesh2_face) ;
  Mesh2_waterlevel:standard_name = "sea_surface_height_above_geoid" ;
  Mesh2_waterlevel:units = "m" ;
  Mesh2_waterlevel:mesh = "Mesh2" ;      // 關聯到網格拓撲
  Mesh2_waterlevel:location = "face" ;   // 資料定義在面上
  Mesh2_waterlevel:coordinates = "Mesh2_face_x Mesh2_face_y" ;
```

## 📊 網格型別 (Mesh Types)

UGRID 支援多種網格型別：

### 1. 1D 網路 (1D Network)

- **拓撲維度**: 1
- **幾何元素**: Nodes, Edges
- **應用場景**: 河流、管道、一維網路
- **示例**: [1D Network Topology](../topology/1d-network.md)

### 2. 2D 三角形網格 (2D Triangular Mesh)

- **拓撲維度**: 2
- **幾何元素**: Nodes, Edges, Faces (三角形)
- **應用場景**: 海洋模型、水文模型
- **示例**: [2D Triangular Topology](../topology/2d-triangular.md)

### 3. 2D 靈活網格 (2D Flexible Mesh)

- **拓撲維度**: 2
- **幾何元素**: Nodes, Edges, Faces (混合形狀)
- **特點**: 支援三角形、四邊形等混合面型別
- **示例**: [2D Flexible Mesh Topology](../topology/2d-flexible.md)

### 4. 3D 分層網格 (3D Layered Mesh)

- **拓撲維度**: 2 (水平) + 垂直座標
- **幾何元素**: Nodes, Edges, Faces (2D) + Layers
- **特點**: 2D 水平網格 + 垂直方向分層
- **示例**: [3D Layered Topology](../topology/3d-layered.md)

### 5. 3D 完全非結構化網格 (3D Fully Unstructured Mesh)

- **拓撲維度**: 3
- **幾何元素**: Nodes, Edges, Faces, Volumes
- **特點**: 完全三維的非結構化網格
- **示例**: [3D Unstructured Topology](../topology/3d-unstructured.md)

## 🔧 體積與通量變數 (Volume and Flux Variables)

UGRID 認識到相同的網格幾何可以用於不同的數值方案：

### 1. 有限體積法 (Finite Volume)

- **體積**: 定義在面 (2D) 或體積 (3D) 上
- **通量**: 定義在邊上，表示**跨越**邊的通量
- **特點**: 體積圍繞面，通量跨越邊

### 2. 連續 Galerkin 有限元法

- **體積**: 定義在節點上
- **通量**: 定義在邊上，表示**沿著**邊的通量
- **特點**: 體積圍繞節點，通量沿著邊

## 📋 屬性定義 (Attribute Definitions)

### 1. 標準化屬性 (Standardized Attributes)

UGRID 定義了以下標準化屬性：

#### 網格拓撲屬性

| 屬性 | 型別 | 必需性 | 描述 |
| ------ | ------ | -------- | ------ |
| `cf_role` | string | 必需 | 變數的角色，如 `mesh_topology` |
| `topology_dimension` | int | 必需 | 網格的最高維度 (1, 2, 3) |
| `node_coordinates` | string | 必需 | 空格分隔的節點座標變數名列表 |
| `edge_node_connectivity` | string | 可選 | 邊-節點連線性變數名 |
| `face_node_connectivity` | string | 條件必需 | 面-節點連線性變數名 |
| `volume_node_connectivity` | string | 條件必需 | 體積-節點連線性變數名 |
| `edge_dimension` | string | 可選 | 邊的維度名 |
| `face_dimension` | string | 可選 | 面的維度名 |
| `volume_dimension` | string | 可選 | 體積的維度名 |

#### 連線性屬性

| 屬性 | 型別 | 必需性 | 描述 |
| ------ | ------ | -------- | ------ |
| `cf_role` | string | 必需 | 連線性變數的角色 |
| `start_index` | int | 可選 | 索引起始值 (0 或 1)，預設 0 |
| `_FillValue` | same as var | 可選 | 缺失值標記 |

#### 資料位置屬性

| 屬性 | 型別 | 必需性 | 描述 |
| ------ | ------ | -------- | ------ |
| `mesh` | string | 必需 | 關聯的網格拓撲變數名 |
| `location` | string | 必需 | 資料位置 (node, edge, face, volume) |
| `coordinates` | string | 可選 | 空格分隔的座標變數名列表 |
| `location_index_set` | string | 可選 | 位置索引集變數名 |

### 2. cf_role 值

UGRID 定義了以下 `cf_role` 值：

#### 網格拓撲角色

- `mesh_topology`: 網格拓撲變數

#### 連線性角色

- `edge_node_connectivity`: 邊-節點連線性
- `face_node_connectivity`: 面-節點連線性
- `volume_node_connectivity`: 體積-節點連線性
- `face_edge_connectivity`: 面-邊連線性
- `face_face_connectivity`: 面-面連線性
- `edge_face_connectivity`: 邊-面連線性
- `volume_face_connectivity`: 體積-面連線性
- `volume_edge_connectivity`: 體積-邊連線性
- `boundary_node_connectivity`: 邊界-節點連線性
- `volume_shape_type`: 體積形狀型別

#### 特殊角色

- `location_index_set`: 位置索引集

### 3. 體積形狀型別 (Volume Shape Types)

UGRID 定義了以下體積形狀型別：

| 標記值 | 形狀名稱 | 節點數 | 描述 |
| -------- | ---------- | -------- | ------ |
| 0 | tetrahedron | 4 | 四面體 |
| 1 | pyramid | 5 | 金字塔 (方形底) |
| 2 | wedge | 6 | 稜柱 (三角形底) |
| 3 | hexahedron | 8 | 六面體 (扭曲的立方體) |

## 🎯 最佳實踐

### 1. 命名約定

- ✅ 使用描述性的變數名 (如 `Mesh2_face_nodes`)
- ✅ 保持一致的字首 (如所有 2D 網格變數以 `Mesh2_` 開頭)
- ❌ 避免使用保留字 (如 `node`, `edge`, `face` 作為變數名)

### 2. 屬性使用

- ✅ 總是定義 `cf_role` 屬性
- ✅ 總是定義 `long_name` 屬性
- ✅ 使用標準名稱 (standard_name) 當適用時
- ✅ 使用 `start_index` 明確索引方式

### 3. 連線性變數

- ✅ 使用 `_FillValue` 處理變長陣列
- ✅ 保持連線性變數與拓撲一致
- ✅ 使用 0-based 索引 (推薦)

### 4. 資料變數

- ✅ 總是定義 `mesh` 和 `location` 屬性
- ✅ 使用 `coordinates` 屬性指向位置座標
- ✅ 確保資料維度與位置一致

---

*下一步*: [命名約定](topology/naming-conventions.md) | [1D 網路拓撲](topology/1d-network.md)
