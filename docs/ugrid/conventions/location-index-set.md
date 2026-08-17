# 位置索引集 (Location Index Set)

## 📖 概述

**位置索引集 (Location Index Set)** 是 UGRID 的一個進階特性，用於表達**稀疏資料**——即資料只定義在網格的一個子集上，而不是全部幾何元素上的情況。

這在以下場景特別有用：

- 觀測站資料（只有部分格點有實測資料）
- 子網格資料（只關注網格的特定區域）
- 邊界條件（只在邊界邊或面上定義）
- 氣象站點資料（稀疏分布的點測量）

## 🏗️ 基本概念

### 問題：稀疏資料的表達困境

假設有一個包含 10,000 個面的海洋網格，但觀測站只在其中 50 個面的中心有資料：

```text
完整網格 (10,000 個面)：
●●●●●●●●●●●●●●●●●●●●
●●●●●●●●●●●●●●●●●●●●
...
●●★●●●●★●●●●●★●●●●★●   ★ = 有觀測資料的面
...

傳統方法（低效）：
  定義 10,000 個面的陣列，其中 9,950 個是缺失值 _FillValue

位置索引集方法（高效）：
  1. 定義 50 個索引，指向有資料的面
  2. 資料陣列只有 50 個元素
```

### 解決方案：`location_index_set`

```cdl
// 步驟 1：定義索引集（哪些面有資料）
integer obs_face_indices(nObs_face) ;
  obs_face_indices:cf_role = "location_index_set" ;
  obs_face_indices:mesh = "Mesh2" ;
  obs_face_indices:location = "face" ;
  obs_face_indices:start_index = 0 ;

// 步驟 2：資料陣列使用索引集的維度
double obs_temperature(time, nObs_face) ;   // 50 個面，不是 10,000 個
  obs_temperature:mesh = "Mesh2" ;
  obs_temperature:location = "face" ;
  obs_temperature:location_index_set = "obs_face_indices" ;  // 指向索引集
```

## 📋 位置索引集變數屬性

位置索引集變數需要以下屬性：

| 屬性 | 型別 | 必需性 | 描述 |
| ------ | ------ | -------- | ------ |
| `cf_role` | string | ✅ 必需 | 固定為 `"location_index_set"` |
| `mesh` | string | ✅ 必需 | 關聯的網格拓撲變數名 |
| `location` | string | ✅ 必需 | 索引對應的位置類型 |
| `start_index` | int | ✅ 建議 | 索引起始值（0 或 1） |
| `long_name` | string | ❌ 可選 | 描述性名稱 |

## 🔧 完整 CDL 示例

### 示例 1：海洋觀測站資料

```cdl
:Conventions = "CF-1.12" ;
:title = "Sparse Ocean Temperature Observations on Unstructured Grid" ;

dimensions:
  nMesh2_node   = 10000 ;    // 全部節點
  nMesh2_face   = 18500 ;    // 全部面
  Three         = 3 ;
  nObs_face     = 50 ;       // 只有 50 個面有觀測資料
  time          = UNLIMITED ;

variables:

  // 網格拓撲（完整網格）
  integer Mesh2 ;
    Mesh2:cf_role = "mesh_topology" ;
    Mesh2:topology_dimension = 2 ;
    Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
    Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
    Mesh2:face_coordinates = "Mesh2_face_x Mesh2_face_y" ;

  // 完整網格連線性和座標...（省略）

  // ── 位置索引集 ──────────────────────────────
  integer obs_face_indices(nObs_face) ;
    obs_face_indices:cf_role = "location_index_set" ;
    obs_face_indices:mesh = "Mesh2" ;
    obs_face_indices:location = "face" ;
    obs_face_indices:start_index = 0 ;
    obs_face_indices:long_name = "Indices of triangular faces containing observation stations" ;

  // ── 稀疏觀測資料 ────────────────────────────
  double obs_temperature(time, nObs_face) ;
    obs_temperature:standard_name = "sea_water_temperature" ;
    obs_temperature:units = "degree_Celsius" ;
    obs_temperature:mesh = "Mesh2" ;
    obs_temperature:location = "face" ;
    obs_temperature:location_index_set = "obs_face_indices" ;
    obs_temperature:coordinates = "Mesh2_face_x Mesh2_face_y" ;
    obs_temperature:long_name = "Observed temperature at monitoring stations" ;
    obs_temperature:_FillValue = -9999.0 ;

  double obs_salinity(time, nObs_face) ;
    obs_salinity:standard_name = "sea_water_salinity" ;
    obs_salinity:units = "1e-3" ;
    obs_salinity:mesh = "Mesh2" ;
    obs_salinity:location = "face" ;
    obs_salinity:location_index_set = "obs_face_indices" ;
    obs_salinity:coordinates = "Mesh2_face_x Mesh2_face_y" ;

  double time(time) ;
    time:standard_name = "time" ;
    time:units = "seconds since 2024-01-01" ;

data:

  // 觀測站位於第 10, 25, 42, 78, 103... 個面（0-based 索引）
  obs_face_indices = 10, 25, 42, 78, 103, ... ;

  // 溫度觀測：50 個站點 × time
  obs_temperature = 
    18.5, 17.2, 19.1, ..., // t=0
    18.7, 17.0, 19.3, ...; // t=1
```

### 示例 2：邊界條件（定義在邊界邊上）

```cdl
dimensions:
  nMesh2_edge       = 5200 ;    // 全部邊
  nBoundary_edge    = 150 ;     // 只有邊界邊（開放邊界）

variables:

  integer boundary_edge_indices(nBoundary_edge) ;
    boundary_edge_indices:cf_role = "location_index_set" ;
    boundary_edge_indices:mesh = "Mesh2" ;
    boundary_edge_indices:location = "edge" ;
    boundary_edge_indices:start_index = 0 ;
    boundary_edge_indices:long_name = "Indices of open boundary edges" ;

  // 潮汐邊界條件（只在邊界邊上）
  double tidal_bc_waterlevel(time, nBoundary_edge) ;
    tidal_bc_waterlevel:standard_name = "sea_surface_height_above_geoid" ;
    tidal_bc_waterlevel:units = "m" ;
    tidal_bc_waterlevel:mesh = "Mesh2" ;
    tidal_bc_waterlevel:location = "edge" ;
    tidal_bc_waterlevel:location_index_set = "boundary_edge_indices" ;
    tidal_bc_waterlevel:long_name = "Prescribed water level at open boundaries" ;
```

### 示例 3：節點上的稀疏資料

```cdl
dimensions:
  nMesh2_node    = 5000 ;
  nStation_node  = 12 ;    // 12 個氣象站節點

variables:

  integer station_node_indices(nStation_node) ;
    station_node_indices:cf_role = "location_index_set" ;
    station_node_indices:mesh = "Mesh2" ;
    station_node_indices:location = "node" ;
    station_node_indices:start_index = 0 ;

  double station_wind_speed(time, nStation_node) ;
    station_wind_speed:standard_name = "wind_speed" ;
    station_wind_speed:units = "m s-1" ;
    station_wind_speed:mesh = "Mesh2" ;
    station_wind_speed:location = "node" ;
    station_wind_speed:location_index_set = "station_node_indices" ;
    station_wind_speed:coordinates = "Mesh2_node_x Mesh2_node_y" ;
```

## 📊 使用索引集 vs. 完整陣列的對比

| 方法 | 陣列大小 | 缺失值比例 | I/O 效率 |
| ------ | ---------- | ------------ | ---------- |
| 完整陣列 (10,000 個面) | 10,000 | 99.5% | 低 |
| 位置索引集 (50 個面) | 50 + 50 (索引) | 0% | 高 |

> 儲存節省：在有 1,000 個時步的情況下，
>
> - 完整陣列：10,000 × 1,000 = 10,000,000 個值
> - 位置索引集：50 + 50 × 1,000 = 50,050 個值
> - **節省約 99.5%** 的儲存空間

## 🎯 最佳實踐

### 1. 索引集的命名

- ✅ 命名應清楚表達其代表的物理意義（如 `obs_face_indices`、`open_boundary_edge_indices`）
- ✅ 在 `long_name` 中描述這些位置的物理含義
- ❌ 避免使用通用名稱（如 `subset_indices`）

### 2. 索引的有效性

- ✅ 確保所有索引值在 `[0, nTotalElements)` 範圍內（0-based）
- ✅ 確保索引不重複
- ✅ 建議索引排序（升序），方便快速查找
- ✅ 明確設置 `start_index`

### 3. 多個索引集

一個網格可以有多個索引集：

```cdl
// 北側開放邊界
integer north_boundary_edges(nNorth_edge) ;
  north_boundary_edges:cf_role = "location_index_set" ;
  north_boundary_edges:mesh = "Mesh2" ;
  north_boundary_edges:location = "edge" ;

// 南側開放邊界
integer south_boundary_edges(nSouth_edge) ;
  south_boundary_edges:cf_role = "location_index_set" ;
  south_boundary_edges:mesh = "Mesh2" ;
  south_boundary_edges:location = "edge" ;
```

### 4. 與座標的配合

使用索引集的資料變數的 `coordinates` 屬性應指向**完整網格**的座標：

```cdl
// ✅ 正確：使用完整網格座標
double sparse_data(time, nObs_face) ;
  sparse_data:location_index_set = "obs_face_indices" ;
  sparse_data:coordinates = "Mesh2_face_x Mesh2_face_y" ;  // 完整面座標

// ❌ 錯誤：不要建立只有 nObs_face 長度的座標
```

工具可以用索引集提取對應的座標值。

## 🔗 相關文件

- [資料位置定義](data-location.md) — 完整網格上的資料定義
- [核心概念](core-concepts.md) — UGRID 基礎屬性
- [符合性要求](../implementation/conformance.md) — 位置索引集的驗證規則
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/#location-index-set)

## 📚 參考資源

- [UGRID Location Index Set](https://ugrid-conventions.github.io/ugrid-conventions/#location-index-set)
- [CF Conventions — Compression by Gathering](https://cfconventions.org/cf-conventions/cf-conventions.html#compression-by-gathering)

---

*下一步*: [符合性要求](../implementation/conformance.md) | [最佳實踐](../implementation/best-practices.md)
