# 幾何元素命名約定 (Naming Conventions for Geometrical Elements)

## 📖 概述

UGRID Conventions 為網格中的幾何元素定義了標準化的命名約定。這些命名在網格拓撲定義中至關重要，確保了不同系統之間的一致性和互操作性。

## 🎯 官方命名約定

### 幾何元素標準名稱

UGRID 官方採用以下標準名稱來描述不同維度的幾何元素：

| 維度 | 標準名稱 | 定義 | 註解 |
| ------ | ---------- | ------ | ------ |
| 0D | **Node** | A point, a coordinate pair or triplet: the most basic element of the topology. | "node" 似乎比 "vertex" 更常用 |
| 1D | **Edge** | A line or curve bounded by two nodes. | |
| 2D | **Face** | A plane or surface enclosed by a set of edges. | 在 2D 水平應用中也可以考慮 "polygon"，但 "face" 在元素層次中最常見 |
| 3D | **Volume** | A volume enclosed by a set of faces. | 備選詞 "cell" 被考慮過，但 "cell" 經常在社群中用來描述二維結構 |

### 命名歷史

在 UGRID 的早期開發階段，社群對幾何元素的命名進行了廣泛的討論：

1. **Node vs Vertex**
   - "Vertex" (頂點) 在幾何學中是常用術語
   - "Node" (節點) 在有限元和網路分析中更常用
   - **決定**: 採用 "Node" 作為標準名稱

2. **Face vs Polygon vs Cell**
   - "Polygon" 在 2D 幾何中很直觀
   - "Cell" 在 CF 社群中常用於描述網格單元
   - "Face" 在拓撲層次中更一致
   - **決定**: 採用 "Face" 作為標準名稱

3. **Volume vs Cell (3D)**
   - "Cell" 可以用於描述 3D 單元
   - "Volume" 更準確地描述了 3D 幾何實體
   - **決定**: 採用 "Volume" 作為標準名稱

⚠️ **重要說明**:
> In favor of simpler code for interpreting compliant files, we have dropped to use of the `locations` attribute which allowed the user to specify his/her own names for nodes, edges, faces and volumes.

這意味著 **不再允許使用者自定義幾何元素的名稱**，必須使用上述標準名稱。

## 🔧 實際應用中的命名

### 1. 網格拓撲變數命名

雖然幾何元素有標準名稱，但 **網格拓撲變數本身** 可以有不同的命名方式：

#### 推薦的命名模式

```cdl
// 方式 1: 使用 Mesh + 維度 + 編號
integer Mesh1 ;  // 1D 網格
integer Mesh2 ;  // 2D 網格
integer Mesh3D ; // 3D 網格

// 方式 2: 使用描述性名稱
integer river_network ;  // 河流網路
integer ocean_mesh ;      // 海洋網格
integer atmospheric_mesh ; // 大氣網格
```

✅ **最佳實踐**: 使用一致的、描述性的名稱，幷包含網格的維度資訊。

### 2. 座標變數命名

座標變數通常遵循以下命名模式：

```cdl
// 標準模式: <MeshPrefix>_<Element>_<Coord>
// 1D 網格示例
int Mesh1 ;
  Mesh1:cf_role = "mesh_topology" ;
  Mesh1:node_coordinates = "Mesh1_node_x Mesh1_node_y" ;

double Mesh1_node_x(nMesh1_node) ;
double Mesh1_node_y(nMesh1_node) ;

// 2D 網格示例
int Mesh2 ;
  Mesh2:cf_role = "mesh_topology" ;
  Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y Mesh2_node_z" ;

double Mesh2_node_x(nMesh2_node) ;
double Mesh2_node_y(nMesh2_node) ;
double Mesh2_node_z(nMesh2_node) ;  // 可選的高程座標
```

### 3. 連線性變數命名

連線性變數通常遵循以下命名模式：

```cdl
// 標準模式: <MeshPrefix>_<FromElement>_<ToElement>
// 2D 網格示例
int Mesh2 ;
  Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
  Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;

int Mesh2_face_nodes(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_nodes:cf_role = "face_node_connectivity" ;

int Mesh2_edge_nodes(nMesh2_edge, 2) ;
  Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
```

### 4. 特徵座標變數命名

特徵座標變數（定義在幾何元素上的座標）通常遵循：

```cdl
// 標準模式: <MeshPrefix>_<Element>_<Coord>
// 2D 網格示例
double Mesh2_face_x(nMesh2_face) ;
  Mesh2_face_x:long_name = "Characteristic longitude of mesh face" ;

double Mesh2_face_y(nMesh2_face) ;
  Mesh2_face_y:long_name = "Characteristic latitude of mesh face" ;

double Mesh2_edge_x(nMesh2_edge) ;
double Mesh2_edge_y(nMesh2_edge) ;
```

## 📋 維度命名

UGRID 對維度命名沒有嚴格的要求，但推薦以下約定：

```cdl
// 標準模式: n<MeshPrefix>_<Element>
dimensions:
  nMesh1_node = 100 ;   // 1D 網格的節點數
  nMesh1_edge = 99 ;    // 1D 網格的邊數
  
  nMesh2_node = 500 ;   // 2D 網格的節點數
  nMesh2_edge = 800 ;   // 2D 網格的邊數
  nMesh2_face = 300 ;   // 2D 網格的面數
  nMaxMesh2_face_nodes = 4 ; // 2D 網格每個面的最大節點數
  
  nMesh3D_node = 2000 ;  // 3D 網格的節點數
  nMesh3D_edge = 4000 ;  // 3D 網格的邊數
  nMesh3D_face = 3000 ;  // 3D 網格的面數
  nMesh3D_vol = 1000 ;   // 3D 網格的體積數
```

✅ **最佳實踐**:

- 使用 `n` 字首表示計數
- 包含網格字首和元素型別
- 對於可變長度的連線性，使用 `nMax*` 表示最大值

## 🎯 cf_role 屬性值

UGRID 定義了標準化的 `cf_role` 屬性值，用於標識變數的角色：

### 網格拓撲角色

| cf_role 值 | 描述 | 變數型別 |
|------------|------|----------|
| `mesh_topology` | 網格拓撲變數 | integer |

### 連線性角色

| cf_role 值 | 描述 | 變數型別 |
| ------------ | ------ | ---------- |
| `edge_node_connectivity` | 邊-節點連線性 | integer |
| `face_node_connectivity` | 面-節點連線性 | integer |
| `volume_node_connectivity` | 體積-節點連線性 | integer |
| `face_edge_connectivity` | 面-邊連線性 | integer |
| `face_face_connectivity` | 面-面連線性 | integer |
| `edge_face_connectivity` | 邊-面連線性 | integer |
| `volume_face_connectivity` | 體積-面連線性 | integer |
| `volume_edge_connectivity` | 體積-邊連線性 | integer |
| `boundary_node_connectivity` | 邊界-節點連線性 | integer |
| `volume_shape_type` | 體積形狀型別 | integer |

### 特殊角色

| cf_role 值 | 描述 | 變數型別 |
|------------|------|----------|
| `location_index_set` | 位置索引集 | integer |

## 📊 體積形狀型別 (Volume Shape Types)

對於 3D 網格中的體積元素，UGRID 定義了標準的形狀型別：

### 標準形狀型別

| 標記值 | 形狀名稱 | 節點數 | 描述 | VTK 對應型別 |
| -------- | ---------- | -------- | ------ | ---------------- |
| 0 | tetrahedron | 4 | 四面體 | VTK_TETRA |
| 1 | pyramid | 5 | 金字塔 (方形底) | VTK_PYRAMID |
| 2 | wedge | 6 | 稜柱 (三角形底) | VTK_WEDGE |
| 3 | hexahedron | 8 | 六面體 (扭曲的立方體) | VTK_HEXAHEDRON |

### 形狀型別定義

```cdl
int Mesh3D_vol_types(nMesh3D_vol) ;
  Mesh3D_vol_types:cf_role = "volume_shape_type" ;
  Mesh3D_vol_types:long_name = "Specifies the shape of the individual volumes." ;
  Mesh3D_vol_types:flag_values = 0, 1, 2, 3 ;
  Mesh3D_vol_types:flag_meanings = "tetrahedron pyramid wedge hexahedron" ;
```

## ✅ 命名最佳實踐

### 1. 保持一致性

- ✅ 在同一個 NetCDF 檔案中使用一致的命名字首
- ✅ 所有相關的變數使用相同的網格字首
- ❌ 避免混合使用不同的命名風格

### 2. 使用描述性名稱

- ✅ 使用有意義的變數名 (如 `Mesh2_face_nodes`)
- ✅ 包含元素型別資訊 (node, edge, face, volume)
- ❌ 避免使用模糊的名稱 (如 `var1`, `data`)

### 3. 包含維度資訊

- ✅ 在變數名中包含維度資訊 (2D, 3D)
- ✅ 使用 `nMax*` 表示最大值
- ❌ 避免讓使用者猜測變數的維度

### 4. 遵循標準約定

- ✅ 使用 UGRID 定義的標準幾何元素名稱
- ✅ 使用 UGRID 定義的標準 cf_role 值
- ✅ 使用 UGRID 定義的標準體積形狀型別
- ❌ 避免使用自定義的元素名稱

### 5. 考慮相容性

- ✅ 使用常見的、廣泛接受的命名方式
- ✅ 考慮現有工具的命名約定
- ❌ 避免使用可能引起混淆的名稱

## 🔍 命名示例

### 1D 網路示例

```cdl
dimensions:
  nMesh1_node = 5 ;   // 5 個節點
  nMesh1_edge = 4 ;   // 4 條邊
  Two = 2 ;            // 每條邊連線 2 個節點

variables:
  // 網格拓撲變數
  integer Mesh1 ;
    Mesh1:cf_role = "mesh_topology" ;
    Mesh1:long_name = "Topology data of 1D network" ;
    Mesh1:topology_dimension = 1 ;
    Mesh1:node_coordinates = "Mesh1_node_x Mesh1_node_y" ;
    Mesh1:edge_node_connectivity = "Mesh1_edge_nodes" ;

  // 連線性變數
  integer Mesh1_edge_nodes(nMesh1_edge, Two) ;
    Mesh1_edge_nodes:cf_role = "edge_node_connectivity" ;
    Mesh1_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;

  // 座標變數
  double Mesh1_node_x(nMesh1_node) ;
    Mesh1_node_x:standard_name = "longitude" ;
    Mesh1_node_x:long_name = "Longitude of 1D network nodes." ;
    Mesh1_node_x:units = "degrees_east" ;

  double Mesh1_node_y(nMesh1_node) ;
    Mesh1_node_y:standard_name = "latitude" ;
    Mesh1_node_y:long_name = "Latitude of 1D network nodes." ;
    Mesh1_node_y:units = "degrees_north" ;
```

### 2D 三角形網格示例

```cdl
dimensions:
  nMesh2_node = 4 ;    // 4 個節點
  nMesh2_edge = 5 ;    // 5 條邊
  nMesh2_face = 2 ;    // 2 個面 (三角形)
  Three = 3 ;          // 每個三角形有 3 個節點

variables:
  // 網格拓撲變數
  integer Mesh2 ;
    Mesh2:cf_role = "mesh_topology" ;
    Mesh2:long_name = "Topology data of 2D triangular mesh" ;
    Mesh2:topology_dimension = 2 ;
    Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
    Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
    Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;

  // 連線性變數
  integer Mesh2_face_nodes(nMesh2_face, Three) ;
    Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
    Mesh2_face_nodes:long_name = "Maps every triangular face to its three corner nodes." ;

  integer Mesh2_edge_nodes(nMesh2_edge, 2) ;
    Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
    Mesh2_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;

  // 座標變數
  double Mesh2_node_x(nMesh2_node) ;
    Mesh2_node_x:standard_name = "longitude" ;
    Mesh2_node_x:long_name = "Longitude of 2D mesh nodes." ;

  double Mesh2_node_y(nMesh2_node) ;
    Mesh2_node_y:standard_name = "latitude" ;
    Mesh2_node_y:long_name = "Latitude of 2D mesh nodes." ;
```

## 📚 相關文件

- [核心概念](core-concepts.md) - UGRID 的基礎概念
- [1D 網路拓撲](1d-network.md) - 1D 網格的詳細定義
- [2D 三角形拓撲](2d-triangular.md) - 2D 三角形網格的詳細定義
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/) - 官方命名約定

---

*下一步*: [1D 網路拓撲](1d-network.md) | [2D 三角形拓撲](2d-triangular.md)
