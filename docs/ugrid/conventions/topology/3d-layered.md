# 3D 分層網格拓撲 (3D Layered Mesh Topology)

## 📖 概述

**3D 分層網格拓撲** 是應對三維大氣和海洋模型的主流方法。其核心思想是：在水平方向使用 2D 非結構化網格（三角形或靈活網格），在垂直方向使用**分層 (Layered)** 的垂直座標系統。

水平和垂直的分開描述，讓 UGRID 保持 `topology_dimension = 2`，垂直結構則通過 CF 的垂直座標約定來表達。

典型應用場景：

- 海洋循環模型（SCHISM-v5、ROMS、NEMO）
- 大氣動力模型（WRF + 非結構化網格）
- 地下水流模型
- 近岸浪潮與海嘯模擬（含垂直分層）

## 🏗️ 概念架構

```text
垂直（Level/Layer）方向
↑
│  ═══════════════════  Layer k+1 (上界面)
│   ─────────────────  Layer k   (體積/儲存格)
│  ═══════════════════  Layer k   (下界面)
│   ─────────────────  Layer k-1
│  ═══════════════════  ...
│   ...
│  ═══════════════════  底部
└─────────────────────────────────────────→ 水平（2D 非結構化網格）

每一層水平切面 → 使用 2D UGRID 網格拓撲
垂直分層        → 使用 CF 垂直座標變數（sigma、z、pressure 等）
```

## 📋 核心設計原則

UGRID 對 3D 分層網格的設計哲學：

1. **水平拓撲** 用 UGRID 2D 網格描述（`topology_dimension = 2`）
2. **垂直結構** 用 CF 垂直座標變數描述
3. **資料變數** 的維度為 `(time, nLayers, nMesh2_face)` 或類似格式
4. **網格拓撲不改變** —— 每一層的水平結構相同

## 📋 必需屬性

網格拓撲變數（`topology_dimension = 2`，與 2D 網格相同）：

| 屬性 | 型別 | 必需性 | 描述 |
| ------ | ------ | -------- | ------ |
| `cf_role` | string | ✅ 必需 | `"mesh_topology"` |
| `topology_dimension` | int | ✅ 必需 | `2`（水平維度） |
| `node_coordinates` | string | ✅ 必需 | 水平節點座標 |
| `face_node_connectivity` | string | ✅ 必需 | 面-節點連線性 |

## 🔧 完整變數結構

### 一、水平 2D 網格拓撲（UGRID 部分）

```cdl
integer Mesh2 ;
  Mesh2:cf_role = "mesh_topology" ;
  Mesh2:long_name = "Topology data of 2D horizontal mesh (used in layered 3D model)" ;
  Mesh2:topology_dimension = 2 ;
  Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
  Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
  Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;
  Mesh2:face_coordinates = "Mesh2_face_x Mesh2_face_y" ;
```

### 二、垂直座標（CF 約定部分）

UGRID 分層模型通常使用以下幾種垂直座標：

#### (A) Sigma 座標（地形追蹤）

```cdl
float sigma(nSigma) ;
  sigma:standard_name = "ocean_sigma_coordinate" ;
  sigma:long_name = "sigma at layer midpoints" ;
  sigma:positive = "up" ;
  sigma:formula_terms = "sigma: sigma eta: eta depth: depth" ;
  sigma:axis = "Z" ;

// sigma 界面座標
float sigma_bnds(nSigma, Two) ;
  sigma_bnds:long_name = "sigma at layer interfaces" ;
```

#### (B) 海洋通用垂直座標（S-coordinate）

```cdl
float s(nSigma) ;
  s:standard_name = "ocean_s_coordinate_g2" ;
  s:formula_terms = "s: s C: C eta: eta depth: depth depth_c: depth_c" ;
  s:axis = "Z" ;
```

#### (C) 深度（z）座標

```cdl
float depth_layers(nLayer) ;
  depth_layers:standard_name = "depth" ;
  depth_layers:long_name = "depth at layer midpoints" ;
  depth_layers:units = "m" ;
  depth_layers:positive = "down" ;
  depth_layers:axis = "Z" ;
```

### 三、水位（Eta）和深度場

Sigma 座標需要水面和底部深度：

```cdl
double Mesh2_eta(time, nMesh2_face) ;
  Mesh2_eta:standard_name = "sea_surface_height_above_geoid" ;
  Mesh2_eta:units = "m" ;
  Mesh2_eta:mesh = "Mesh2" ;
  Mesh2_eta:location = "face" ;
  Mesh2_eta:coordinates = "Mesh2_face_x Mesh2_face_y" ;

double Mesh2_depth(nMesh2_face) ;
  Mesh2_depth:standard_name = "sea_floor_depth_below_geoid" ;
  Mesh2_depth:units = "m" ;
  Mesh2_depth:mesh = "Mesh2" ;
  Mesh2_depth:location = "face" ;
  Mesh2_depth:coordinates = "Mesh2_face_x Mesh2_face_y" ;
```

## 📄 完整 CDL 示例

```cdl
:Conventions = "CF-1.12" ;
:title = "Example 3D Layered Mesh — Sigma Coordinate" ;
:institution = "Example Institute" ;

dimensions:
  nMesh2_node = 100 ;     // 水平節點數
  nMesh2_edge = 270 ;     // 水平邊數
  nMesh2_face = 180 ;     // 水平面（儲存格）數
  nSigma      = 10 ;      // 垂直 sigma 層數
  time        = UNLIMITED ;
  Two   = 2 ;
  Three = 3 ;

variables:

  // ─── 水平網格拓撲 (UGRID) ───────────────────────────
  integer Mesh2 ;
    Mesh2:cf_role = "mesh_topology" ;
    Mesh2:long_name = "Horizontal 2D topology for layered ocean model" ;
    Mesh2:topology_dimension = 2 ;
    Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
    Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
    Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;
    Mesh2:face_coordinates = "Mesh2_face_x Mesh2_face_y" ;

  integer Mesh2_face_nodes(nMesh2_face, Three) ;
    Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
    Mesh2_face_nodes:long_name = "Maps every triangular face to its three corner nodes." ;
    Mesh2_face_nodes:start_index = 0 ;

  integer Mesh2_edge_nodes(nMesh2_edge, Two) ;
    Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
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

  // ─── 垂直座標 (CF) ──────────────────────────────────
  float sigma(nSigma) ;
    sigma:standard_name = "ocean_sigma_coordinate" ;
    sigma:long_name = "sigma at layer midpoints" ;
    sigma:positive = "up" ;
    sigma:formula_terms = "sigma: sigma eta: Mesh2_eta depth: Mesh2_depth" ;
    sigma:axis = "Z" ;

  // ─── 時間 ──────────────────────────────────────────
  double time(time) ;
    time:standard_name = "time" ;
    time:units = "seconds since 2024-01-01 00:00:00" ;
    time:axis = "T" ;

  // ─── 水位與深度 ──────────────────────────────────────
  double Mesh2_eta(time, nMesh2_face) ;
    Mesh2_eta:standard_name = "sea_surface_height_above_geoid" ;
    Mesh2_eta:units = "m" ;
    Mesh2_eta:mesh = "Mesh2" ;
    Mesh2_eta:location = "face" ;
    Mesh2_eta:coordinates = "Mesh2_face_x Mesh2_face_y" ;

  double Mesh2_depth(nMesh2_face) ;
    Mesh2_depth:standard_name = "sea_floor_depth_below_geoid" ;
    Mesh2_depth:units = "m" ;
    Mesh2_depth:mesh = "Mesh2" ;
    Mesh2_depth:location = "face" ;
    Mesh2_depth:coordinates = "Mesh2_face_x Mesh2_face_y" ;

  // ─── 3D 資料變數 ─────────────────────────────────────
  float Mesh2_salinity(time, nSigma, nMesh2_face) ;
    Mesh2_salinity:standard_name = "sea_water_salinity" ;
    Mesh2_salinity:units = "1e-3" ;
    Mesh2_salinity:mesh = "Mesh2" ;
    Mesh2_salinity:location = "face" ;
    Mesh2_salinity:coordinates = "sigma Mesh2_face_x Mesh2_face_y" ;
    Mesh2_salinity:long_name = "Salinity at layer centers" ;

  float Mesh2_temperature(time, nSigma, nMesh2_face) ;
    Mesh2_temperature:standard_name = "sea_water_temperature" ;
    Mesh2_temperature:units = "degree_Celsius" ;
    Mesh2_temperature:mesh = "Mesh2" ;
    Mesh2_temperature:location = "face" ;
    Mesh2_temperature:coordinates = "sigma Mesh2_face_x Mesh2_face_y" ;
    Mesh2_temperature:long_name = "Water temperature at layer centers" ;
```

## 🎯 資料維度說明

### 不同位置的資料維度

| 資料位置 | 典型維度 | 說明 |
|----------|----------|------|
| 2D 面資料 | `(time, nMesh2_face)` | 水面資料，如水位 |
| 3D 面資料 | `(time, nSigma, nMesh2_face)` | 體積資料，如溫度、鹽度 |
| 3D 邊資料 | `(time, nSigma, nMesh2_edge)` | 側向通量 |
| 3D 節點資料 | `(time, nSigmaNodes, nMesh2_node)` | 節點插值資料 |
| 界面資料 | `(time, nSigma+1, nMesh2_face)` | 層界面資料 |

### 索引順序約定

UGRID 建議最慢變化維度在前（C 語言記憶體順序）：

```
(time, nSigma, nMesh2_face)
  ↑       ↑         ↑
慢變化  中間   快變化（連續記憶體）
```

## 📊 垂直座標型別比較

| 垂直座標 | CF standard_name | 優點 | 適用場景 |
|----------|------------------|------|----------|
| Sigma (σ) | `ocean_sigma_coordinate` | 地形追蹤，無障礙 | 近岸、淺水 |
| S-coordinate | `ocean_s_coordinate_g2` | 靈活拉伸 | 深海 + 近岸 |
| Z-level | `depth` | 簡單，物理直觀 | 深海、大洋 |
| Hybrid sigma-pressure | `atmosphere_hybrid_sigma_pressure_coordinate` | 大氣模型 | 大氣動力 |

## 🎯 最佳實踐

### 1. 水平與垂直分離

- ✅ 水平拓撲用 UGRID 2D 網格描述
- ✅ 垂直結構用 CF 標準垂直座標
- ✅ 資料變數的 `coordinates` 同時包含水平和垂直座標
- ❌ 不要試圖在 `topology_dimension` 中加入垂直維度

### 2. Sigma 座標的 `formula_terms`

- ✅ 必須正確設置 `formula_terms`，指向實際資料變數
- ✅ 確保 `eta`（水位）和 `depth`（底深）的 `mesh` 和 `location` 屬性正確
- ✅ 使用 CF 規範認可的 `standard_name`

### 3. 層數命名

- ✅ 使用描述性維度名（如 `nSigma`、`nLayer`、`nLevel`）
- ✅ 為界面層和中心層分別定義維度（如 `nSigma` 和 `nSigma_bnds`）
- ✅ 在全域屬性中記錄層結構的說明

### 4. 效能優化

- ✅ 對 3D 資料使用適當的分塊策略（chunking）
- ✅ 按時間步分塊可提升時序分析效能
- ✅ 按垂直層分塊可提升剖面查詢效能

## 🔗 相關文件

- [2D 三角形拓撲](2d-triangular.md) — 水平網格基礎
- [2D 靈活網格](2d-flexible.md) — 混合面型別
- [3D 完全非結構化](3d-unstructured.md) — 不分層的 3D 網格
- [資料位置定義](../data-location.md) — 如何在網格上定義資料
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/#3d-layered-mesh-topology)

## 📚 參考資源

- [UGRID 3D Layered Mesh Topology](https://ugrid-conventions.github.io/ugrid-conventions/#3d-layered-mesh-topology)
- [CF Conventions — Vertical Coordinate](https://cfconventions.org/cf-conventions/cf-conventions.html#vertical-coordinate)
- [CF Conventions — Ocean Sigma Coordinate](https://cfconventions.org/cf-conventions/cf-conventions.html#_ocean_sigma_coordinate)

---

*下一步*: [3D 完全非結構化網格](3d-unstructured.md) | [資料位置定義](../data-location.md)
