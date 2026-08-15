# UGRID 核心概念与术语定义

## 📖 概述

UGRID Conventions 建立在一组清晰定义的概念之上。理解这些核心概念是正确使用和实现 UGRID 的基础。本文档详细说明了 UGRID 中的所有关键术语和概念。

## 🏗️ 基础概念

### 1. 几何元素层次 (Geometric Elements Hierarchy)

UGRID 定义了一个四层的几何元素层次结构，用于描述网格的拓扑：

```
┌─────────────────────────────────────┐
│           3D - Volume (体积)            │
│   由多个面围成的三维空间区域           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           2D - Face (面)                │
│   由多个边围成的二维平面区域           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           1D - Edge (边)                │
│   由两个节点定义的线段                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│           0D - Node (节点/顶点)         │
│   基本几何元素，表示一个坐标点           │
└──────────────────────────────────────┘
```

### 2. 正式定义

| 维度 | 名称 | UGRID 定义 | 同义词 | 描述 |
|------|------|------------|--------|------|
| 0D | **Node** | 基本元素 | Vertex (顶点) | 坐标点，网格的最基本组成单元 |
| 1D | **Edge** | 线段 | Link (链接) | 连接两个节点的直线或曲线 |
| 2D | **Face** | 平面区域 | Polygon (多边形), Cell (单元) | 由边围成的封闭区域 |
| 3D | **Volume** | 体积 | Cell (单元) | 由面围成的三维空间 |

⚠️ **重要说明**：
- **Vertex** 这个术语在 UGRID 中已经被 **Node** 取代，以保持一致性
- **Cell** 在社区中有时用于描述 2D 元素，但 UGRID 官方使用 **Face** 来避免混淆
- **Volume** 而不是 Cell 用于描述 3D 元素

## 🎯 网格拓扑 (Mesh Topology)

### 1. 定义

**网格拓扑 (Mesh Topology)** 指的是网格中各种几何元素之间的互连关系。这是 UGRID 的核心概念，描述了网格的结构和连接性。

> "Inspired by Wikipedia's definition of network topology, we define the mesh topology here as the interconnection of various geometrical elements of the mesh."

### 2. 组成部分

网格拓扑由以下部分组成：

1. **几何元素**: Nodes, Edges, Faces, Volumes
2. **连接性**: 元素之间的连接关系
3. **属性**: 描述拓扑特性的元数据

### 3. 表示方式

UGRID 使用 **网格拓扑变量 (Mesh Topology Variable)** 来存储拓扑信息：

```cdl
integer Mesh2 ;
  Mesh2:cf_role = "mesh_topology" ;
  Mesh2:long_name = "Topology data of 2D unstructured mesh" ;
  Mesh2:topology_dimension = 2 ;
  Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
  Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
```

## 🔗 连接性 (Connectivity)

### 1. 定义

**连接性 (Connectivity)** 描述了网格中不同几何元素之间的连接关系。UGRID 使用 **连接性变量 (Connectivity Variables)** 来存储这些关系。

### 2. 连接性变量类型

UGRID 定义了多种连接性变量：

#### 节点连接性 (Node Connectivity)
- `edge_node_connectivity`: 边到节点的映射
- `face_node_connectivity`: 面到节点的映射
- `volume_node_connectivity`: 体积到节点的映射

#### 边连接性 (Edge Connectivity)
- `face_edge_connectivity`: 面到边的映射
- `volume_edge_connectivity`: 体积到边的映射

#### 面连接性 (Face Connectivity)
- `volume_face_connectivity`: 体积到面的映射

#### 相邻连接性 (Adjacency Connectivity)
- `face_face_connectivity`: 面到相邻面的映射
- `edge_face_connectivity`: 边到相邻面的映射
- `volume_volume_connectivity`: 体积到相邻体积的映射

### 3. 连接性变量的属性

所有连接性变量都有：
- `cf_role`: 变量的角色 (如 `edge_node_connectivity`)
- `long_name`: 描述性名称
- `start_index`: 索引起始值 (0 或 1)
- `_FillValue`: 缺失值标记

### 4. 索引约定

UGRID 支持两种索引方式：

#### 0-based 索引 (默认)
```cdl
int mesh_face_nodes(nMesh_face, nMaxNodesPerFace) ;
  mesh_face_nodes:start_index = 0 ;  // 可以省略，0 是默认值
```

#### 1-based 索引
```cdl
int mesh_face_nodes(nMesh_face, nMaxNodesPerFace) ;
  mesh_face_nodes:start_index = 1 ;
```

✅ **最佳实践**: 建议使用 0-based 索引，因为这与 CF 的压缩约定一致。

## 📍 坐标系统 (Coordinate Systems)

### 1. 节点坐标 (Node Coordinates)

UGRID 使用 **辅助坐标变量 (Auxiliary Coordinate Variables)** 来描述节点的空间位置：

```cdl
double Mesh2_node_x(nMesh2_node) ;
  Mesh2_node_x:standard_name = "longitude" ;
  Mesh2_node_x:long_name = "Longitude of 2D mesh nodes." ;
  Mesh2_node_x:units = "degrees_east" ;

double Mesh2_node_y(nMesh2_node) ;
  Mesh2_node_y:standard_name = "latitude" ;
  Mesh2_node_y:long_name = "Latitude of 2D mesh nodes." ;
  Mesh2_node_y:units = "degrees_north" ;
```

### 2. 特征坐标 (Characteristic Coordinates)

除了节点坐标，UGRID 还支持定义边、面、体积的特征坐标：

- **边坐标**: 通常定义在边的中点
- **面坐标**: 通常定义在面的几何中心 (如外接圆圆心)
- **体积坐标**: 通常定义在体积的几何中心

```cdl
double Mesh2_edge_x(nMesh2_edge) ;
  Mesh2_edge_x:standard_name = "longitude" ;
  Mesh2_edge_x:long_name = "Characteristic longitude of 2D mesh edge (e.g. midpoint of the edge)." ;

double Mesh2_face_x(nMesh2_face) ;
  Mesh2_face_x:standard_name = "longitude" ;
  Mesh2_face_x:long_name = "Characteristics longitude of 2D mesh face (e.g. circumcenter coordinate)." ;
```

### 3. 坐标边界 (Coordinate Bounds)

UGRID 支持使用 `bounds` 属性来定义坐标的边界：

```cdl
double Mesh2_face_x(nMesh2_face) ;
  Mesh2_face_x:bounds = "Mesh2_face_xbnds" ;

double Mesh2_face_xbnds(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_xbnds:long_name = "Longitude bounds of 2D mesh face" ;
```

## 🎯 数据位置 (Data Location)

### 1. 定义

**数据位置 (Data Location)** 描述了数据变量在网格中的定义位置。UGRID 支持在不同几何元素上定义数据。

### 2. 位置类型

UGRID 定义了以下位置类型：

| 位置类型 | 描述 | 使用场景 |
|----------|------|----------|
| `node` | 数据定义在节点上 | 点数据，节点值 |
| `edge` | 数据定义在边上 | 通量数据，边值 |
| `face` | 数据定义在面上 | 单元数据，面值 |
| `volume` | 数据定义在体积上 | 3D 单元数据 |

### 3. 位置属性

数据变量使用以下属性来指定位置：

- `mesh`: 指向关联的网格拓扑变量
- `location`: 指定数据位置类型 (node, edge, face, volume)
- `coordinates`: 指向位置的坐标变量

```cdl
double Mesh2_waterlevel(time, nMesh2_face) ;
  Mesh2_waterlevel:standard_name = "sea_surface_height_above_geoid" ;
  Mesh2_waterlevel:units = "m" ;
  Mesh2_waterlevel:mesh = "Mesh2" ;      // 关联到网格拓扑
  Mesh2_waterlevel:location = "face" ;   // 数据定义在面上
  Mesh2_waterlevel:coordinates = "Mesh2_face_x Mesh2_face_y" ;
```

## 📊 网格类型 (Mesh Types)

UGRID 支持多种网格类型：

### 1. 1D 网络 (1D Network)
- **拓扑维度**: 1
- **几何元素**: Nodes, Edges
- **应用场景**: 河流、管道、一维网络
- **示例**: [1D Network Topology](../topology/1d-network.md)

### 2. 2D 三角形网格 (2D Triangular Mesh)
- **拓扑维度**: 2
- **几何元素**: Nodes, Edges, Faces (三角形)
- **应用场景**: 海洋模型、水文模型
- **示例**: [2D Triangular Topology](../topology/2d-triangular.md)

### 3. 2D 灵活网格 (2D Flexible Mesh)
- **拓扑维度**: 2
- **几何元素**: Nodes, Edges, Faces (混合形状)
- **特点**: 支持三角形、四边形等混合面类型
- **示例**: [2D Flexible Mesh Topology](../topology/2d-flexible.md)

### 4. 3D 分层网格 (3D Layered Mesh)
- **拓扑维度**: 2 (水平) + 垂直坐标
- **几何元素**: Nodes, Edges, Faces (2D) + Layers
- **特点**: 2D 水平网格 + 垂直方向分层
- **示例**: [3D Layered Topology](../topology/3d-layered.md)

### 5. 3D 完全非结构化网格 (3D Fully Unstructured Mesh)
- **拓扑维度**: 3
- **几何元素**: Nodes, Edges, Faces, Volumes
- **特点**: 完全三维的非结构化网格
- **示例**: [3D Unstructured Topology](../topology/3d-unstructured.md)

## 🔧 体积与通量变量 (Volume and Flux Variables)

UGRID 认识到相同的网格几何可以用于不同的数值方案：

### 1. 有限体积法 (Finite Volume)
- **体积**: 定义在面 (2D) 或体积 (3D) 上
- **通量**: 定义在边上，表示**跨越**边的通量
- **特点**: 体积围绕面，通量跨越边

### 2. 连续 Galerkin 有限元法
- **体积**: 定义在节点上
- **通量**: 定义在边上，表示**沿着**边的通量
- **特点**: 体积围绕节点，通量沿着边

## 📋 属性定义 (Attribute Definitions)

### 1. 标准化属性 (Standardized Attributes)

UGRID 定义了以下标准化属性：

#### 网格拓扑属性
| 属性 | 类型 | 必需性 | 描述 |
|------|------|--------|------|
| `cf_role` | string | 必需 | 变量的角色，如 `mesh_topology` |
| `topology_dimension` | int | 必需 | 网格的最高维度 (1, 2, 3) |
| `node_coordinates` | string | 必需 | 空格分隔的节点坐标变量名列表 |
| `edge_node_connectivity` | string | 可选 | 边-节点连接性变量名 |
| `face_node_connectivity` | string | 条件必需 | 面-节点连接性变量名 |
| `volume_node_connectivity` | string | 条件必需 | 体积-节点连接性变量名 |
| `edge_dimension` | string | 可选 | 边的维度名 |
| `face_dimension` | string | 可选 | 面的维度名 |
| `volume_dimension` | string | 可选 | 体积的维度名 |

#### 连接性属性
| 属性 | 类型 | 必需性 | 描述 |
|------|------|--------|------|
| `cf_role` | string | 必需 | 连接性变量的角色 |
| `start_index` | int | 可选 | 索引起始值 (0 或 1)，默认 0 |
| `_FillValue` | same as var | 可选 | 缺失值标记 |

#### 数据位置属性
| 属性 | 类型 | 必需性 | 描述 |
|------|------|--------|------|
| `mesh` | string | 必需 | 关联的网格拓扑变量名 |
| `location` | string | 必需 | 数据位置 (node, edge, face, volume) |
| `coordinates` | string | 可选 | 空格分隔的坐标变量名列表 |
| `location_index_set` | string | 可选 | 位置索引集变量名 |

### 2. cf_role 值

UGRID 定义了以下 `cf_role` 值：

#### 网格拓扑角色
- `mesh_topology`: 网格拓扑变量

#### 连接性角色
- `edge_node_connectivity`: 边-节点连接性
- `face_node_connectivity`: 面-节点连接性
- `volume_node_connectivity`: 体积-节点连接性
- `face_edge_connectivity`: 面-边连接性
- `face_face_connectivity`: 面-面连接性
- `edge_face_connectivity`: 边-面连接性
- `volume_face_connectivity`: 体积-面连接性
- `volume_edge_connectivity`: 体积-边连接性
- `boundary_node_connectivity`: 边界-节点连接性
- `volume_shape_type`: 体积形状类型

#### 特殊角色
- `location_index_set`: 位置索引集

### 3. 体积形状类型 (Volume Shape Types)

UGRID 定义了以下体积形状类型：

| 标记值 | 形状名称 | 节点数 | 描述 |
|--------|----------|--------|------|
| 0 | tetrahedron | 4 | 四面体 |
| 1 | pyramid | 5 | 金字塔 (方形底) |
| 2 | wedge | 6 | 棱柱 (三角形底) |
| 3 | hexahedron | 8 | 六面体 (扭曲的立方体) |

## 🎯 最佳实践

### 1. 命名约定
- ✅ 使用描述性的变量名 (如 `Mesh2_face_nodes`)
- ✅ 保持一致的前缀 (如所有 2D 网格变量以 `Mesh2_` 开头)
- ❌ 避免使用保留字 (如 `node`, `edge`, `face` 作为变量名)

### 2. 属性使用
- ✅ 总是定义 `cf_role` 属性
- ✅ 总是定义 `long_name` 属性
- ✅ 使用标准名称 (standard_name) 当适用时
- ✅ 使用 `start_index` 明确索引方式

### 3. 连接性变量
- ✅ 使用 `_FillValue` 处理变长数组
- ✅ 保持连接性变量与拓扑一致
- ✅ 使用 0-based 索引 (推荐)

### 4. 数据变量
- ✅ 总是定义 `mesh` 和 `location` 属性
- ✅ 使用 `coordinates` 属性指向位置坐标
- ✅ 确保数据维度与位置一致

---

*下一步*: [命名约定](topology/naming-conventions.md) | [1D 网络拓扑](topology/1d-network.md)
