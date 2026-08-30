# 體積與通量變數 (Volume and Flux Variables)

## 📖 概述

UGRID 認識到：**相同的網格幾何可以支援不同的數值離散方案**，而這些方案對「體積 (Volume)」和「通量 (Flux)」的定義各不相同。本文件詳細說明如何在 UGRID 框架中正確表達體積和通量資料。

## 🎯 核心概念

### 什麼是「體積」？

在數值計算中，「體積」指的是**控制體 (Control Volume)**——一個圍繞特定計算點的空間區域，用於積分守恆方程。

根據數值方法的不同，控制體的形狀也不同：

| 數值方法 | 控制體定義 | UGRID 位置 |
| ---------- | ------------ | ------------ |
| 有限體積法 (FVM-cell-centered) | 面（儲存格）本身 | `face` |
| 有限體積法 (FVM-vertex-centered) | 節點周圍的對偶格 | `node` |
| 連續 Galerkin 有限元 (CG-FEM) | 節點周圍的支援域 | `node` |
| 間斷 Galerkin 有限元 (DG-FEM) | 面（元素）本身 | `face` |

### 什麼是「通量」？

**通量 (Flux)** 表示物理量跨越控制體邊界的傳輸速率。在 UGRID 中，通量通常定義在**邊 (Edge)** 上。

- **法向通量** (Normal Flux)：垂直於邊界面的通量
- **切向通量** (Tangential Flux)：沿著邊界面的通量

## 🏗️ 兩種主要數值格式

### 方案 A：有限體積法（以面為儲存格）

```text
典型模型：FVCOM, SCHISM, Delft3D FM

儲存格（控制體）= 三角形/多邊形面
通量 = 跨越邊的法向流量

示意圖：
  ●─────────●
  │    F1   │← 面 F1 是控制體
  │    ↕    │← 箭頭表示法向通量穿過共享邊
  │    F2   │← 面 F2 是相鄰控制體
  ●─────────●
```

CDL 示例：

```cdl
// 面上的守恆量（水體積）
double Mesh2_waterlevel(time, nMesh2_face) ;
  Mesh2_waterlevel:standard_name = "sea_surface_height_above_geoid" ;
  Mesh2_waterlevel:units = "m" ;
  Mesh2_waterlevel:mesh = "Mesh2" ;
  Mesh2_waterlevel:location = "face" ;        // 面儲存格

// 邊上的通量（流量，正值 = 從 face_1 流向 face_2）
double Mesh2_edge_normal_velocity(time, nMesh2_edge) ;
  Mesh2_edge_normal_velocity:standard_name = "sea_water_velocity" ;
  Mesh2_edge_normal_velocity:units = "m s-1" ;
  Mesh2_edge_normal_velocity:mesh = "Mesh2" ;
  Mesh2_edge_normal_velocity:location = "edge" ;     // 邊通量
  Mesh2_edge_normal_velocity:long_name = "Normal velocity component through edges" ;
```

### 方案 B：連續 Galerkin 有限元法（以節點為儲存格）

```
典型模型：ADCIRC (部分實現)

控制體（對偶格）圍繞節點
通量 = 沿著邊的切向分量 或 法向分量

示意圖：
  ●─────●─────●
  │ ╲   │   ╱ │
  │   ╲ │ ╱   │
  ●─────●─────●  ← 中心節點是「控制體中心」
  │   ╱ │ ╲   │
  │ ╱   │   ╲ │
  ●─────●─────●
```

CDL 示例：

```cdl
// 節點上的守恆量
double Mesh2_node_elevation(time, nMesh2_node) ;
  Mesh2_node_elevation:standard_name = "sea_surface_height_above_geoid" ;
  Mesh2_node_elevation:units = "m" ;
  Mesh2_node_elevation:mesh = "Mesh2" ;
  Mesh2_node_elevation:location = "node" ;    // 節點儲存格
```

## 🔧 通量方向約定

### 邊方向定義

邊的正方向由 `edge_node_connectivity` 中的節點排序決定：

```
edge_node_connectivity 定義：
  Edge E: Node A → Node B

  Node A ●──────────────→ Node B
         ↑ 邊的正方向

法向（Normal）方向：
  從邊 E 的左邊面（face_left）朝向右邊面（face_right）
  左/右由邊正方向的右手定則確定
```

### 通量符號約定

```cdl
// 正通量 = 從 face_1 流向 face_2（按 edge_face_connectivity 的第一/第二個面）
double Mesh2_flux(time, nMesh2_edge) ;
  Mesh2_flux:mesh = "Mesh2" ;
  Mesh2_flux:location = "edge" ;
  Mesh2_flux:long_name = "Positive flux is from first face to second face in edge_face_connectivity" ;
```

## 📋 完整示例：有限體積法海洋模型

```cdl
:Conventions = "CF-1.12" ;
:title = "2D Depth-Averaged Ocean Model Output" ;

dimensions:
  nMesh2_node = 1000 ;
  nMesh2_edge = 2800 ;
  nMesh2_face = 1850 ;
  Three = 3 ;
  Two   = 2 ;
  time  = UNLIMITED ;

variables:

  // 網格拓撲
  integer Mesh2 ;
    Mesh2:cf_role = "mesh_topology" ;
    Mesh2:topology_dimension = 2 ;
    Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
    Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
    Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;
    Mesh2:edge_face_connectivity = "Mesh2_edge_faces" ;
    Mesh2:face_coordinates = "Mesh2_face_x Mesh2_face_y" ;
    Mesh2:edge_coordinates = "Mesh2_edge_x Mesh2_edge_y" ;

  // ... (連線性和座標變數省略)

  double time(time) ;
    time:standard_name = "time" ;
    time:units = "seconds since 2024-01-01 00:00:00" ;

  // ─── 面儲存格量（守恆量）─────────────────────
  // 水位
  double Mesh2_s1(time, nMesh2_face) ;
    Mesh2_s1:standard_name = "sea_surface_height_above_geoid" ;
    Mesh2_s1:units = "m" ;
    Mesh2_s1:mesh = "Mesh2" ;
    Mesh2_s1:location = "face" ;
    Mesh2_s1:coordinates = "Mesh2_face_x Mesh2_face_y" ;
    Mesh2_s1:_FillValue = -9999.0 ;

  // 深度平均鹽度
  double Mesh2_salinity(time, nMesh2_face) ;
    Mesh2_salinity:standard_name = "sea_water_salinity" ;
    Mesh2_salinity:units = "1e-3" ;
    Mesh2_salinity:mesh = "Mesh2" ;
    Mesh2_salinity:location = "face" ;
    Mesh2_salinity:coordinates = "Mesh2_face_x Mesh2_face_y" ;

  // 水深（靜態）
  double Mesh2_depth(nMesh2_face) ;
    Mesh2_depth:standard_name = "sea_floor_depth_below_geoid" ;
    Mesh2_depth:units = "m" ;
    Mesh2_depth:mesh = "Mesh2" ;
    Mesh2_depth:location = "face" ;
    Mesh2_depth:coordinates = "Mesh2_face_x Mesh2_face_y" ;

  // ─── 邊通量量────────────────────────────────
  // 法向速度（跨越邊的通量）
  double Mesh2_su2(time, nMesh2_edge) ;
    Mesh2_su2:standard_name = "sea_water_velocity" ;
    Mesh2_su2:units = "m2 s-1" ;  // 深度積分後的體積通量
    Mesh2_su2:mesh = "Mesh2" ;
    Mesh2_su2:location = "edge" ;
    Mesh2_su2:coordinates = "Mesh2_edge_x Mesh2_edge_y" ;
    Mesh2_su2:long_name = "Normal velocity flux across edges (depth-integrated)" ;
```

## 📊 面速度 vs. 邊通量

許多模型同時儲存**面速度向量**和**邊法向通量**：

```cdl
// 後處理用：面上的速度向量分量（由邊通量計算而來）
double Mesh2_ucx(time, nMesh2_face) ;
  Mesh2_ucx:standard_name = "eastward_sea_water_velocity" ;
  Mesh2_ucx:units = "m s-1" ;
  Mesh2_ucx:mesh = "Mesh2" ;
  Mesh2_ucx:location = "face" ;
  Mesh2_ucx:long_name = "Depth-averaged eastward velocity at face centers" ;

double Mesh2_ucy(time, nMesh2_face) ;
  Mesh2_ucy:standard_name = "northward_sea_water_velocity" ;
  Mesh2_ucy:units = "m s-1" ;
  Mesh2_ucy:mesh = "Mesh2" ;
  Mesh2_ucy:location = "face" ;
  Mesh2_ucy:long_name = "Depth-averaged northward velocity at face centers" ;

// 模型核心量：邊法向通量（更精確）
double Mesh2_unorm(time, nMesh2_edge) ;
  Mesh2_unorm:standard_name = "sea_water_velocity" ;
  Mesh2_unorm:units = "m s-1" ;
  Mesh2_unorm:mesh = "Mesh2" ;
  Mesh2_unorm:location = "edge" ;
  Mesh2_unorm:long_name = "Normal velocity component at edge midpoints" ;
```

## 🎯 最佳實踐

### 1. 通量正方向文件

- ✅ 在 `long_name` 或全域屬性中說明通量的正方向定義
- ✅ 說明使用 `edge_face_connectivity` 中的哪個面作為參考
- ❌ 不要假設讀者知道通量符號約定

### 2. 物理量的 `standard_name`

- ✅ 體積流量：`water_volume_transport_into_sea_water_from_rivers`
- ✅ 速度通量：`sea_water_velocity`（法向分量）
- ✅ 面水位：`sea_surface_height_above_geoid`
- ✅ 查閱 CF 標準名稱表確保準確性

### 3. 單位一致性

| 物理量 | 常用單位 |
| -------- | ---------- |
| 法向速度 | `m s-1` |
| 體積通量 | `m3 s-1` |
| 深度積分通量 | `m2 s-1` |
| 水位 | `m` |
| 鹽度 | `1e-3` 或 `g kg-1` |

### 4. 資料位置選擇

- ✅ 有限體積法（儲存格中心）：量放在 `face`，通量放在 `edge`
- ✅ 有限元法（節點中心）：量放在 `node`，通量視方案而定
- ✅ 保持整個檔案的位置選擇一致
- ❌ 不要在未說明的情況下混合 `node` 和 `face` 的同一物理量

## 🔗 相關文件

- [資料位置定義](data-location.md) — 資料位置基礎概念
- [位置索引集](location-index-set.md) — 稀疏資料定義
- [2D 三角形拓撲](topology/2d-triangular.md) — 邊-面連線性
- [符合性要求](../implementation/conformance.md) — 合規檢查清單

## 📚 參考資源

- [UGRID Volume and Flux Variables](https://ugrid-conventions.github.io/ugrid-conventions/#volume-and-flux-variables)
- [CF Conventions — Standard Names](https://cfconventions.org/Data/cf-standard-names/current/build/cf-standard-name-table.html)

---

*下一步*: [位置索引集](location-index-set.md) | [符合性要求](../implementation/conformance.md)
