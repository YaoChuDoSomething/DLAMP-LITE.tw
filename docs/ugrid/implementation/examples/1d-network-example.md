# 1D 網路示例 (1D Network Example)

## 📖 概述

本示例演示如何使用 UGRID 表達一個**一維河道網路（1D Network）**——最基礎的非結構化網格形式。

**適用場景**：

- 河川、水系、排水網路
- 管線網路（水管、油管）
- 道路/鐵路網路
- 電力傳輸線路

在 1D 網路中，網格的基本元素是**節點（Nodes）**和**邊（Edges）**：

```text
O──────O──────O──────O       ← 節點（Nodes）連接構成
  edge0  edge1  edge2         ← 邊（Edges）= 一維線段
```

## 🗺️ 示例：台灣淡水河流域網路

以下示例模擬台灣淡水河主流及主要支流的水位傳遞網路：

```text
         ○ 大漢溪上游 (Node 4)
         │
         │ 大漢溪 (Edge 3)
         │
○────────○────────○
上游    匯流點   下游出海口
(Node 0) (Node 2) (Node 1)
         │
         │ 新店溪 (Edge 4)
         │
         ○ 新店溪上游 (Node 3)
```

## 🔧 完整 CDL 示例

```cdl
netcdf tamsui_river_network {

:Conventions = "CF-1.12" ;
:title = "Tamsui River System 1D Network" ;
:institution = "National Taiwan University" ;
:source = "DLAMP 1D River Model" ;
:history = "2024-06-01 Created for demonstration" ;
:featureType = "unstructuredGrid" ;

dimensions:
  nNetwork_node = 5 ;         // 5 個節點（上下游端點 + 匯流點）
  nNetwork_edge = 4 ;         // 4 條邊（4 個河段）
  Two           = 2 ;         // 每條邊連接 2 個節點（固定）
  time          = UNLIMITED ; // 時間維度（無限延伸）

variables:

  // ═══════════════════════════════════════════════
  // 網格拓撲
  // ═══════════════════════════════════════════════
  integer Network ;
    Network:cf_role = "mesh_topology" ;
    Network:topology_dimension = 1 ;               // 1D 網格
    Network:node_coordinates = "Network_node_x Network_node_y" ;
    Network:edge_node_connectivity = "Network_edge_nodes" ;
    Network:edge_coordinates = "Network_edge_x Network_edge_y" ;
    Network:long_name = "1D Tamsui River Network" ;

  // ═══════════════════════════════════════════════
  // 連線性（Connectivity）
  // ═══════════════════════════════════════════════
  integer Network_edge_nodes(nNetwork_edge, Two) ;
    Network_edge_nodes:cf_role = "edge_node_connectivity" ;
    Network_edge_nodes:start_index = 0 ;
    Network_edge_nodes:long_name = "Maps every edge to its two end nodes" ;

  // ═══════════════════════════════════════════════
  // 節點座標
  // ═══════════════════════════════════════════════
  double Network_node_x(nNetwork_node) ;
    Network_node_x:standard_name = "longitude" ;
    Network_node_x:units = "degrees_east" ;
    Network_node_x:long_name = "Longitude of 1D network nodes" ;

  double Network_node_y(nNetwork_node) ;
    Network_node_y:standard_name = "latitude" ;
    Network_node_y:units = "degrees_north" ;
    Network_node_y:long_name = "Latitude of 1D network nodes" ;

  // ═══════════════════════════════════════════════
  // 邊中心座標（可選，但建議提供）
  // ═══════════════════════════════════════════════
  double Network_edge_x(nNetwork_edge) ;
    Network_edge_x:standard_name = "longitude" ;
    Network_edge_x:units = "degrees_east" ;
    Network_edge_x:long_name = "Longitude of 1D network edge midpoints" ;

  double Network_edge_y(nNetwork_edge) ;
    Network_edge_y:standard_name = "latitude" ;
    Network_edge_y:units = "degrees_north" ;
    Network_edge_y:long_name = "Latitude of 1D network edge midpoints" ;

  // ═══════════════════════════════════════════════
  // 靜態屬性（與時間無關的河道特性）
  // ═══════════════════════════════════════════════
  double channel_length(nNetwork_edge) ;
    channel_length:standard_name = "length_of_channel" ;
    channel_length:long_name = "Length of each channel reach" ;
    channel_length:units = "m" ;
    channel_length:mesh = "Network" ;
    channel_length:location = "edge" ;

  double channel_slope(nNetwork_edge) ;
    channel_slope:long_name = "Average bed slope of each channel reach" ;
    channel_slope:units = "1" ;     // 無因次，m/m
    channel_slope:mesh = "Network" ;
    channel_slope:location = "edge" ;

  double bank_elevation(nNetwork_node) ;
    bank_elevation:standard_name = "bank_elevation" ;
    bank_elevation:long_name = "Bank top elevation at node" ;
    bank_elevation:units = "m" ;
    bank_elevation:positive = "up" ;
    bank_elevation:mesh = "Network" ;
    bank_elevation:location = "node" ;

  // ═══════════════════════════════════════════════
  // 動態資料（隨時間變化的水文量）
  // ═══════════════════════════════════════════════
  double water_level(time, nNetwork_node) ;
    water_level:standard_name = "water_surface_height_above_reference_datum" ;
    water_level:long_name = "Water surface elevation at network nodes" ;
    water_level:units = "m" ;
    water_level:positive = "up" ;
    water_level:mesh = "Network" ;
    water_level:location = "node" ;
    water_level:coordinates = "Network_node_x Network_node_y" ;
    water_level:_FillValue = -9999.0 ;

  double flow_discharge(time, nNetwork_edge) ;
    flow_discharge:standard_name = "water_volume_transport_in_river_channel" ;
    flow_discharge:long_name = "Water discharge through each channel reach" ;
    flow_discharge:units = "m3 s-1" ;
    flow_discharge:mesh = "Network" ;
    flow_discharge:location = "edge" ;
    flow_discharge:coordinates = "Network_edge_x Network_edge_y" ;
    flow_discharge:_FillValue = -9999.0 ;

  double flow_velocity(time, nNetwork_edge) ;
    flow_velocity:standard_name = "sea_water_speed" ;
    flow_velocity:long_name = "Cross-sectional averaged flow velocity" ;
    flow_velocity:units = "m s-1" ;
    flow_velocity:mesh = "Network" ;
    flow_velocity:location = "edge" ;
    flow_velocity:coordinates = "Network_edge_x Network_edge_y" ;
    flow_velocity:_FillValue = -9999.0 ;

  // ═══════════════════════════════════════════════
  // 時間座標
  // ═══════════════════════════════════════════════
  double time(time) ;
    time:standard_name = "time" ;
    time:long_name = "Simulation time" ;
    time:units = "seconds since 2024-01-01 00:00:00 +08:00" ;
    time:calendar = "proleptic_gregorian" ;
    time:axis = "T" ;

data:

  // 節點座標（5 個節點的經緯度）
  //   Node 0: 大漢溪上游
  //   Node 1: 下游出海口
  //   Node 2: 大漢溪 + 新店溪匯流點
  //   Node 3: 新店溪上游
  //   Node 4: 另一條支流上游
  Network_node_x = 121.20, 121.45, 121.30, 121.28, 121.18 ;
  Network_node_y = 24.95,  25.18,  25.05,  24.93,  25.00  ;

  // 邊連線性（每條邊連接的兩個節點，0-based 索引）
  //   Edge 0: Node 0 → Node 2  (大漢溪段1)
  //   Edge 1: Node 2 → Node 1  (匯流點→出海口)
  //   Edge 2: Node 3 → Node 2  (新店溪)
  //   Edge 3: Node 4 → Node 2  (支流)
  Network_edge_nodes = 
    0, 2,    // Edge 0
    2, 1,    // Edge 1
    3, 2,    // Edge 2
    4, 2 ;   // Edge 3

  // 邊中心座標（各段中點）
  Network_edge_x = 121.25, 121.375, 121.29, 121.24 ;
  Network_edge_y = 25.00,  25.115,  24.99,  25.025 ;

  // 靜態屬性
  channel_length = 8500., 12300., 7200., 6800. ;   // 公尺
  channel_slope  = 0.0012, 0.0005, 0.0015, 0.0020 ; // m/m

  bank_elevation = 25.0, 3.5, 12.0, 28.0, 22.0 ;  // 公尺

  // 動態資料（兩個時步的示例）
  water_level =
    18.5, 3.1, 9.2, 21.0, 15.8,    // t=0
    20.1, 3.5, 10.5, 22.8, 17.3 ;  // t=1

  flow_discharge =
    125.0, 350.0, 185.0, 95.0,    // t=0
    215.0, 580.0, 310.0, 160.0 ;  // t=1

  flow_velocity =
    0.82, 1.15, 0.95, 0.78,    // t=0
    1.35, 1.88, 1.52, 1.25 ;   // t=1

  time = 0., 3600. ;   // 0 秒, 3600 秒 (1 小時)

} // end tamsui_river_network
```

## 🐍 Python 建立示例

```python
"""建立 UGRID 1D 河道網路 NetCDF 檔案的示例。"""

import netCDF4 as nc
import numpy as np

def create_1d_network(filename: str) -> None:
    """建立 1D 河道網路 UGRID NetCDF 檔案。
    
    Args:
        filename: 輸出 NetCDF 檔案路徑。
    """
    ds = nc.Dataset(filename, 'w', format='NETCDF4')
    
    # 全域屬性
    ds.Conventions = "CF-1.12"
    ds.title = "Tamsui River System 1D Network"
    ds.institution = "National Taiwan University"
    ds.featureType = "unstructuredGrid"
    
    # 維度
    ds.createDimension('nNetwork_node', 5)
    ds.createDimension('nNetwork_edge', 4)
    ds.createDimension('Two', 2)
    ds.createDimension('time', None)  # 無限維度
    
    # 網格拓撲變數
    topology = ds.createVariable('Network', 'i4', ())
    topology.cf_role = "mesh_topology"
    topology.topology_dimension = 1
    topology.node_coordinates = "Network_node_x Network_node_y"
    topology.edge_node_connectivity = "Network_edge_nodes"
    topology.edge_coordinates = "Network_edge_x Network_edge_y"
    topology.long_name = "1D Tamsui River Network"
    topology[:] = -1  # 純拓撲變數，值沒有意義
    
    # 連線性
    edge_nodes = ds.createVariable(
        'Network_edge_nodes', 'i4', ('nNetwork_edge', 'Two'))
    edge_nodes.cf_role = "edge_node_connectivity"
    edge_nodes.start_index = 0
    edge_nodes[:] = [[0, 2], [2, 1], [3, 2], [4, 2]]
    
    # 節點座標
    node_x = ds.createVariable('Network_node_x', 'f8', ('nNetwork_node',))
    node_x.standard_name = "longitude"
    node_x.units = "degrees_east"
    node_x[:] = [121.20, 121.45, 121.30, 121.28, 121.18]
    
    node_y = ds.createVariable('Network_node_y', 'f8', ('nNetwork_node',))
    node_y.standard_name = "latitude"
    node_y.units = "degrees_north"
    node_y[:] = [24.95, 25.18, 25.05, 24.93, 25.00]
    
    # 邊中心座標
    edge_x = ds.createVariable('Network_edge_x', 'f8', ('nNetwork_edge',))
    edge_x.standard_name = "longitude"
    edge_x.units = "degrees_east"
    edge_x[:] = [121.25, 121.375, 121.29, 121.24]
    
    edge_y = ds.createVariable('Network_edge_y', 'f8', ('nNetwork_edge',))
    edge_y.standard_name = "latitude"
    edge_y.units = "degrees_north"
    edge_y[:] = [25.00, 25.115, 24.99, 25.025]
    
    # 資料變數
    water_level = ds.createVariable(
        'water_level', 'f8', ('time', 'nNetwork_node'),
        fill_value=-9999.0, zlib=True, complevel=4)
    water_level.standard_name = "water_surface_height_above_reference_datum"
    water_level.units = "m"
    water_level.mesh = "Network"
    water_level.location = "node"
    water_level.coordinates = "Network_node_x Network_node_y"
    
    discharge = ds.createVariable(
        'flow_discharge', 'f8', ('time', 'nNetwork_edge'),
        fill_value=-9999.0, zlib=True, complevel=4)
    discharge.standard_name = "water_volume_transport_in_river_channel"
    discharge.units = "m3 s-1"
    discharge.mesh = "Network"
    discharge.location = "edge"
    discharge.coordinates = "Network_edge_x Network_edge_y"
    
    # 時間
    time_var = ds.createVariable('time', 'f8', ('time',))
    time_var.standard_name = "time"
    time_var.units = "seconds since 2024-01-01 00:00:00 +08:00"
    time_var.calendar = "proleptic_gregorian"
    
    # 寫入資料
    time_var[:] = [0., 3600.]
    water_level[:] = [[18.5, 3.1, 9.2, 21.0, 15.8],
                      [20.1, 3.5, 10.5, 22.8, 17.3]]
    discharge[:] = [[125.0, 350.0, 185.0, 95.0],
                    [215.0, 580.0, 310.0, 160.0]]
    
    ds.close()
    print(f"已建立: {filename}")

if __name__ == '__main__':
    create_1d_network('tamsui_river.nc')
```

## 🎨 視覺化示例（Python）

```python
"""讀取並視覺化 1D 河道網路的示例。"""

import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def plot_1d_network(filename: str) -> None:
    """繪製 1D 河道網路及流量資料。
    
    Args:
        filename: UGRID NetCDF 檔案路徑。
    """
    ds = nc.Dataset(filename)
    
    # 讀取座標和連線性
    node_x = ds.variables['Network_node_x'][:]
    node_y = ds.variables['Network_node_y'][:]
    edge_nodes = ds.variables['Network_edge_nodes'][:]  # shape: (nEdge, 2)
    
    # 讀取資料（第一個時步）
    water_level = ds.variables['water_level'][0, :]
    discharge = ds.variables['flow_discharge'][0, :]
    
    # 建立圖形
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 左：水位（節點）
    ax = axes[0]
    scatter = ax.scatter(
        node_x, node_y,
        c=water_level,
        s=200, cmap='Blues', zorder=5, edgecolors='navy'
    )
    # 繪製邊（河段）
    for i, (n0, n1) in enumerate(edge_nodes):
        ax.plot(
            [node_x[n0], node_x[n1]],
            [node_y[n0], node_y[n1]],
            'b-', linewidth=2, alpha=0.5
        )
    plt.colorbar(scatter, ax=ax, label='水位 (m)')
    ax.set_title('節點水位分布')
    ax.set_xlabel('經度')
    ax.set_ylabel('緯度')
    
    # 右：流量（邊）
    ax = axes[1]
    norm = mcolors.Normalize(vmin=discharge.min(), vmax=discharge.max())
    cmap = plt.cm.get_cmap('Reds')
    for i, (n0, n1) in enumerate(edge_nodes):
        color = cmap(norm(discharge[i]))
        ax.plot(
            [node_x[n0], node_x[n1]],
            [node_y[n0], node_y[n1]],
            color=color, linewidth=4
        )
        # 標記邊的中點
        mid_x = (node_x[n0] + node_x[n1]) / 2
        mid_y = (node_y[n0] + node_y[n1]) / 2
        ax.text(mid_x, mid_y, f'{discharge[i]:.0f}',
                ha='center', fontsize=9)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    plt.colorbar(sm, ax=ax, label='流量 (m³/s)')
    ax.scatter(node_x, node_y, c='black', s=50, zorder=5)
    ax.set_title('邊流量分布')
    ax.set_xlabel('經度')
    ax.set_ylabel('緯度')
    
    plt.tight_layout()
    plt.savefig('tamsui_network_visualization.png', dpi=150, bbox_inches='tight')
    plt.show()
    
    ds.close()

if __name__ == '__main__':
    plot_1d_network('tamsui_river.nc')
```

## 📊 典型應用與常見問題

### Q1: 1D 網路可以表達環狀（迴路）嗎？

✅ 可以。UGRID 1D 網路不限制為樹狀結構，允許存在迴路（環狀管網）：

```text
        ○─────○
       / \   / \
      ○   ○─○   ○
       \ /   \ /
        ○─────○
```

### Q2: 如何表達節點的分叉（一對多）？

```text
// 一個節點 (Node 2) 可以連接多條邊
Network_edge_nodes =
  0, 2,   // Edge 0: 上游1 → 匯流點
  1, 2,   // Edge 1: 上游2 → 匯流點
  2, 3 ;  // Edge 2: 匯流點 → 下游
```

### Q3: 邊的方向（edge_nodes 的順序）是否有意義？

依預設，UGRID 對邊的方向（節點 0 → 節點 1）**不強制規定物理意義**，但模型可以用這個方向定義正流向。建議在全域屬性或 `long_name` 中說明慣例。

## 🔗 相關文件

- [1D 網路拓撲結構](../../conventions/topology/1d-network.md) — 詳細拓撲說明
- [2D 三角形示例](2d-triangular-example.md) — 進階示例
- [最佳實踐](../best-practices.md) — 一般最佳實踐

---

*下一步*: [2D 三角形示例](2d-triangular-example.md) | [符合性要求](../conformance.md)
