# 3D 完全非結構化網格拓撲 (3D Fully Unstructured Mesh Topology)

## 📖 概述

**3D 完全非結構化網格拓撲** 是 UGRID 中最複雜、維度最高的拓撲型別。與 3D 分層網格不同，這種拓撲在三維空間中完全非結構化，沒有隱含的層結構。

`topology_dimension = 3`，引入了**體積 (Volume)** 這一新的幾何元素。

典型應用場景：

- 地質建模（地層、斷層）
- 地下水流（複雜孔隙介質）
- 有限元結構力學
- 流體動力學模擬（複雜三維幾何）
- 近岸三維海洋模型（完全非結構化垂直）

## 🏗️ 幾何元素層次

```text
3D 非結構化網格包含全部四層幾何元素：

Volume (體積) ← 四面體、六面體、稜柱等
   ↓ 由面圍成
Face (面) ← 三角形、四邊形
   ↓ 由邊圍成
Edge (邊) ← 線段
   ↓ 由節點定義
Node (節點) ← 三維座標點 (x, y, z)
```

### 幾何元素

| 元素 | 維度 | 描述 | 必需性 |
| --- | --- | --- | --- |
| Node | 0D | 三維座標點 | ✅ 必需 |
| Edge | 1D | 連線兩節點的線段 | ❌ 可選 |
| Face | 2D | 由邊圍成的多邊形 | ❌ 可選* |
| Volume | 3D | 由面圍成的三維體 | ✅ 必需 |

> *`face_node_connectivity` 在部分應用中可選，但 `volume_node_connectivity` 必需。

## 📋 必需屬性

| 屬性 | 型別 | 必需性 | 描述 |
| --- | --- | --- | --- |
| `cf_role` | string | ✅ 必需 | `"mesh_topology"` |
| `topology_dimension` | int | ✅ 必需 | 固定為 `3` |
| `node_coordinates` | string | ✅ 必需 | 節點座標（含 z 分量） |
| `volume_node_connectivity` | string | ✅ 必需 | 體積-節點連線性 |
| `volume_shape_type` | string | 條件 | 混合體積時必需 |

### 完整網格拓撲變數

```cdl
integer Mesh3 ;
  Mesh3:cf_role = "mesh_topology" ;
  Mesh3:long_name = "Topology data of 3D unstructured mesh" ;
  Mesh3:topology_dimension = 3 ;
  Mesh3:node_coordinates = "Mesh3_node_x Mesh3_node_y Mesh3_node_z" ;
  Mesh3:volume_node_connectivity = "Mesh3_volume_nodes" ;
  Mesh3:volume_shape_type = "Mesh3_volume_types" ;      // 混合體積時
  Mesh3:face_node_connectivity = "Mesh3_face_nodes" ;   // 可選
  Mesh3:volume_face_connectivity = "Mesh3_volume_faces" ; // 可選
  Mesh3:edge_node_connectivity = "Mesh3_edge_nodes" ;    // 可選
  Mesh3:volume_coordinates = "Mesh3_volume_x Mesh3_volume_y Mesh3_volume_z" ;
```

## 🔧 連線性變數

### 體積-節點連線性 (Volume-Node Connectivity) — 必需

每個體積單元由多個節點定義：

```cdl
integer Mesh3_volume_nodes(nMesh3_volume, nMaxNodesPerVolume) ;
  Mesh3_volume_nodes:cf_role = "volume_node_connectivity" ;
  Mesh3_volume_nodes:long_name = "Maps every volume to its corner nodes." ;
  Mesh3_volume_nodes:start_index = 0 ;
  Mesh3_volume_nodes:_FillValue = -999 ;
```

### 體積形狀型別 (Volume Shape Type) — 混合體積時必需

當網格包含不同形狀的體積時，需要指定每個體積的形狀：

```cdl
integer Mesh3_volume_types(nMesh3_volume) ;
  Mesh3_volume_types:cf_role = "volume_shape_type" ;
  Mesh3_volume_types:long_name = "Specifies the shape of each volume element." ;
  Mesh3_volume_types:flag_values = 0, 1, 2, 3 ;
  Mesh3_volume_types:flag_meanings = "tetrahedron pyramid wedge hexahedron" ;
```

#### 體積形狀型別定義

| 標記值 | 名稱 | 節點數 | 描述 |
| -------- | ---------- | -------- | ------ |
| 0 | `tetrahedron` | 4 | 四面體（最常見） |
| 1 | `pyramid` | 5 | 方形底錐體 |
| 2 | `wedge` | 6 | 三角柱體（稜柱） |
| 3 | `hexahedron` | 8 | 六面體（扭曲立方體） |

```text
四面體 (4 節點)    方形底錐體 (5 節點)   三角柱體 (6 節點)   六面體 (8 節點)

     3                   4                   5───4             7─────6
    /|\                 /|\                  │\ /│            /│    /│
   / | \               / | \                │ 3 │           / │   / │
  /  |  \             / _|_ \              2───│───3       4─────5  │
 0───────1           0──────1              │   │   │       │  3──│──2
                     2─(base)─3            │   0   │       │ /   │ /
                                           0───────1       0─────1
```

### 面-節點連線性 — 可選

```cdl
integer Mesh3_face_nodes(nMesh3_face, nMaxNodesPerFace) ;
  Mesh3_face_nodes:cf_role = "face_node_connectivity" ;
  Mesh3_face_nodes:start_index = 0 ;
  Mesh3_face_nodes:_FillValue = -999 ;
```

### 體積-面連線性 — 可選

```cdl
integer Mesh3_volume_faces(nMesh3_volume, nMaxFacesPerVolume) ;
  Mesh3_volume_faces:cf_role = "volume_face_connectivity" ;
  Mesh3_volume_faces:start_index = 0 ;
  Mesh3_volume_faces:_FillValue = -999 ;
```

### 體積-邊連線性 — 可選

```cdl
integer Mesh3_volume_edges(nMesh3_volume, nMaxEdgesPerVolume) ;
  Mesh3_volume_edges:cf_role = "volume_edge_connectivity" ;
  Mesh3_volume_edges:start_index = 0 ;
  Mesh3_volume_edges:_FillValue = -999 ;
```

### 體積-體積連線性 — 可選

相鄰體積查詢（每個體積相鄰面對面的體積）：

```cdl
integer Mesh3_volume_links(nMesh3_volume, nMaxFacesPerVolume) ;
  Mesh3_volume_links:cf_role = "volume_volume_connectivity" ;
  Mesh3_volume_links:start_index = 0 ;
  Mesh3_volume_links:_FillValue = -999 ;
```

## 📍 座標變數

3D 網格節點具有三個座標分量：

```cdl
double Mesh3_node_x(nMesh3_node) ;
  Mesh3_node_x:standard_name = "longitude" ;
  Mesh3_node_x:long_name = "Longitude of 3D mesh nodes." ;
  Mesh3_node_x:units = "degrees_east" ;

double Mesh3_node_y(nMesh3_node) ;
  Mesh3_node_y:standard_name = "latitude" ;
  Mesh3_node_y:long_name = "Latitude of 3D mesh nodes." ;
  Mesh3_node_y:units = "degrees_north" ;

double Mesh3_node_z(nMesh3_node) ;
  Mesh3_node_z:standard_name = "depth" ;
  Mesh3_node_z:long_name = "Depth of 3D mesh nodes (positive down)." ;
  Mesh3_node_z:units = "m" ;
  Mesh3_node_z:positive = "down" ;
```

體積特徵座標（質心）：

```cdl
double Mesh3_volume_x(nMesh3_volume) ;
  Mesh3_volume_x:standard_name = "longitude" ;
  Mesh3_volume_x:long_name = "Longitude of volume centroid." ;

double Mesh3_volume_y(nMesh3_volume) ;
  Mesh3_volume_y:standard_name = "latitude" ;
  Mesh3_volume_y:long_name = "Latitude of volume centroid." ;

double Mesh3_volume_z(nMesh3_volume) ;
  Mesh3_volume_z:standard_name = "depth" ;
  Mesh3_volume_z:long_name = "Depth of volume centroid." ;
  Mesh3_volume_z:units = "m" ;
```

## 📄 完整 CDL 示例（純四面體網格）

```cdl
:Conventions = "CF-1.12" ;
:title = "Example 3D Fully Unstructured Tetrahedral Mesh" ;

dimensions:
  nMesh3_node   = 10 ;    // 節點數
  nMesh3_face   = 20 ;    // 三角形面數
  nMesh3_volume = 8  ;    // 四面體體積數
  Four  = 4 ;              // 四面體節點數
  Three = 3 ;              // 三角形面節點數
  time  = UNLIMITED ;

variables:

  integer Mesh3 ;
    Mesh3:cf_role = "mesh_topology" ;
    Mesh3:long_name = "Topology data of 3D tetrahedral mesh" ;
    Mesh3:topology_dimension = 3 ;
    Mesh3:node_coordinates = "Mesh3_node_x Mesh3_node_y Mesh3_node_z" ;
    Mesh3:volume_node_connectivity = "Mesh3_volume_nodes" ;
    Mesh3:face_node_connectivity = "Mesh3_face_nodes" ;
    Mesh3:volume_coordinates = "Mesh3_volume_x Mesh3_volume_y Mesh3_volume_z" ;

  integer Mesh3_volume_nodes(nMesh3_volume, Four) ;
    Mesh3_volume_nodes:cf_role = "volume_node_connectivity" ;
    Mesh3_volume_nodes:long_name = "Maps every tetrahedron to its 4 corner nodes." ;
    Mesh3_volume_nodes:start_index = 0 ;

  integer Mesh3_face_nodes(nMesh3_face, Three) ;
    Mesh3_face_nodes:cf_role = "face_node_connectivity" ;
    Mesh3_face_nodes:long_name = "Maps every triangular face to its 3 corner nodes." ;
    Mesh3_face_nodes:start_index = 0 ;

  double Mesh3_node_x(nMesh3_node) ;
    Mesh3_node_x:standard_name = "longitude" ;
    Mesh3_node_x:units = "degrees_east" ;

  double Mesh3_node_y(nMesh3_node) ;
    Mesh3_node_y:standard_name = "latitude" ;
    Mesh3_node_y:units = "degrees_north" ;

  double Mesh3_node_z(nMesh3_node) ;
    Mesh3_node_z:standard_name = "depth" ;
    Mesh3_node_z:units = "m" ;
    Mesh3_node_z:positive = "down" ;

  double Mesh3_volume_x(nMesh3_volume) ;
    Mesh3_volume_x:standard_name = "longitude" ;
    Mesh3_volume_x:units = "degrees_east" ;

  double Mesh3_volume_y(nMesh3_volume) ;
    Mesh3_volume_y:standard_name = "latitude" ;
    Mesh3_volume_y:units = "degrees_north" ;

  double Mesh3_volume_z(nMesh3_volume) ;
    Mesh3_volume_z:standard_name = "depth" ;
    Mesh3_volume_z:units = "m" ;

  double time(time) ;
    time:standard_name = "time" ;
    time:units = "seconds since 2024-01-01" ;

  // 3D 資料變數
  float Mesh3_pressure(time, nMesh3_volume) ;
    Mesh3_pressure:standard_name = "air_pressure" ;
    Mesh3_pressure:units = "Pa" ;
    Mesh3_pressure:mesh = "Mesh3" ;
    Mesh3_pressure:location = "volume" ;
    Mesh3_pressure:coordinates = "Mesh3_volume_x Mesh3_volume_y Mesh3_volume_z" ;
    Mesh3_pressure:long_name = "Pressure at volume centroids" ;
```

## 🎯 資料變數示例

### 定義在體積上的資料（最常見）

```cdl
float Mesh3_temperature(time, nMesh3_volume) ;
  Mesh3_temperature:standard_name = "air_temperature" ;
  Mesh3_temperature:units = "K" ;
  Mesh3_temperature:mesh = "Mesh3" ;
  Mesh3_temperature:location = "volume" ;
  Mesh3_temperature:coordinates = "Mesh3_volume_x Mesh3_volume_y Mesh3_volume_z" ;
```

### 定義在面上的通量資料

```cdl
float Mesh3_face_flux(time, nMesh3_face) ;
  Mesh3_face_flux:standard_name = "water_volume_flux_per_unit_area" ;
  Mesh3_face_flux:units = "m s-1" ;
  Mesh3_face_flux:mesh = "Mesh3" ;
  Mesh3_face_flux:location = "face" ;
  Mesh3_face_flux:coordinates = "Mesh3_face_x Mesh3_face_y Mesh3_face_z" ;
```

## 📊 各拓撲型別對比

| 特性 | 1D 網路 | 2D 三角形 | 2D 靈活 | 3D 分層 | 3D 非結構化 |
| ------ | --------- | ----------- | --------- | --------- | ------------- |
| `topology_dimension` | 1 | 2 | 2 | 2 | 3 |
| Node | ✅ | ✅ | ✅ | ✅ | ✅ |
| Edge | ✅ | ✅ | ✅ | ✅ | ✅ |
| Face | ❌ | ✅ | ✅ | ✅ | ✅ |
| Volume | ❌ | ❌ | ❌ | ❌ | ✅ |
| 垂直結構 | ❌ | ❌ | ❌ | CF 座標 | UGRID |
| 複雜度 | 低 | 中 | 中 | 高 | 最高 |

## 🎯 最佳實踐

### 1. 體積形狀的一致性

- ✅ 純四面體網格：無需 `volume_shape_type`
- ✅ 混合網格：必須提供 `volume_shape_type`
- ✅ 使用 UGRID 規範的標記值 (0-3)

### 2. 記憶體與效能

- ✅ 3D 非結構化網格檔案通常較大，建議使用 NetCDF-4/HDF5 格式
- ✅ 使用合適的分塊策略（chunking）提升 I/O 效能
- ✅ 考慮按體積分組壓縮（deflate）

### 3. 三維座標的處理

- ✅ 明確定義 `positive = "up"` 或 `positive = "down"`
- ✅ z 座標使用 CF 標準名稱（如 `depth`、`height`）
- ✅ 對笛卡爾座標系使用 `projection_x_coordinate` / `projection_y_coordinate`

### 4. 連線性完整性

- ✅ 確保 `volume_node_connectivity` 的節點索引均在有效範圍內
- ✅ 面的順序與體積的方向性一致（右手定則）
- ✅ 提供 `volume_face_connectivity` 以加速鄰居查詢

## 🔗 相關文件

- [3D 分層網格](3d-layered.md) — 更常用的分層 3D 方法
- [2D 靈活網格](2d-flexible.md) — 2D 非結構化基礎
- [核心概念](../core-concepts.md) — 體積形狀型別定義
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/#3d-unstructured-mesh-topology)

## 📚 參考資源

- [UGRID 3D Unstructured Mesh](https://ugrid-conventions.github.io/ugrid-conventions/#3d-unstructured-mesh-topology)
- [VTK Cell Types Documentation](https://vtk.org/wp-content/uploads/2015/04/file-formats.pdf) — 常見三維體積元素定義

---

*下一步*: [資料位置定義](../data-location.md) | [體積與通量變數](../volume-flux-variables.md)
