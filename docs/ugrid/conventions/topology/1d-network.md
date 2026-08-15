# 1D 网络拓扑 (1D Network Topology)

## 📖 概述

**1D 网络拓扑** 用于描述 **一维的线性网络结构**，例如：
- 河流系统
- 管道网络
- 道路网络
- 电力线路
- 其他一维连接结构

这是 UGRID 中最简单的拓扑类型，只包含 **节点 (Nodes)** 和 **边 (Edges)** 两种几何元素。

## 🏗️ 基本结构

1D 网络由以下组件组成：

```
Node 0 ●────────● Node 1
          Edge 0
          
Node 1 ●────────● Node 2
          Edge 1
          
Node 2 ●────────● Node 3
          Edge 2
```

### 几何元素

| 元素 | 维度 | 描述 | 数量 |
|------|------|------|------|
| Node | 0D | 网络中的点 | nNodes |
| Edge | 1D | 连接两个节点的线段 | nEdges |

## 📋 必需属性

### 网格拓扑变量属性

1D 网络的网格拓扑变量 **必须** 包含以下属性：

| 属性 | 类型 | 必需性 | 描述 |
|------|------|--------|------|
| `cf_role` | string | ✅ 必需 | 必须为 `"mesh_topology"` |
| `topology_dimension` | int | ✅ 必需 | 必须为 `1` |
| `node_coordinates` | string | ✅ 必需 | 节点坐标变量名 (空格分隔) |
| `edge_node_connectivity` | string | ✅ 必需 | 边-节点连接性变量名 |

### 可选属性

| 属性 | 类型 | 必需性 | 描述 |
|------|------|--------|------|
| `long_name` | string | ❌ 可选 | 描述性名称 |
| `edge_coordinates` | string | ❌ 可选 | 边的特征坐标变量名 |

## 🔧 连接性变量

### 边-节点连接性 (Edge-Node Connectivity)

**必须** 提供一个连接性变量，描述每条边连接哪两个节点：

```cdl
int Mesh1_edge_nodes(nMesh1_edge, 2) ;
  Mesh1_edge_nodes:cf_role = "edge_node_connectivity" ;
  Mesh1_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;
  Mesh1_edge_nodes:start_index = 0 ;  // 或 1，默认 0
```

这个变量是一个 **nEdges × 2** 的矩阵，每一行表示一条边连接的两个节点的索引。

### 示例数据

对于上面的简单网络（4 个节点，3 条边）：

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

## 📍 坐标变量

### 节点坐标 (Node Coordinates)

**必须** 提供节点的坐标变量：

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

对于 1D 网络，通常使用 **经纬度坐标**，但也可以使用其他坐标系（如投影坐标）。

### 边坐标 (Edge Coordinates) - 可选

可以提供边的特征坐标，通常定义在边的中点：

```cdl
double Mesh1_edge_x(nMesh1_edge) ;
  Mesh1_edge_x:standard_name = "longitude" ;
  Mesh1_edge_x:long_name = "Characteristic longitude of 1D network edge (e.g. midpoint of the edge)." ;
  Mesh1_edge_x:units = "degrees_east" ;
  Mesh1_edge_x:bounds = "Mesh1_edge_xbnds" ;  // 可选的边界

double Mesh1_edge_y(nMesh1_edge) ;
  Mesh1_edge_y:standard_name = "latitude" ;
  Mesh1_edge_y:long_name = "Characteristic latitude of 1D network edge (e.g. midpoint of the edge)." ;
  Mesh1_edge_y:units = "degrees_north" ;
  Mesh1_edge_y:bounds = "Mesh1_edge_ybnds" ;  // 可选的边界
```

### 边界变量 (Bounds Variables) - 可选

可以为边坐标提供边界变量，定义边的两个端点坐标：

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

以下是一个完整的 1D 网络 UGRID 示例：

```cdl
// 文件全局属性
:Conventions = "CF-1.12" ;  // CF v1.11+ 自动支持 UGRID
:title = "Example 1D River Network" ;
:institution = "Example Institute" ;
:source = "UGRID example" ;

// 维度定义
dimensions:
  nMesh1_node = 5 ;   // 5 个节点
  nMesh1_edge = 4 ;   // 4 条边
  Two = 2 ;            // 每条边连接 2 个节点

// 变量定义
variables:
  
  // 网格拓扑变量
  integer Mesh1 ;
    Mesh1:cf_role = "mesh_topology" ;
    Mesh1:long_name = "Topology data of 1D river network" ;
    Mesh1:topology_dimension = 1 ;
    Mesh1:node_coordinates = "Mesh1_node_x Mesh1_node_y" ;
    Mesh1:edge_node_connectivity = "Mesh1_edge_nodes" ;
    Mesh1:edge_coordinates = "Mesh1_edge_x Mesh1_edge_y" ;  // 可选
  
  // 连接性变量
  integer Mesh1_edge_nodes(nMesh1_edge, Two) ;
    Mesh1_edge_nodes:cf_role = "edge_node_connectivity" ;
    Mesh1_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;
    Mesh1_edge_nodes:start_index = 1 ;  // 使用 1-based 索引
  
  // 节点坐标变量
  double Mesh1_node_x(nMesh1_node) ;
    Mesh1_node_x:standard_name = "longitude" ;
    Mesh1_node_x:long_name = "Longitude of 1D network nodes." ;
    Mesh1_node_x:units = "degrees_east" ;
    
  double Mesh1_node_y(nMesh1_node) ;
    Mesh1_node_y:standard_name = "latitude" ;
    Mesh1_node_y:long_name = "Latitude of 1D network nodes." ;
    Mesh1_node_y:units = "degrees_north" ;
  
  // 边坐标变量 (可选)
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
  
  // 边界变量 (可选)
  double Mesh1_edge_xbnds(nMesh1_edge, Two) ;
    Mesh1_edge_xbnds:standard_name = "longitude" ;
    Mesh1_edge_xbnds:long_name = "Longitude bounds of 1D network edge (i.e. begin and end longitude)." ;
    Mesh1_edge_xbnds:units = "degrees_east" ;
    
  double Mesh1_edge_ybnds(nMesh1_edge, Two) ;
    Mesh1_edge_ybnds:standard_name = "latitude" ;
    Mesh1_edge_ybnds:long_name = "Latitude bounds of 1D network edge (i.e. begin and end latitude)." ;
    Mesh1_edge_ybnds:units = "degrees_north" ;

// 数据定义
data:
  
  // 网格拓扑数据
  Mesh1 = 0 ;  // 虚拟变量，值不重要
  
  // 连接性数据 (1-based 索引)
  Mesh1_edge_nodes = 
    1, 2,  // Edge 0: Node 1 -> Node 2
    2, 3,  // Edge 1: Node 2 -> Node 3
    3, 4,  // Edge 2: Node 3 -> Node 4
    4, 5;  // Edge 3: Node 4 -> Node 5
  
  // 节点坐标数据
  Mesh1_node_x = 10.0, 10.1, 10.2, 10.3, 10.4 ;
  Mesh1_node_y = 40.0, 40.05, 40.1, 40.15, 40.2 ;
  
  // 边坐标数据 (中点)
  Mesh1_edge_x = 10.05, 10.15, 10.25, 10.35 ;
  Mesh1_edge_y = 40.025, 40.075, 40.125, 40.175 ;
  
  // 边界数据
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

## 🎯 数据变量示例

在 1D 网络上可以定义各种数据变量：

### 节点数据 (Node Data)

```cdl
// 定义在节点上的数据
double Mesh1_node_elevation(nMesh1_node) ;
  Mesh1_node_elevation:standard_name = "height_above_mean_sea_level" ;
  Mesh1_node_elevation:units = "m" ;
  Mesh1_node_elevation:mesh = "Mesh1" ;
  Mesh1_node_elevation:location = "node" ;
  Mesh1_node_elevation:coordinates = "Mesh1_node_x Mesh1_node_y" ;
  Mesh1_node_elevation:long_name = "Elevation at network nodes" ;

// 数据
Mesh1_node_elevation = 10.5, 11.2, 9.8, 10.1, 12.0 ;
```

### 边数据 (Edge Data)

```cdl
// 定义在边上的数据
double Mesh1_edge_flow(nMesh1_edge) ;
  Mesh1_edge_flow:standard_name = "water_volume_flow_rate" ;
  Mesh1_edge_flow:units = "m3 s-1" ;
  Mesh1_edge_flow:mesh = "Mesh1" ;
  Mesh1_edge_flow:location = "edge" ;
  Mesh1_edge_flow:coordinates = "Mesh1_edge_x Mesh1_edge_y" ;
  Mesh1_edge_flow:long_name = "Water flow rate through edges" ;

// 数据
Mesh1_edge_flow = 5.0, 7.5, 6.0, 8.0 ;
```

### 带时间维度的数据

```cdl
dimensions:
  time = 10 ;

variables:
  double time(time) ;
    time:standard_name = "time" ;
    time:units = "days since 2024-01-01" ;
    time:axis = "T" ;
  
  // 定义在节点上的时间序列数据
  double Mesh1_node_temperature(time, nMesh1_node) ;
    Mesh1_node_temperature:standard_name = "water_temperature" ;
    Mesh1_node_temperature:units = "K" ;
    Mesh1_node_temperature:mesh = "Mesh1" ;
    Mesh1_node_temperature:location = "node" ;
    Mesh1_node_temperature:coordinates = "Mesh1_node_x Mesh1_node_y" ;
    Mesh1_node_temperature:long_name = "Water temperature at network nodes" ;
```

## 📊 实际应用

### 河流网络应用

1D 网络拓扑特别适用于河流系统：

- **节点** 表示河流交汇点、入海口、水库等
- **边** 表示河流段
- **节点数据** 可以表示水位、沉积物浓度等
- **边数据** 可以表示流量、流速等

### 管道网络应用

- **节点** 表示泵站、阀门、交汇点等
- **边** 表示管道段
- **数据** 可以表示压力、流量、温度等

### 道路网络应用

- **节点** 表示交叉口、终点等
- **边** 表示道路段
- **数据** 可以表示交通流量、速度限制等

## 🎯 最佳实践

### 1. 连接性定义
- ✅ **必须** 提供 `edge_node_connectivity`
- ✅ 明确指定 `start_index` (0 或 1)
- ✅ 确保连接性数据与节点索引一致
- ❌ 避免使用不连续的节点索引

### 2. 坐标系统
- ✅ 使用标准坐标系 (经纬度或投影坐标)
- ✅ 为坐标变量提供 `standard_name` 和 `units`
- ✅ 考虑使用 `axis` 属性 (X, Y)
- ❌ 避免使用未定义的坐标系

### 3. 数据定义
- ✅ 为数据变量提供 `mesh` 和 `location` 属性
- ✅ 使用 `coordinates` 属性指向位置的坐标
- ✅ 为数据变量提供适当的 `standard_name` 和 `units`
- ❌ 不要遗漏必需的位置属性

### 4. 文件结构
- ✅ 保持一致的变量命名
- ✅ 使用描述性的变量名
- ✅ 包含文件级元数据 (title, institution, source)
- ❌ 避免变量名冲突

## 🔗 相关文档

- [核心概念](../core-concepts.md) - UGRID 基础概念
- [命名约定](naming-conventions.md) - 几何元素命名
- [2D 三角形拓扑](2d-triangular.md) - 更复杂的 2D 拓扑
- [UGRID 官方文档](https://ugrid-conventions.github.io/ugrid-conventions/) - 官方 1D 网络定义

## 📚 参考资源

- [UGRID 1D Network Topology Official Documentation](https://ugrid-conventions.github.io/ugrid-conventions/#1d-network-topology)
- [CF Conventions Mesh Topology Variables](https://cfconventions.org/cf-conventions/cf-conventions.html#mesh-topology-variables)

---

*下一步*: [2D 三角形拓扑](2d-triangular.md) | [命名约定](naming-conventions.md)
