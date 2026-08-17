# UGRID 後設資料屬性參考 (Metadata Attributes Reference)

## 📖 概述

本文件提供 UGRID 規範中所有**標準後設資料屬性**的完整參考，包括屬性名稱、型別、允許值及使用情境。

## 1. 網格拓撲屬性（Mesh Topology Attributes）

這些屬性定義在 `cf_role = "mesh_topology"` 的變數上：

| 屬性名稱 | 型別 | 必需性 | 允許值 / 格式 | 描述 |
| ---------- | ------ | -------- | --------------- | ------ |
| `cf_role` | string | ✅ 必需 | `"mesh_topology"` | 標識此變數為網格拓撲 |
| `topology_dimension` | int | ✅ 必需 | `1`, `2`, `3` | 網格的最高維度 |
| `node_coordinates` | string | ✅ 必需 | 空格分隔的變數名 | 節點座標變數 |
| `edge_node_connectivity` | string | 視維度 | 單一變數名 | 邊-節點連線性 |
| `face_node_connectivity` | string | 視維度 | 單一變數名 | 面-節點連線性 |
| `volume_node_connectivity` | string | 視維度 | 單一變數名 | 體積-節點連線性 |
| `edge_face_connectivity` | string | ❌ 可選 | 單一變數名 | 邊-面連線性 |
| `face_edge_connectivity` | string | ❌ 可選 | 單一變數名 | 面-邊連線性 |
| `face_face_connectivity` | string | ❌ 可選 | 單一變數名 | 面-面連線性 |
| `volume_face_connectivity` | string | ❌ 可選 | 單一變數名 | 體積-面連線性 |
| `volume_edge_connectivity` | string | ❌ 可選 | 單一變數名 | 體積-邊連線性 |
| `volume_volume_connectivity` | string | ❌ 可選 | 單一變數名 | 體積-體積連線性 |
| `boundary_node_connectivity` | string | ❌ 可選 | 單一變數名 | 邊界-節點連線性 |
| `edge_coordinates` | string | ❌ 可選 | 空格分隔的變數名 | 邊中心座標 |
| `face_coordinates` | string | ❌ 可選 | 空格分隔的變數名 | 面中心座標 |
| `volume_coordinates` | string | ❌ 可選 | 空格分隔的變數名 | 體積中心座標 |
| `long_name` | string | ❌ 可選 | 任意字串 | 描述性名稱 |

### 依 topology_dimension 的必需屬性

```text
topology_dimension = 1 → edge_node_connectivity 必需
topology_dimension = 2 → face_node_connectivity 必需
topology_dimension = 3 → volume_node_connectivity 必需
```

## 2. 連線性屬性（Connectivity Attributes）

| 屬性名稱 | 型別 | 必需性 | 描述 |
| ---------- | ------ | -------- | ------ |
| `cf_role` | string | ✅ 必需 | 見下表 |
| `start_index` | int | ⚠️ 強烈建議 | 索引起始值（0 或 1） |
| `_FillValue` | 同資料型別 | 條件必需 | 可變長度陣列必需 |
| `long_name` | string | ❌ 可選 | 描述性名稱 |

### cf_role 允許值

| cf_role 值 | 對應連線性 | 維度示例 |
| ------------ | ----------- | --------- |
| `edge_node_connectivity` | 邊→節點 | `(nEdge, Two)` |
| `face_node_connectivity` | 面→節點 | `(nFace, nMax)` |
| `volume_node_connectivity` | 體積→節點 | `(nVol, nMax)` |
| `face_edge_connectivity` | 面→邊 | `(nFace, nMax)` |
| `edge_face_connectivity` | 邊→面 | `(nEdge, Two)` |
| `face_face_connectivity` | 面→相鄰面 | `(nFace, nMax)` |
| `volume_face_connectivity` | 體積→面 | `(nVol, nMax)` |
| `volume_edge_connectivity` | 體積→邊 | `(nVol, nMax)` |
| `volume_volume_connectivity` | 體積→相鄰體積 | `(nVol, nMax)` |
| `boundary_node_connectivity` | 邊界→節點 | `(nBdry, Two)` |
| `volume_shape_type` | 體積形狀型別 | `(nVol,)` |
| `location_index_set` | 位置索引集 | `(nSubset,)` |

## 3. 資料變數屬性（Data Variable Attributes）

| 屬性名稱 | 型別 | 必需性 | 描述 |
| ---------- | ------ | -------- | ------ |
| `mesh` | string | ✅ 必需 | 引用的網格拓撲變數名 |
| `location` | string | ✅ 必需 | 資料所在位置 |
| `location_index_set` | string | ❌ 可選 | 位置索引集變數名（稀疏資料） |
| `coordinates` | string | ⚠️ 建議 | 座標變數名（空格分隔） |
| `standard_name` | string | ⚠️ 建議 | CF 標準名稱 |
| `long_name` | string | ⚠️ 建議 | 描述性名稱 |
| `units` | string | ⚠️ 建議 | UDUNITS 格式的單位 |
| `_FillValue` | 同資料型別 | ⚠️ 建議 | 缺失值標識 |
| `valid_range` | 同資料型別陣列 | ❌ 可選 | 有效值範圍 `[min, max]` |
| `valid_min` | 同資料型別 | ❌ 可選 | 最小有效值 |
| `valid_max` | 同資料型別 | ❌ 可選 | 最大有效值 |
| `scale_factor` | float | ❌ 可選 | 壓縮存儲的縮放因子 |
| `add_offset` | float | ❌ 可選 | 壓縮存儲的偏移量 |
| `grid_mapping` | string | ❌ 可選 | 座標參考系統變數名 |

### location 允許值

| 值 | 意義 | 適用維度 |
| ---- | ------ | --------- |
| `"node"` | 節點（0D 元素） | topology_dimension 1/2/3 |
| `"edge"` | 邊（1D 元素） | topology_dimension 1/2/3 |
| `"face"` | 面（2D 元素） | topology_dimension 2/3 |
| `"volume"` | 體積（3D 元素） | topology_dimension 3 |

## 4. 座標變數屬性（Coordinate Attributes）

| 屬性名稱 | 型別 | 必需性 | 描述 |
| ---------- | ------ | -------- | ------ |
| `standard_name` | string | ⚠️ 建議 | 如 `"longitude"`, `"latitude"` |
| `units` | string | ⚠️ 建議 | 如 `"degrees_east"`, `"m"` |
| `long_name` | string | ❌ 可選 | 描述性名稱 |
| `axis` | string | ❌ 可選 | `"X"`, `"Y"`, `"Z"`, `"T"` |
| `positive` | string | 視情況 | `"up"` 或 `"down"` |
| `grid_mapping` | string | 條件建議 | 使用投影座標時必需 |

### 常見的 standard_name 值

| standard_name | 適用座標 | units |
| --------------- | ---------- | ------- |
| `longitude` | 節點/面/邊 x（地理） | `degrees_east` |
| `latitude` | 節點/面/邊 y（地理） | `degrees_north` |
| `projection_x_coordinate` | 節點/面/邊 x（投影） | `m` |
| `projection_y_coordinate` | 節點/面/邊 y（投影） | `m` |
| `ocean_sigma_coordinate` | 垂直 σ 層 | `1` |
| `time` | 時間座標 | `seconds since ...` |

## 5. 全域屬性（Global Attributes）

| 屬性名稱 | 型別 | 必需性 | 描述 |
| ---------- | ------ | -------- | ------ |
| `Conventions` | string | ✅ 必需 | 如 `"CF-1.12"` |
| `title` | string | ⚠️ 建議 | 資料集標題 |
| `institution` | string | ⚠️ 建議 | 產生機構 |
| `source` | string | ⚠️ 建議 | 資料來源/模型 |
| `history` | string | ⚠️ 建議 | 處理歷程 |
| `references` | string | ⚠️ 建議 | 參考文獻/DOI |
| `comment` | string | ❌ 可選 | 補充說明 |
| `featureType` | string | ❌ 建議 | 見下方 |

### featureType 的推薦值

```cdl
// UGRID 非結構化網格
:featureType = "unstructuredGrid" ;
```

## 6. 壓縮存儲屬性（Packing Attributes）

使用 `scale_factor` 和 `add_offset` 可以用整數儲存浮點資料，節省空間：

```cdl
// 以 int16 存儲溫度（-40 到 60°C，精度 0.001°C）
short temperature(time, nMesh2_face) ;
  temperature:standard_name = "sea_water_potential_temperature" ;
  temperature:units = "degree_Celsius" ;
  temperature:scale_factor = 0.001 ;
  temperature:add_offset = 10.0 ;
  temperature:_FillValue = -32768s ;
  // 實際值 = raw * scale_factor + add_offset
  // 溫度 20°C → 存儲為 (20 - 10) / 0.001 = 10000
```

## 7. 網格映射屬性（Grid Mapping Attributes）

當使用投影座標時，需要一個 CRS（座標參考系統）變數：

### 常見投影的屬性

#### WGS84 地理座標（經緯度）

```cdl
char wgs84 ;
  wgs84:grid_mapping_name = "latitude_longitude" ;
  wgs84:longitude_of_prime_meridian = 0.0 ;
  wgs84:semi_major_axis = 6378137.0 ;
  wgs84:inverse_flattening = 298.257223563 ;
```

#### TWD97 / TM2 zone 121 投影

```cdl
char crs_twd97 ;
  crs_twd97:grid_mapping_name = "transverse_mercator" ;
  crs_twd97:semi_major_axis = 6378137.0 ;
  crs_twd97:inverse_flattening = 298.257222101 ;
  crs_twd97:longitude_of_central_meridian = 121.0 ;
  crs_twd97:latitude_of_projection_origin = 0.0 ;
  crs_twd97:scale_factor_at_central_meridian = 0.9999 ;
  crs_twd97:false_easting = 250000.0 ;
  crs_twd97:false_northing = 0.0 ;
  crs_twd97:projected_coordinate_system_name = "TWD97 / TM2 zone 121" ;
  crs_twd97:geographic_coordinate_system_name = "TWD97" ;
  crs_twd97:horizontal_datum_name = "Taiwan Datum 1997" ;
  crs_twd97:reference_ellipsoid_name = "GRS 1980" ;
  crs_twd97:prime_meridian_name = "Greenwich" ;
  crs_twd97:EPSG_code = "EPSG:3826" ;
```

## 8. 完整屬性示例彙整

```cdl
// ═══════════════════════════════════
// 完整屬性示例：一個 2D 面上的資料變數
// ═══════════════════════════════════
double temperature(time, nMesh2_face) ;

  // UGRID 必需屬性
  temperature:mesh = "Mesh2" ;
  temperature:location = "face" ;

  // CF 建議屬性
  temperature:standard_name = "sea_water_potential_temperature" ;
  temperature:long_name = "Potential temperature at face centroids" ;
  temperature:units = "degree_Celsius" ;
  temperature:coordinates = "Mesh2_face_lon Mesh2_face_lat" ;
  temperature:_FillValue = -9999.0 ;

  // 可選屬性
  temperature:valid_range = -5.0, 45.0 ;
  temperature:grid_mapping = "wgs84" ;
  temperature:cell_methods = "time: mean" ;
  temperature:source = "DLAMP v2.0 FVCOM ocean model" ;
  temperature:comment = "Vertically averaged temperature for 2D simulation" ;
```

## 🔗 相關文件

- [核心概念](../conventions/core-concepts.md) — 屬性架構概述
- [符合性要求](../implementation/conformance.md) — 必需屬性的驗證
- [座標系統](coordinate-systems.md) — CRS 和座標的詳細說明

## 📚 參考資源

- [UGRID 官方屬性列表](https://ugrid-conventions.github.io/ugrid-conventions/#mesh-topology-variable)
- [CF Conventions 屬性](https://cfconventions.org/cf-conventions/cf-conventions.html#attribute-appendix)
- [NetCDF 屬性約定](https://www.unidata.ucar.edu/software/netcdf/docs/attribute_conventions.html)

---

*下一步*: [座標系統](coordinate-systems.md) | [參考文獻](../resources/references.md)
