# 1D 網路拓撲 (1D Network Topology)

## 📖 概述

**1D 網路拓撲** 用於描述 **一維的線性網路結構**，例如：

- 河流系統
- 管道網路
- 道路網路
- 電力線路
- 其他一維連線結構

這是 UGRID 中最簡單的拓撲型別，只包含 **節點 (Nodes)** 和 **邊 (Edges)** 兩種幾何元素。

## 🏗️ 基本結構

1D 網路由以下元件組成：

```
Node 0 ●────────● Node 1
          Edge 0
          
Node 1 ●────────● Node 2
          Edge 1
          
Node 2 ●────────● Node 3
          Edge 2
```

### 幾何元素

| 元素 | 維度 | 描述 | 數量 |
|------|------|------|------|
| Node | 0D | 網路中的點 | nNodes |
| Edge | 1D | 連線兩個節點的線段 | nEdges |

## 📋 必需屬性

### 網格拓撲變數屬性

1D 網路的網格拓撲變數 **必須** 包含以下屬性：

| 屬性 | 型別 | 必需性 | 描述 |
| ------ | ------ | -------- | ------ |
| `cf_role` | string | ✅ 必需 | 必須為 `"mesh_topology"` |
| `topology_dimension` | int | ✅ 必需 | 必須為 `1` |
| `node_coordinates` | string | ✅ 必需 | 節點座標變數名 (空格分隔) |
| `edge_node_connectivity` | string | ✅ 必需 | 邊-節點連線性變數名 |

### 可選屬性

| 屬性 | 型別 | 必需性 | 描述 |
|------|------|--------|------|
| `long_name` | string | ❌ 可選 | 描述性名稱 |
| `edge_coordinates` | string | ❌ 可選 | 邊的特徵座標變數名 |

## 🔧 連線性變數

### 邊-節點連線性 (Edge-Node Connectivity)

**必須** 提供一個連線性變數，描述每條邊連線哪兩個節點：

```cdl
int Mesh1_edge_nodes(nMesh1_edge, 2) ;
  Mesh1_edge_nodes:cf_role = "edge_node_connectivity" ;
  Mesh1_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;
  Mesh1_edge_nodes:start_index = 0 ;  // 或 1，預設 0
```

這個變數是一個 **nEdges × 2** 的矩陣，每一行表示一條邊連線的兩個節點的索引。

### 示例資料

對於上面的簡單網路（4 個節點，3 條邊）：

**0-based 索引**：

```
Mesh1_edge_nodes = 
  0, 1,  // Edge 0: Node 0 -> Node 1
  1, 2,  // Edge 1: Node 1 -> Node 2
  2, 3;  // Edge 2: Node 2 -> Node 3
```

**1-based 索引**：

```
Mesh1_edge_nodes = 
  1, 2,  // Edge 0: Node 1 -> Node 2
  2, 3,  // Edge 1: Node 2 -> Node 3
  3, 4;  // Edge 2: Node 3 -> Node 4
```

## 📍 座標變數

### 節點座標 (Node Coordinates)

**必須** 提供節點的座標變數：

```cdl
double Mesh1_node_x(nMesh1_node) ;
  Mesh1_node_x:standard_name = "longitude" ;
  Mesh1_node_x:long_name = "Longitude of 1D network nodes." ;
  Mesh1_node_x:units = "degrees_east" ;

double Mesh1_node_y(nMesh1_node) ;
  Mesh1_node_y:standard_name = "latitude" ;
  Mesh1_node_y:long_name = "Latitude of 1D network nodes." ;
  Mesh1_node_y:units = "degrees_north" ;
```

對於 1D 網路，通常使用 **經緯度座標**，但也可以使用其他座標系（如投影座標）。

### 邊座標 (Edge Coordinates) - 可選

可以提供邊的特徵座標，通常定義在邊的中點：

```cdl
double Mesh1_edge_x(nMesh1_edge) ;
  Mesh1_edge_x:standard_name = "longitude" ;
  Mesh1_edge_x:long_name = "Characteristic longitude of 1D network edge (e.g. midpoint of the edge)." ;
  Mesh1_edge_x:units = "degrees_east" ;
  Mesh1_edge_x:bounds = "Mesh1_edge_xbnds" ;  // 可選的邊界

double Mesh1_edge_y(nMesh1_edge) ;
  Mesh1_edge_y:standard_name = "latitude" ;
  Mesh1_edge_y:long_name = "Characteristic latitude of 1D network edge (e.g. midpoint of the edge)." ;
  Mesh1_edge_y:units = "degrees_north" ;
  Mesh1_edge_y:bounds = "Mesh1_edge_ybnds" ;  // 可選的邊界
```

### 邊界變數 (Bounds Variables) - 可選

可以為邊座標提供邊界變數，定義邊的兩個端點座標：

```cdl
double Mesh1_edge_xbnds(nMesh1_edge, 2) ;
  Mesh1_edge_xbnds:standard_name = "longitude" ;
  Mesh1_edge_xbnds:long_name = "Longitude bounds of 1D network edge (i.e. begin and end longitude)." ;
  Mesh1_edge_xbnds:units = "degrees_east" ;

double Mesh1_edge_ybnds(nMesh1_edge, 2) ;
  Mesh1_edge_ybnds:standard_name = "latitude" ;
  Mesh1_edge_ybnds:long_name = "Latitude bounds of 1D network edge (i.e. begin and end latitude)." ;
  Mesh1_edge_ybnds:units = "degrees_north" ;
```

## 📄 完整示例

以下是一個完整的 1D 網路 UGRID 示例：

```cdl
// 檔案全域性屬性
:Conventions = "CF-1.12" ;  // CF v1.11+ 自動支援 UGRID
:title = "Example 1D River Network" ;
:institution = "Example Institute" ;
:source = "UGRID example" ;

// 維度定義
dimensions:
  nMesh1_node = 5 ;   // 5 個節點
  nMesh1_edge = 4 ;   // 4 條邊
  Two = 2 ;            // 每條邊連線 2 個節點

// 變數定義
variables:
  
  // 網格拓撲變數
  integer Mesh1 ;
    Mesh1:cf_role = "mesh_topology" ;
    Mesh1:long_name = "Topology data of 1D river network" ;
    Mesh1:topology_dimension = 1 ;
    Mesh1:node_coordinates = "Mesh1_node_x Mesh1_node_y" ;
    Mesh1:edge_node_connectivity = "Mesh1_edge_nodes" ;
    Mesh1:edge_coordinates = "Mesh1_edge_x Mesh1_edge_y" ;  // 可選
  
  // 連線性變數
  integer Mesh1_edge_nodes(nMesh1_edge, Two) ;
    Mesh1_edge_nodes:cf_role = "edge_node_connectivity" ;
    Mesh1_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;
    Mesh1_edge_nodes:start_index = 1 ;  // 使用 1-based 索引
  
  // 節點座標變數
  double Mesh1_node_x(nMesh1_node) ;
    Mesh1_node_x:standard_name = "longitude" ;
    Mesh1_node_x:long_name = "Longitude of 1D network nodes." ;
    Mesh1_node_x:units = "degrees_east" ;
    
  double Mesh1_node_y(nMesh1_node) ;
    Mesh1_node_y:standard_name = "latitude" ;
    Mesh1_node_y:long_name = "Latitude of 1D network nodes." ;
    Mesh1_node_y:units = "degrees_north" ;
  
  // 邊座標變數 (可選)
  double Mesh1_edge_x(nMesh1_edge) ;
    Mesh1_edge_x:standard_name = "longitude" ;
    Mesh1_edge_x:long_name = "Characteristic longitude of 1D network edge (e.g. midpoint of the edge)." ;
    Mesh1_edge_x:units = "degrees_east" ;
    Mesh1_edge_x:bounds = "Mesh1_edge_xbnds" ;
    
  double Mesh1_edge_y(nMesh1_edge) ;
    Mesh1_edge_y:standard_name = "latitude" ;
    Mesh1_edge_y:long_name = "Characteristic latitude of 1D network edge (e.g. midpoint of the edge)." ;
    Mesh1_edge_y:units = "degrees_north" ;
    Mesh1_edge_y:bounds = "Mesh1_edge_ybnds" ;
  
  // 邊界變數 (可選)
  double Mesh1_edge_xbnds(nMesh1_edge, Two) ;
    Mesh1_edge_xbnds:standard_name = "longitude" ;
    Mesh1_edge_xbnds:long_name = "Longitude bounds of 1D network edge (i.e. begin and end longitude)." ;
    Mesh1_edge_xbnds:units = "degrees_east" ;
    
  double Mesh1_edge_ybnds(nMesh1_edge, Two) ;
    Mesh1_edge_ybnds:standard_name = "latitude" ;
    Mesh1_edge_ybnds:long_name = "Latitude bounds of 1D network edge (i.e. begin and end latitude)." ;
    Mesh1_edge_ybnds:units = "degrees_north" ;

// 資料定義
data:
  
  // 網格拓撲資料
  Mesh1 = 0 ;  // 虛擬變數，值不重要
  
  // 連線性資料 (1-based 索引)
  Mesh1_edge_nodes = 
    1, 2,  // Edge 0: Node 1 -> Node 2
    2, 3,  // Edge 1: Node 2 -> Node 3
    3, 4,  // Edge 2: Node 3 -> Node 4
    4, 5;  // Edge 3: Node 4 -> Node 5
  
  // 節點座標資料
  Mesh1_node_x = 10.0, 10.1, 10.2, 10.3, 10.4 ;
  Mesh1_node_y = 40.0, 40.05, 40.1, 40.15, 40.2 ;
  
  // 邊座標資料 (中點)
  Mesh1_edge_x = 10.05, 10.15, 10.25, 10.35 ;
  Mesh1_edge_y = 40.025, 40.075, 40.125, 40.175 ;
  
  // 邊界資料
  Mesh1_edge_xbnds = 
    10.0, 10.1,
    10.1, 10.2,
    10.2, 10.3,
    10.3, 10.4 ;
    
  Mesh1_edge_ybnds = 
    40.0, 40.05,
    40.05, 40.1,
    40.1, 40.15,
    40.15, 40.2 ;
```

## 🎯 資料變數示例

在 1D 網路上可以定義各種資料變數：

### 節點資料 (Node Data)

```cdl
// 定義在節點上的資料
double Mesh1_node_elevation(nMesh1_node) ;
  Mesh1_node_elevation:standard_name = "height_above_mean_sea_level" ;
  Mesh1_node_elevation:units = "m" ;
  Mesh1_node_elevation:mesh = "Mesh1" ;
  Mesh1_node_elevation:location = "node" ;
  Mesh1_node_elevation:coordinates = "Mesh1_node_x Mesh1_node_y" ;
  Mesh1_node_elevation:long_name = "Elevation at network nodes" ;

// 資料
Mesh1_node_elevation = 10.5, 11.2, 9.8, 10.1, 12.0 ;
```

### 邊資料 (Edge Data)

```cdl
// 定義在邊上的資料
double Mesh1_edge_flow(nMesh1_edge) ;
  Mesh1_edge_flow:standard_name = "water_volume_flow_rate" ;
  Mesh1_edge_flow:units = "m3 s-1" ;
  Mesh1_edge_flow:mesh = "Mesh1" ;
  Mesh1_edge_flow:location = "edge" ;
  Mesh1_edge_flow:coordinates = "Mesh1_edge_x Mesh1_edge_y" ;
  Mesh1_edge_flow:long_name = "Water flow rate through edges" ;

// 資料
Mesh1_edge_flow = 5.0, 7.5, 6.0, 8.0 ;
```

### 帶時間維度的資料

```cdl
dimensions:
  time = 10 ;

variables:
  double time(time) ;
    time:standard_name = "time" ;
    time:units = "days since 2024-01-01" ;
    time:axis = "T" ;
  
  // 定義在節點上的時間序列資料
  double Mesh1_node_temperature(time, nMesh1_node) ;
    Mesh1_node_temperature:standard_name = "water_temperature" ;
    Mesh1_node_temperature:units = "K" ;
    Mesh1_node_temperature:mesh = "Mesh1" ;
    Mesh1_node_temperature:location = "node" ;
    Mesh1_node_temperature:coordinates = "Mesh1_node_x Mesh1_node_y" ;
    Mesh1_node_temperature:long_name = "Water temperature at network nodes" ;
```

## 📊 實際應用

### 河流網路應用

1D 網路拓撲特別適用於河流系統：

- **節點** 表示河流交匯點、入海口、水庫等
- **邊** 表示河流段
- **節點資料** 可以表示水位、沉積物濃度等
- **邊資料** 可以表示流量、流速等

### 管道網路應用

- **節點** 表示泵站、閥門、交匯點等
- **邊** 表示管道段
- **資料** 可以表示壓力、流量、溫度等

### 道路網路應用

- **節點** 表示交叉口、終點等
- **邊** 表示道路段
- **資料** 可以表示交通流量、速度限制等

## 🎯 最佳實踐

### 1. 連線性定義

- ✅ **必須** 提供 `edge_node_connectivity`
- ✅ 明確指定 `start_index` (0 或 1)
- ✅ 確保連線性資料與節點索引一致
- ❌ 避免使用不連續的節點索引

### 2. 座標系統

- ✅ 使用標準座標系 (經緯度或投影座標)
- ✅ 為座標變數提供 `standard_name` 和 `units`
- ✅ 考慮使用 `axis` 屬性 (X, Y)
- ❌ 避免使用未定義的座標系

### 3. 資料定義

- ✅ 為資料變數提供 `mesh` 和 `location` 屬性
- ✅ 使用 `coordinates` 屬性指向位置的座標
- ✅ 為資料變數提供適當的 `standard_name` 和 `units`
- ❌ 不要遺漏必需的位置屬性

### 4. 檔案結構

- ✅ 保持一致的變數命名
- ✅ 使用描述性的變數名
- ✅ 包含檔案級後設資料 (title, institution, source)
- ❌ 避免變數名衝突

## 🔗 相關文件

- [核心概念](../core-concepts.md) - UGRID 基礎概念
- [命名約定](naming-conventions.md) - 幾何元素命名
- [2D 三角形拓撲](2d-triangular.md) - 更復雜的 2D 拓撲
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/) - 官方 1D 網路定義

## 📚 參考資源

- [UGRID 1D Network Topology Official Documentation](https://ugrid-conventions.github.io/ugrid-conventions/#1d-network-topology)
- [CF Conventions Mesh Topology Variables](https://cfconventions.org/cf-conventions/cf-conventions.html#mesh-topology-variables)

---

*下一步*: [2D 三角形拓撲](2d-triangular.md) | [命名約定](naming-conventions.md)
