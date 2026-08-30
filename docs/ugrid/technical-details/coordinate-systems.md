# UGRID 座標系統 (Coordinate Systems)

## 📖 概述

UGRID 支援多種座標系統用於描述網格節點的位置。本文件說明如何正確表達地理座標、投影座標，以及垂直座標系統。

## 1. 水平座標系統

### 1.1 地理座標系（Geographic CRS）

最常見的座標表達方式，直接以**經度（Longitude）**和**緯度（Latitude）**定義節點位置：

```cdl
double Mesh2_node_lon(nMesh2_node) ;
  Mesh2_node_lon:standard_name = "longitude" ;
  Mesh2_node_lon:units = "degrees_east" ;
  Mesh2_node_lon:long_name = "Longitude of 2D mesh nodes" ;

double Mesh2_node_lat(nMesh2_node) ;
  Mesh2_node_lat:standard_name = "latitude" ;
  Mesh2_node_lat:units = "degrees_north" ;
  Mesh2_node_lat:long_name = "Latitude of 2D mesh nodes" ;
```

**適用情況**：

- 大尺度海洋/大氣模型（跨越多個緯度帶）
- 需要與衛星資料或全球資料集整合
- 資料共享和長期歸檔

### 1.2 投影座標系（Projected CRS）

使用地圖投影將球面轉換為平面，以**公尺**為單位的 x/y 座標：

```cdl
double Mesh2_node_x(nMesh2_node) ;
  Mesh2_node_x:standard_name = "projection_x_coordinate" ;
  Mesh2_node_x:units = "m" ;
  Mesh2_node_x:long_name = "Easting coordinate of mesh nodes (TWD97 TM2)" ;
  Mesh2_node_x:grid_mapping = "crs" ;     // ← 必需，指向 CRS 定義

double Mesh2_node_y(nMesh2_node) ;
  Mesh2_node_y:standard_name = "projection_y_coordinate" ;
  Mesh2_node_y:units = "m" ;
  Mesh2_node_y:long_name = "Northing coordinate of mesh nodes (TWD97 TM2)" ;
  Mesh2_node_y:grid_mapping = "crs" ;     // ← 必需

// 座標參考系統定義
char crs ;
  crs:grid_mapping_name = "transverse_mercator" ;
  crs:semi_major_axis = 6378137.0 ;
  crs:inverse_flattening = 298.257222101 ;
  crs:longitude_of_central_meridian = 121.0 ;
  crs:latitude_of_projection_origin = 0.0 ;
  crs:scale_factor_at_central_meridian = 0.9999 ;
  crs:false_easting = 250000.0 ;
  crs:false_northing = 0.0 ;
  crs:EPSG_code = "EPSG:3826" ;
  crs:projected_coordinate_system_name = "TWD97 / TM2 zone 121" ;
```

**適用情況**：

- 區域模型（台灣本島、台灣海峽）
- 需要準確的距離計算（公尺）
- 與 GIS 系統整合（QGIS、ArcGIS）

### 1.3 雙座標（推薦最佳實踐）

當使用投影座標時，**強烈建議同時提供地理座標**作為輔助：

```cdl
// 主要：投影座標（用於數值計算）
double Mesh2_node_x(nMesh2_node) ;
  Mesh2_node_x:standard_name = "projection_x_coordinate" ;
  Mesh2_node_x:units = "m" ;
  Mesh2_node_x:grid_mapping = "crs" ;

double Mesh2_node_y(nMesh2_node) ;
  Mesh2_node_y:standard_name = "projection_y_coordinate" ;
  Mesh2_node_y:units = "m" ;
  Mesh2_node_y:grid_mapping = "crs" ;

// 輔助：地理座標（方便視覺化和資料交換）
double Mesh2_node_lon(nMesh2_node) ;
  Mesh2_node_lon:standard_name = "longitude" ;
  Mesh2_node_lon:units = "degrees_east" ;

double Mesh2_node_lat(nMesh2_node) ;
  Mesh2_node_lat:standard_name = "latitude" ;
  Mesh2_node_lat:units = "degrees_north" ;
```

## 2. 常用座標參考系統（CRS）

### 2.1 WGS84（全球地理座標）

```cdl
char wgs84 ;
  wgs84:grid_mapping_name = "latitude_longitude" ;
  wgs84:longitude_of_prime_meridian = 0.0 ;
  wgs84:semi_major_axis = 6378137.0 ;
  wgs84:inverse_flattening = 298.257223563 ;
  wgs84:EPSG_code = "EPSG:4326" ;
  wgs84:geographic_coordinate_system_name = "WGS 84" ;
  wgs84:horizontal_datum_name = "World Geodetic System 1984" ;
  wgs84:prime_meridian_name = "Greenwich" ;
  wgs84:reference_ellipsoid_name = "WGS 84" ;
```

### 2.2 TWD97 / TM2（台灣基準，二度分帶）

台灣地區最常用的投影座標系：

```cdl
// Zone 119 (台灣本島西部)
char crs_twd97_119 ;
  crs_twd97_119:grid_mapping_name = "transverse_mercator" ;
  crs_twd97_119:semi_major_axis = 6378137.0 ;
  crs_twd97_119:inverse_flattening = 298.257222101 ;
  crs_twd97_119:longitude_of_central_meridian = 119.0 ;
  crs_twd97_119:latitude_of_projection_origin = 0.0 ;
  crs_twd97_119:scale_factor_at_central_meridian = 0.9999 ;
  crs_twd97_119:false_easting = 250000.0 ;
  crs_twd97_119:false_northing = 0.0 ;
  crs_twd97_119:EPSG_code = "EPSG:3825" ;
  crs_twd97_119:projected_coordinate_system_name = "TWD97 / TM2 zone 119" ;

// Zone 121 (台灣本島主要區域)
char crs_twd97_121 ;
  crs_twd97_121:grid_mapping_name = "transverse_mercator" ;
  crs_twd97_121:semi_major_axis = 6378137.0 ;
  crs_twd97_121:inverse_flattening = 298.257222101 ;
  crs_twd97_121:longitude_of_central_meridian = 121.0 ;
  crs_twd97_121:latitude_of_projection_origin = 0.0 ;
  crs_twd97_121:scale_factor_at_central_meridian = 0.9999 ;
  crs_twd97_121:false_easting = 250000.0 ;
  crs_twd97_121:false_northing = 0.0 ;
  crs_twd97_121:EPSG_code = "EPSG:3826" ;
  crs_twd97_121:projected_coordinate_system_name = "TWD97 / TM2 zone 121" ;
```

### 2.3 通用墨卡托投影（UTM）

全球分帶投影，對台灣地區適用 UTM zone 51N：

```cdl
char crs_utm51n ;
  crs_utm51n:grid_mapping_name = "transverse_mercator" ;
  crs_utm51n:semi_major_axis = 6378137.0 ;
  crs_utm51n:inverse_flattening = 298.257223563 ;
  crs_utm51n:longitude_of_central_meridian = 123.0 ;
  crs_utm51n:latitude_of_projection_origin = 0.0 ;
  crs_utm51n:scale_factor_at_central_meridian = 0.9996 ;
  crs_utm51n:false_easting = 500000.0 ;
  crs_utm51n:false_northing = 0.0 ;
  crs_utm51n:EPSG_code = "EPSG:32651" ;
  crs_utm51n:projected_coordinate_system_name = "WGS 84 / UTM zone 51N" ;
```

## 3. 垂直座標系統

### 3.1 σ（Sigma）座標

海洋模型最常用的地形跟隨座標，定義範圍為 [-1, 0]：

```text
σ = (z - η) / (H + η)

其中：
  z：實際高度（公尺，正向上）
  η：水面高度（公尺）
  H：靜止水深（公尺）

σ = 0  → 水面
σ = -1 → 海底
```

```cdl
double sigma(nSigma) ;
  sigma:standard_name = "ocean_sigma_coordinate" ;
  sigma:long_name = "Ocean sigma coordinate at layer midpoints" ;
  sigma:units = "1" ;
  sigma:positive = "up" ;
  sigma:formula_terms = "sigma: sigma eta: water_surface_elevation depth: bathymetry" ;
  sigma:axis = "Z" ;

data:
  // 20 層均勻分布的 σ 座標
  sigma = -0.975, -0.925, -0.875, -0.825, -0.775,
          -0.725, -0.675, -0.625, -0.575, -0.525,
          -0.475, -0.425, -0.375, -0.325, -0.275,
          -0.225, -0.175, -0.125, -0.075, -0.025 ;
```

### 3.2 z 座標（絕對深度）

直接以公尺為單位的深度，適用於固定層網格：

```cdl
double depth(nDepth) ;
  depth:standard_name = "depth" ;
  depth:long_name = "Depth at layer midpoints" ;
  depth:units = "m" ;
  depth:positive = "down" ;       // 向下為正
  depth:axis = "Z" ;

data:
  depth = 5., 15., 30., 50., 100., 200., 500. ;   // 公尺
```

### 3.3 海拔高度（用於大氣模型）

```cdl
double altitude(nAlt) ;
  altitude:standard_name = "altitude" ;
  altitude:long_name = "Altitude above sea level" ;
  altitude:units = "m" ;
  altitude:positive = "up" ;
  altitude:axis = "Z" ;
```

## 4. Python 座標轉換工具

### 4.1 投影座標 ↔ 地理座標

```python
"""座標系統轉換工具。"""

from pyproj import Transformer
import numpy as np


def project_to_latlon(
    x: np.ndarray,
    y: np.ndarray,
    epsg_from: int = 3826
) -> tuple[np.ndarray, np.ndarray]:
    """將投影座標轉換為地理座標（經緯度）。
    
    Args:
        x: 東向座標（公尺）。
        y: 北向座標（公尺）。
        epsg_from: 來源 EPSG 代碼，預設 3826（TWD97/TM2 zone 121）。
        
    Returns:
        (longitude, latitude) 的 tuple，單位為度。
    """
    transformer = Transformer.from_crs(epsg_from, 4326, always_xy=True)
    lon, lat = transformer.transform(x, y)
    return lon, lat


def latlon_to_project(
    lon: np.ndarray,
    lat: np.ndarray,
    epsg_to: int = 3826
) -> tuple[np.ndarray, np.ndarray]:
    """將地理座標（經緯度）轉換為投影座標。
    
    Args:
        lon: 經度（度）。
        lat: 緯度（度）。
        epsg_to: 目標 EPSG 代碼，預設 3826（TWD97/TM2 zone 121）。
        
    Returns:
        (x, y) 的 tuple，單位為公尺。
    """
    transformer = Transformer.from_crs(4326, epsg_to, always_xy=True)
    x, y = transformer.transform(lon, lat)
    return x, y


# 示例
if __name__ == '__main__':
    # 台北市政府的 TWD97 TM2 座標
    x = np.array([306000.0])
    y = np.array([2769000.0])
    
    lon, lat = project_to_latlon(x, y, epsg_from=3826)
    print(f"TWD97 TM2: ({x[0]:.0f}, {y[0]:.0f})")
    print(f"WGS84:     ({lon[0]:.6f}°E, {lat[0]:.6f}°N)")
```

### 4.2 σ 座標轉換為實際深度

```python
"""σ 座標轉換工具。"""

import numpy as np
import netCDF4 as nc


def sigma_to_z(
    sigma: np.ndarray,
    eta: np.ndarray,
    depth: np.ndarray
) -> np.ndarray:
    """將 σ 座標轉換為實際高度（z 座標）。
    
    海洋 σ 座標定義：z = sigma * (H + eta) + eta
    
    Args:
        sigma: σ 座標陣列，shape: (nSigma,)
        eta: 水面高度（公尺），shape: (nNode,) 或廣播相容的形狀。
        depth: 靜止水深（公尺，正值），shape: (nNode,)。
        
    Returns:
        實際高度（公尺，向上為正），shape: (nSigma, nNode)。
    """
    # 廣播：sigma (nSigma,) → (nSigma, 1)
    sigma_2d = sigma[:, np.newaxis]
    
    # z = sigma * (H + eta) + eta
    z = sigma_2d * (depth + eta) + eta
    return z   # shape: (nSigma, nNode)


# 示例
def extract_real_depths(filename: str) -> None:
    """從 UGRID 檔案計算各 σ 層的實際深度。"""
    ds = nc.Dataset(filename)
    
    sigma = ds.variables['sigma'][:]             # (nSigma,)
    eta = ds.variables['water_surface_elevation'][0, :]  # 第 0 時步的水位
    depth = ds.variables['bathymetry'][:]        # 水深（正值）
    
    z_levels = sigma_to_z(sigma, eta, depth)    # (nSigma, nNode)
    
    # 顯示第 100 個節點的垂直層高度
    node_idx = 100
    print(f"節點 {node_idx} 的水深: {depth[node_idx]:.1f} m")
    print(f"節點 {node_idx} 的水位: {eta[node_idx]:.2f} m")
    print("各 σ 層的實際高度:")
    for i, (sig, z) in enumerate(zip(sigma, z_levels[:, node_idx])):
        print(f"  σ={sig:.3f}: z={z:.2f} m")
    
    ds.close()
```

## 5. 常見座標問題與解決

### Q1: 經度範圍 [-180, 180] 還是 [0, 360]？

CF 規範允許兩種範圍，但要保持一致性：

```cdl
// ✅ [-180, 180] 範圍（建議）
Mesh2_node_lon:units = "degrees_east" ;
data: Mesh2_node_lon = -180.0, ..., 180.0 ;

// ✅ [0, 360] 範圍（也接受）
data: Mesh2_node_lon = 0.0, ..., 360.0 ;

// ⚠️ 跨越本初子午線時需特別注意
// 例如：台灣海峽約 120°E，使用 [-180, 180] 更直觀
```

### Q2: 投影座標如何處理跨帶問題？

若網格跨越兩個 TM2 帶（如同時包含 zone 119 和 zone 121 的區域），建議：

1. **使用地理座標**（經緯度）而非投影座標
2. 或選擇一個投影帶，接受邊緣的少量失真

### Q3: 垂直座標的 `positive` 屬性

```cdl
// 向上為正（海洋的 z、σ 座標）
sigma:positive = "up" ;    // σ = 0 在頂部

// 向下為正（水深）
bathymetry:positive = "down" ;  // 正值 = 較深

// ⚠️ 不要混用！
// sigma:positive = "down" 是合法的，但意味著 σ = -1 在頂部（少見）
```

## 🔗 相關文件

- [後設資料屬性](metadata-attributes.md) — 座標變數的完整屬性列表
- [3D 分層示例](../implementation/examples/3d-layered-example.md) — σ 座標的實際應用
- [最佳實踐](../implementation/best-practices.md) — 座標相關建議

## 📚 參考資源

- [CF Conventions - Coordinate Types](https://cfconventions.org/cf-conventions/cf-conventions.html#coordinate-types)
- [CF Conventions - Grid Mappings](https://cfconventions.org/cf-conventions/cf-conventions.html#grid-mappings-and-projections)
- [EPSG 座標系統資料庫](https://epsg.io/) — 查找座標系統 EPSG 代碼
- [pyproj 文件](https://pyproj4.github.io/pyproj/) — Python 座標轉換工具

---

*下一步*: [參考文獻](../resources/references.md) | [常見問題](../resources/faqs.md)
