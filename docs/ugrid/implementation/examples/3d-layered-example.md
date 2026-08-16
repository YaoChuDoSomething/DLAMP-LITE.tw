# 3D 分層網格示例 (3D Layered Mesh Example)

## 📖 概述

本示例演示如何使用 UGRID 表達一個**三維分層非結構化網格（3D Layered Unstructured Mesh）**——將 2D 非結構化網格在垂直方向延伸的常見海洋模型網格形式。

**適用場景**：

- 三維海洋環流模式（如 FVCOM-3D、ROMS、SCHISM）
- 大氣三維模擬
- 地下水三維流場
- 湖泊溫鹽躍層模擬

**3D 分層網格的結構**：

```text
         海面 (σ=0)
    ○────○────○────○
   /|   /|   /|   /|   ← Layer 0 (表層)
  ○─○──○─○──○─○──○─○
   \|   \|   \|   \|   ← Layer 1
    ○────○────○────○
   /|   /|   /|   /|   ← Layer 2
  ○─○──○─○──○─○──○─○
   \|   \|   \|   \|
    ○────○────○────○
         海底 (σ=-1)
```

## 🏗️ 3D 分層網格的 UGRID 表達策略

UGRID 提供兩種方式表達 3D 分層數據：

### 方式 A：2D 網格 + 垂直座標（推薦）

使用 2D `mesh_topology` (topology_dimension=2) + 分開的垂直座標維度：

```cdl
// 2D 水平網格 + 垂直 σ 層
integer Mesh2 ;
  Mesh2:cf_role = "mesh_topology" ;
  Mesh2:topology_dimension = 2 ;     // ← 2D，水平網格
  ...

// 3D 資料變數使用 (time, nLayer, nFace) 的維度
double temperature(time, nSigma, nMesh2_face) ;
  temperature:mesh = "Mesh2" ;       // 引用 2D 網格
  temperature:location = "face" ;    // 水平位置 = 面
  temperature:coordinates = "sigma Mesh2_face_lon Mesh2_face_lat" ;
```

### 方式 B：3D `mesh_topology` (topology_dimension=3)

使用真正的 3D 體積元素（稜柱體、六面體等）：

```cdl
integer Mesh3D ;
  Mesh3D:cf_role = "mesh_topology" ;
  Mesh3D:topology_dimension = 3 ;   // ← 真正 3D 網格
  Mesh3D:volume_node_connectivity = "Mesh3D_volume_nodes" ;
  ...
```

> 💡 **建議**：多數海洋模型使用**方式 A**，因為體積連線性（方式 B）的計算和存儲成本更高，且水平平流和垂直混合通常分開處理。

## 🔧 完整 CDL 示例（方式 A）

```cdl
netcdf taiwan_strait_3d {

:Conventions = "CF-1.12" ;
:title = "Taiwan Strait 3D Ocean Simulation" ;
:institution = "National Taiwan University" ;
:source = "DLAMP FVCOM-3D v2.0" ;
:history = "2024-06-01 3D ocean model output" ;
:featureType = "unstructuredGrid" ;

dimensions:
  nMesh2_node  = 2500 ;     // 2D 水平節點數
  nMesh2_face  = 4800 ;     // 2D 水平面數（三角形）
  Three        = 3 ;
  Two          = 2 ;
  nSigma       = 20 ;       // 垂直 σ 層數
  nSigma_w     = 21 ;       // σ 層界面數（= nSigma + 1）
  time         = UNLIMITED ;

variables:

  // ═══════════════════════════════════════════════
  // 2D 水平網格拓撲（作為 3D 的水平骨架）
  // ═══════════════════════════════════════════════
  integer Mesh2 ;
    Mesh2:cf_role = "mesh_topology" ;
    Mesh2:topology_dimension = 2 ;
    Mesh2:node_coordinates = "Mesh2_node_lon Mesh2_node_lat" ;
    Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
    Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;
    Mesh2:face_face_connectivity = "Mesh2_face_faces" ;
    Mesh2:face_coordinates = "Mesh2_face_lon Mesh2_face_lat" ;
    Mesh2:long_name = "Horizontal 2D triangular mesh (basis for 3D layers)" ;

  // ═══════════════════════════════════════════════
  // 連線性（2D 水平）
  // ═══════════════════════════════════════════════
  integer Mesh2_face_nodes(nMesh2_face, Three) ;
    Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
    Mesh2_face_nodes:start_index = 0 ;

  integer Mesh2_edge_nodes(nMesh2_edge, Two) ;
    Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
    Mesh2_edge_nodes:start_index = 0 ;

  integer Mesh2_face_faces(nMesh2_face, Three) ;
    Mesh2_face_faces:cf_role = "face_face_connectivity" ;
    Mesh2_face_faces:start_index = 0 ;
    Mesh2_face_faces:_FillValue = -1 ;

  // ═══════════════════════════════════════════════
  // 水平座標
  // ═══════════════════════════════════════════════
  double Mesh2_node_lon(nMesh2_node) ;
    Mesh2_node_lon:standard_name = "longitude" ;
    Mesh2_node_lon:units = "degrees_east" ;

  double Mesh2_node_lat(nMesh2_node) ;
    Mesh2_node_lat:standard_name = "latitude" ;
    Mesh2_node_lat:units = "degrees_north" ;

  double Mesh2_face_lon(nMesh2_face) ;
    Mesh2_face_lon:standard_name = "longitude" ;
    Mesh2_face_lon:units = "degrees_east" ;
    Mesh2_face_lon:long_name = "Longitude of face centroids" ;

  double Mesh2_face_lat(nMesh2_face) ;
    Mesh2_face_lat:standard_name = "latitude" ;
    Mesh2_face_lat:units = "degrees_north" ;
    Mesh2_face_lat:long_name = "Latitude of face centroids" ;

  // ═══════════════════════════════════════════════
  // 垂直座標（σ 座標系）
  // ═══════════════════════════════════════════════
  double sigma(nSigma) ;
    sigma:standard_name = "ocean_sigma_coordinate" ;
    sigma:long_name = "Mid-layer ocean sigma coordinate" ;
    sigma:units = "1" ;
    sigma:positive = "up" ;
    sigma:formula_terms = "sigma: sigma eta: water_surface_elevation depth: bathymetry" ;
    sigma:axis = "Z" ;

  double sigma_w(nSigma_w) ;
    sigma_w:standard_name = "ocean_sigma_coordinate" ;
    sigma_w:long_name = "Layer interface ocean sigma coordinate" ;
    sigma_w:units = "1" ;
    sigma_w:positive = "up" ;
    sigma_w:formula_terms = "sigma: sigma_w eta: water_surface_elevation depth: bathymetry" ;
    sigma_w:axis = "Z" ;

  // ═══════════════════════════════════════════════
  // 靜態屬性
  // ═══════════════════════════════════════════════
  double bathymetry(nMesh2_node) ;
    bathymetry:standard_name = "sea_floor_depth_below_geoid" ;
    bathymetry:long_name = "Water column depth at mesh nodes" ;
    bathymetry:units = "m" ;
    bathymetry:positive = "down" ;
    bathymetry:mesh = "Mesh2" ;
    bathymetry:location = "node" ;
    bathymetry:coordinates = "Mesh2_node_lon Mesh2_node_lat" ;
    bathymetry:_FillValue = -9999.0 ;

  // ═══════════════════════════════════════════════
  // 2D 動態量（水面）
  // ═══════════════════════════════════════════════
  double water_surface_elevation(time, nMesh2_node) ;
    water_surface_elevation:standard_name = "sea_surface_height_above_geoid" ;
    water_surface_elevation:long_name = "Water surface elevation at nodes" ;
    water_surface_elevation:units = "m" ;
    water_surface_elevation:positive = "up" ;
    water_surface_elevation:mesh = "Mesh2" ;
    water_surface_elevation:location = "node" ;
    water_surface_elevation:coordinates = "Mesh2_node_lon Mesh2_node_lat" ;
    water_surface_elevation:_FillValue = -9999.0 ;

  double u_barotropic(time, nMesh2_face) ;
    u_barotropic:standard_name = "eastward_sea_water_velocity" ;
    u_barotropic:long_name = "Depth-averaged eastward velocity (barotropic)" ;
    u_barotropic:units = "m s-1" ;
    u_barotropic:mesh = "Mesh2" ;
    u_barotropic:location = "face" ;
    u_barotropic:coordinates = "Mesh2_face_lon Mesh2_face_lat" ;
    u_barotropic:_FillValue = -9999.0 ;

  double v_barotropic(time, nMesh2_face) ;
    v_barotropic:standard_name = "northward_sea_water_velocity" ;
    v_barotropic:long_name = "Depth-averaged northward velocity (barotropic)" ;
    v_barotropic:units = "m s-1" ;
    v_barotropic:mesh = "Mesh2" ;
    v_barotropic:location = "face" ;
    v_barotropic:coordinates = "Mesh2_face_lon Mesh2_face_lat" ;
    v_barotropic:_FillValue = -9999.0 ;

  // ═══════════════════════════════════════════════
  // 3D 動態量（各 σ 層）
  // ═══════════════════════════════════════════════
  double temperature(time, nSigma, nMesh2_face) ;
    temperature:standard_name = "sea_water_potential_temperature" ;
    temperature:long_name = "Potential temperature at sigma layer midpoints" ;
    temperature:units = "degree_Celsius" ;
    temperature:mesh = "Mesh2" ;
    temperature:location = "face" ;
    temperature:coordinates = "sigma Mesh2_face_lon Mesh2_face_lat" ;
    temperature:_FillValue = -9999.0 ;

  double salinity(time, nSigma, nMesh2_face) ;
    salinity:standard_name = "sea_water_practical_salinity" ;
    salinity:long_name = "Salinity at sigma layer midpoints" ;
    salinity:units = "1e-3" ;
    salinity:mesh = "Mesh2" ;
    salinity:location = "face" ;
    salinity:coordinates = "sigma Mesh2_face_lon Mesh2_face_lat" ;
    salinity:_FillValue = -9999.0 ;

  double u_baroclinic(time, nSigma, nMesh2_face) ;
    u_baroclinic:standard_name = "eastward_sea_water_velocity" ;
    u_baroclinic:long_name = "Eastward velocity at sigma layer midpoints" ;
    u_baroclinic:units = "m s-1" ;
    u_baroclinic:mesh = "Mesh2" ;
    u_baroclinic:location = "face" ;
    u_baroclinic:coordinates = "sigma Mesh2_face_lon Mesh2_face_lat" ;
    u_baroclinic:_FillValue = -9999.0 ;

  double v_baroclinic(time, nSigma, nMesh2_face) ;
    v_baroclinic:standard_name = "northward_sea_water_velocity" ;
    v_baroclinic:long_name = "Northward velocity at sigma layer midpoints" ;
    v_baroclinic:units = "m s-1" ;
    v_baroclinic:mesh = "Mesh2" ;
    v_baroclinic:location = "face" ;
    v_baroclinic:coordinates = "sigma Mesh2_face_lon Mesh2_face_lat" ;
    v_baroclinic:_FillValue = -9999.0 ;

  // 垂直速度定義在 σ 界面（nSigma_w 層）
  double w_velocity(time, nSigma_w, nMesh2_node) ;
    w_velocity:standard_name = "upward_sea_water_velocity" ;
    w_velocity:long_name = "Vertical velocity at sigma interfaces and nodes" ;
    w_velocity:units = "m s-1" ;
    w_velocity:mesh = "Mesh2" ;
    w_velocity:location = "node" ;
    w_velocity:coordinates = "sigma_w Mesh2_node_lon Mesh2_node_lat" ;
    w_velocity:_FillValue = -9999.0 ;

  // ═══════════════════════════════════════════════
  // 時間座標
  // ═══════════════════════════════════════════════
  double time(time) ;
    time:standard_name = "time" ;
    time:units = "seconds since 2024-01-01 00:00:00 +08:00" ;
    time:calendar = "proleptic_gregorian" ;
    time:axis = "T" ;

data:

  // σ 層中點（均勻 20 層）
  sigma = -0.975, -0.925, -0.875, -0.825, -0.775,
          -0.725, -0.675, -0.625, -0.575, -0.525,
          -0.475, -0.425, -0.375, -0.325, -0.275,
          -0.225, -0.175, -0.125, -0.075, -0.025 ;

  // σ 界面（21 個，從底到頂）
  sigma_w = -1.0, -0.95, -0.90, ..., -0.05, 0.0 ;

} // end taiwan_strait_3d
```

## 🐍 Python 工具：三維資料處理

```python
"""3D 分層 UGRID 資料的讀取和分析工具。"""

import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt


def extract_depth_profile(filename: str, face_idx: int,
                          time_idx: int = 0) -> tuple:
    """提取指定面的垂直溫鹽剖面。
    
    Args:
        filename: UGRID NetCDF 檔案路徑。
        face_idx: 面索引（0-based）。
        time_idx: 時步索引（0-based）。
        
    Returns:
        包含 (depth_m, temperature, salinity) 的 tuple。
    """
    ds = nc.Dataset(filename)
    
    # 讀取垂直座標
    sigma = ds.variables['sigma'][:]        # shape: (nSigma,)
    
    # 讀取水深（這裡需要節點的水深對應到面）
    bathymetry_node = ds.variables['bathymetry'][:]
    face_nodes = ds.variables['Mesh2_face_nodes'][:]
    bath_face = bathymetry_node[face_nodes[face_idx]].mean()   # 面平均水深
    
    # 讀取水位（簡化：不考慮潮差）
    eta = 0.0
    
    # 計算實際深度（公尺）
    depth_m = sigma * (bath_face + eta)  # σ 轉換為實際深度
    
    # 讀取溫鹽
    temp = ds.variables['temperature'][time_idx, :, face_idx]
    salt = ds.variables['salinity'][time_idx, :, face_idx]
    
    ds.close()
    return depth_m, temp, salt


def compute_mixed_layer_depth(temperature: np.ndarray,
                               depth_m: np.ndarray,
                               criterion: float = 0.5) -> float:
    """計算混合層深度（溫度梯度法）。
    
    Args:
        temperature: 從海面到海底的溫度剖面（°C）。
        depth_m: 對應深度（公尺，負值向下）。
        criterion: 混合層溫度差定義（°C），預設 0.5°C。
        
    Returns:
        混合層深度（正值，公尺）。
    """
    # 從海面（最後一個 σ 層）向下搜尋
    sst = temperature[-1]  # 海面溫度
    for i in range(len(temperature) - 1, -1, -1):
        if sst - temperature[i] > criterion:
            return abs(depth_m[i])
    return abs(depth_m[0])  # 若未找到，返回最大深度


def plot_ts_diagram(filename: str, time_idx: int = 0,
                    n_sample: int = 500) -> None:
    """繪製 T-S 圖（溫鹽關係圖）。
    
    Args:
        filename: UGRID NetCDF 檔案路徑。
        time_idx: 時步索引。
        n_sample: 隨機取樣的面數。
    """
    ds = nc.Dataset(filename)
    
    nFace = ds.dimensions['nMesh2_face'].size
    sample_idx = np.random.choice(nFace, min(n_sample, nFace), replace=False)
    
    temp = ds.variables['temperature'][time_idx, :, sample_idx]  # (nSigma, n)
    salt = ds.variables['salinity'][time_idx, :, sample_idx]
    sigma = ds.variables['sigma'][:]
    
    # σ 對應顏色（-1=底層=藍，0=表層=紅）
    fig, ax = plt.subplots(figsize=(8, 6))
    for k, sig in enumerate(sigma):
        color = plt.cm.RdBu_r((sig + 1) / 2)  # 藍→紅對應底→頂
        ax.scatter(salt[k], temp[k], c=[color], s=2, alpha=0.3)
    
    # 顏色條
    sm = plt.cm.ScalarMappable(cmap='RdBu_r',
                                norm=plt.Normalize(-1, 0))
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label='σ 座標 (底=-1, 頂=0)')
    
    ax.set_xlabel('鹽度 (psu)')
    ax.set_ylabel('溫度 (°C)')
    ax.set_title('T-S 圖（溫鹽關係）')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('ts_diagram.png', dpi=150)
    plt.show()
    
    ds.close()
```

## 📊 3D UGRID 的資料維度一覽

| 物理量 | 位置 | 典型維度 | 說明 |
| -------- | ------ | ---------- | ------ |
| 水位 | node | `(time, nNode)` | 2D，水平 |
| 深度平均流速 | face | `(time, nFace)` | 2D，水平 |
| 溫度/鹽度 | face | `(time, nSigma, nFace)` | 3D |
| 水平流速 | face | `(time, nSigma, nFace)` | 3D |
| 垂直速度 | node | `(time, nSigma_w, nNode)` | 定義在界面 |
| 渦動黏滯係數 | face | `(time, nSigma_w, nFace)` | 定義在界面 |

## 🔗 相關文件

- [3D 分層拓撲結構](../../conventions/topology/3d-layered.md) — 拓撲概念說明
- [3D 非結構化拓撲](../../conventions/topology/3d-unstructured.md) — 真正 3D 體積元素
- [2D 三角形示例](2d-triangular-example.md) — 水平部分詳細說明
- [最佳實踐](../best-practices.md) — 效能最佳化建議

---

*下一步*: [索引技術細節](../../technical-details/indexing.md) | [最佳實踐](../best-practices.md)
