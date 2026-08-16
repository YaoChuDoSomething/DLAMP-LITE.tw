# 資料在非結構化網格上的定義 (Data Location on Unstructured Grids)

## 📖 概述

在 UGRID 中，資料變數可以定義在網格的任意幾何元素上——節點、邊、面或體積。**資料位置 (Data Location)** 規定了如何將資料與特定幾何元素關聯，是 UGRID 中最重要的概念之一。

正確設置資料位置使得工具可以：

- 自動判斷資料的空間分辨率
- 正確執行空間插值
- 在後處理和視覺化時準確定位資料

## 🎯 資料位置型別

UGRID 定義了四種資料位置：

| `location` 值 | 幾何元素 | 維度 | 典型用途 |
|---------------|----------|------|----------|
| `node` | Node（節點）| 0D | 水位節點值、溫度點資料 |
| `edge` | Edge（邊） | 1D | 法向通量、流速分量 |
| `face` | Face（面） | 2D | 平均水位、濃度場 |
| `volume` | Volume（體積）| 3D | 三維壓力場、溫度場 |

## 📋 必需屬性

每個 UGRID 資料變數必須攜帶以下屬性：

### 核心屬性

| 屬性 | 型別 | 必需性 | 描述 |
| ------ | ------ | -------- | ------ |
| `mesh` | string | ✅ 必需 | 關聯的網格拓撲變數名 |
| `location` | string | ✅ 必需 | 資料位置（`node`/`edge`/`face`/`volume`） |
| `coordinates` | string | ✅ 建議 | 空格分隔的座標變數名 |

### 可選屬性

| 屬性 | 型別 | 描述 |
| ------ | ------ | ------ |
| `location_index_set` | string | 指向位置索引集變數（稀疏資料用） |

## 🔧 各位置的完整示例

### 節點資料 (location = "node")

```cdl
double Mesh2_node_salinity(time, nMesh2_node) ;
  Mesh2_node_salinity:standard_name = "sea_water_salinity" ;
  Mesh2_node_salinity:units = "1e-3" ;
  Mesh2_node_salinity:mesh = "Mesh2" ;           // 關聯到 Mesh2 拓撲
  Mesh2_node_salinity:location = "node" ;         // 資料在節點上
  Mesh2_node_salinity:coordinates = "Mesh2_node_x Mesh2_node_y" ;
  Mesh2_node_salinity:long_name = "Salinity at mesh nodes" ;
```

**維度說明**：
- 非時序資料：`(nMesh2_node)`
- 時序資料：`(time, nMesh2_node)`
- 3D 分層資料：`(time, nLayer, nMesh2_node)`

### 邊資料 (location = "edge")

邊資料最常用於儲存**法向通量**（垂直於邊的流量）：

```cdl
double Mesh2_edge_normal_flux(time, nMesh2_edge) ;
  Mesh2_edge_normal_flux:standard_name = "water_volume_flux_per_unit_area" ;
  Mesh2_edge_normal_flux:units = "m s-1" ;
  Mesh2_edge_normal_flux:mesh = "Mesh2" ;
  Mesh2_edge_normal_flux:location = "edge" ;
  Mesh2_edge_normal_flux:coordinates = "Mesh2_edge_x Mesh2_edge_y" ;
  Mesh2_edge_normal_flux:long_name = "Normal flux through mesh edges" ;
```

> 💡 **邊方向約定**：邊的正方向由 `edge_node_connectivity` 中的節點排序決定（從第一個節點指向第二個節點）。正通量表示從「左邊面」流向「右邊面」。

### 面資料 (location = "face")

面資料是 2D 海洋和水文模型中最常用的資料位置：

```cdl
double Mesh2_waterlevel(time, nMesh2_face) ;
  Mesh2_waterlevel:standard_name = "sea_surface_height_above_geoid" ;
  Mesh2_waterlevel:units = "m" ;
  Mesh2_waterlevel:mesh = "Mesh2" ;
  Mesh2_waterlevel:location = "face" ;
  Mesh2_waterlevel:coordinates = "Mesh2_face_x Mesh2_face_y" ;
  Mesh2_waterlevel:long_name = "Water level at face centers" ;
  Mesh2_waterlevel:_FillValue = -9999.0 ;

double Mesh2_velocity_x(time, nMesh2_face) ;
  Mesh2_velocity_x:standard_name = "eastward_sea_water_velocity" ;
  Mesh2_velocity_x:units = "m s-1" ;
  Mesh2_velocity_x:mesh = "Mesh2" ;
  Mesh2_velocity_x:location = "face" ;
  Mesh2_velocity_x:coordinates = "Mesh2_face_x Mesh2_face_y" ;

double Mesh2_velocity_y(time, nMesh2_face) ;
  Mesh2_velocity_y:standard_name = "northward_sea_water_velocity" ;
  Mesh2_velocity_y:units = "m s-1" ;
  Mesh2_velocity_y:mesh = "Mesh2" ;
  Mesh2_velocity_y:location = "face" ;
  Mesh2_velocity_y:coordinates = "Mesh2_face_x Mesh2_face_y" ;
```

### 體積資料 (location = "volume")

體積資料用於 3D 完全非結構化網格：

```cdl
float Mesh3_temperature(time, nMesh3_volume) ;
  Mesh3_temperature:standard_name = "sea_water_temperature" ;
  Mesh3_temperature:units = "degree_Celsius" ;
  Mesh3_temperature:mesh = "Mesh3" ;
  Mesh3_temperature:location = "volume" ;
  Mesh3_temperature:coordinates = "Mesh3_volume_x Mesh3_volume_y Mesh3_volume_z" ;
  Mesh3_temperature:long_name = "Temperature at volume centroids" ;
```

## 📊 座標指定規則

`coordinates` 屬性應指向**與資料位置對應的座標變數**：

| 資料位置 | 推薦座標變數 |
|----------|-------------|
| `node` | `Mesh2_node_x Mesh2_node_y` |
| `edge` | `Mesh2_edge_x Mesh2_edge_y` （邊中點座標）|
| `face` | `Mesh2_face_x Mesh2_face_y` （面特徵座標）|
| `volume` | `Mesh3_volume_x Mesh3_volume_y Mesh3_volume_z` |

若對應的特徵座標變數不存在，可以省略 `coordinates` 屬性，但不建議。

## 🕐 時間維度的處理

時間維度放在**最前面**（最慢變化維度）：

```cdl
// 靜態資料（無時間維度）
double Mesh2_bathymetry(nMesh2_face) ;
  Mesh2_bathymetry:mesh = "Mesh2" ;
  Mesh2_bathymetry:location = "face" ;

// 時序資料
double Mesh2_temperature(time, nMesh2_face) ;
  Mesh2_temperature:mesh = "Mesh2" ;
  Mesh2_temperature:location = "face" ;

// 3D 分層時序資料
double Mesh2_salinity(time, nSigma, nMesh2_face) ;
  Mesh2_salinity:mesh = "Mesh2" ;
  Mesh2_salinity:location = "face" ;
  Mesh2_salinity:coordinates = "sigma Mesh2_face_x Mesh2_face_y" ;
```

## 🔀 多網格共存

一個 NetCDF 檔案可以包含多個 UGRID 網格（例如流體域和固體域）：

```cdl
// 第一個網格：海洋
integer OceanMesh ;
  OceanMesh:cf_role = "mesh_topology" ;
  OceanMesh:topology_dimension = 2 ;
  ...

// 第二個網格：大氣
integer AtmosMesh ;
  AtmosMesh:cf_role = "mesh_topology" ;
  AtmosMesh:topology_dimension = 2 ;
  ...

// 海洋資料
double OceanMesh_sst(time, nOceanMesh_face) ;
  OceanMesh_sst:mesh = "OceanMesh" ;   // 明確指向海洋網格
  OceanMesh_sst:location = "face" ;

// 大氣資料
double AtmosMesh_temperature(time, nAtmosMesh_face) ;
  AtmosMesh_temperature:mesh = "AtmosMesh" ;  // 指向大氣網格
  AtmosMesh_temperature:location = "face" ;
```

## 🎯 稀疏資料與 `location_index_set`

當資料只定義在網格的一個**子集**上時（例如只有部分面有觀測），使用 `location_index_set`：

```cdl
// 觀測站索引集（只有 50 個面有資料，共 1000 個面）
integer obs_face_indices(nObs_face) ;
  obs_face_indices:cf_role = "location_index_set" ;
  obs_face_indices:mesh = "Mesh2" ;
  obs_face_indices:location = "face" ;
  obs_face_indices:long_name = "Indices of faces with observations" ;
  obs_face_indices:start_index = 0 ;

// 稀疏資料：維度是 nObs_face 而不是 nMesh2_face
double obs_temperature(time, nObs_face) ;
  obs_temperature:mesh = "Mesh2" ;
  obs_temperature:location = "face" ;
  obs_temperature:location_index_set = "obs_face_indices" ;
  obs_temperature:long_name = "Observed temperature at select face locations" ;
```

> 詳細說明見 [位置索引集](location-index-set.md)。

## 📊 有限體積法 vs. 有限元法的資料位置選擇

不同數值方法對資料位置有不同偏好：

| 數值方法 | 標量 | 向量（通量） |
|----------|------|-------------|
| 有限體積法 (FVM) | `face`（儲存格中心）| `edge`（法向通量）|
| 連續 Galerkin 有限元 | `node`（節點值）| `edge`（切向分量）|
| 間斷 Galerkin 有限元 | `face`（元素上）| `face`（元素邊界）|

## 🎯 最佳實踐

### 1. 必須提供的屬性

- ✅ 所有 UGRID 資料變數都必須有 `mesh` 和 `location` 屬性
- ✅ 提供 `coordinates` 屬性以指向對應的特徵座標
- ✅ 提供 `standard_name` 和 `units` 以符合 CF 約定

### 2. 缺失值處理

- ✅ 設置合適的 `_FillValue`（避免使用 0，可能是有效資料值）
- ✅ 使用 CF 推薦的缺失值（如 `9.969209968386869e+36`）
- ✅ 在 `valid_range` 或 `valid_min`/`valid_max` 中記錄物理有效範圍

### 3. 命名約定

- ✅ 變數名包含網格字首（如 `Mesh2_` ）和位置（如 `face_`、`node_`）
- ✅ 對於同一物理量在不同位置的資料，使用不同變數名區分

### 4. 多維度資料

- ✅ 時間維度始終是最慢變化維度（最外維）
- ✅ 垂直維度位於時間與水平維度之間
- ✅ 水平位置維度（如 `nMesh2_face`）是最快變化維度（最內維）

## 🔗 相關文件

- [核心概念](core-concepts.md) — 幾何元素和位置定義
- [體積與通量變數](volume-flux-variables.md) — 邊通量的特殊處理
- [位置索引集](location-index-set.md) — 稀疏資料的定義
- [2D 三角形拓撲](topology/2d-triangular.md) — 面資料示例
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/#data-on-meshes)

## 📚 參考資源

- [UGRID Data on Unstructured Grids](https://ugrid-conventions.github.io/ugrid-conventions/#data-on-meshes)
- [CF Conventions — Coordinates of Data Variables](https://cfconventions.org/cf-conventions/cf-conventions.html#coordinates-for-data-variables)

---

*下一步*: [體積與通量變數](volume-flux-variables.md) | [位置索引集](location-index-set.md)
