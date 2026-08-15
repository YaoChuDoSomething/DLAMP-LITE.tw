# 几何元素命名约定 (Naming Conventions for Geometrical Elements)

## 📖 概述

UGRID Conventions 为网格中的几何元素定义了标准化的命名约定。这些命名在网格拓扑定义中至关重要，确保了不同系统之间的一致性和互操作性。

## 🎯 官方命名约定

### 几何元素标准名称

UGRID 官方采用以下标准名称来描述不同维度的几何元素：

| 维度 | 标准名称 | 定义 | 注解 |
|------|----------|------|------|
| 0D | **Node** | A point, a coordinate pair or triplet: the most basic element of the topology. | "node" 似乎比 "vertex" 更常用 |
| 1D | **Edge** | A line or curve bounded by two nodes. |  |
| 2D | **Face** | A plane or surface enclosed by a set of edges. | 在 2D 水平应用中也可以考虑 "polygon"，但 "face" 在元素层次中最常见 |
| 3D | **Volume** | A volume enclosed by a set of faces. | 备选词 "cell" 被考虑过，但 "cell" 经常在社区中用来描述二维结构 |

### 命名历史

在 UGRID 的早期开发阶段，社区对几何元素的命名进行了广泛的讨论：

1. **Node vs Vertex**
   - "Vertex" (顶点) 在几何学中是常用术语
   - "Node" (节点) 在有限元和网络分析中更常用
   - **决定**: 采用 "Node" 作为标准名称

2. **Face vs Polygon vs Cell**
   - "Polygon" 在 2D 几何中很直观
   - "Cell" 在 CF 社区中常用于描述网格单元
   - "Face" 在拓扑层次中更一致
   - **决定**: 采用 "Face" 作为标准名称

3. **Volume vs Cell (3D)**
   - "Cell" 可以用于描述 3D 单元
   - "Volume" 更准确地描述了 3D 几何实体
   - **决定**: 采用 "Volume" 作为标准名称

⚠️ **重要说明**:
> In favor of simpler code for interpreting compliant files, we have dropped to use of the `locations` attribute which allowed the user to specify his/her own names for nodes, edges, faces and volumes.

这意味着 **不再允许用户自定义几何元素的名称**，必须使用上述标准名称。

## 🔧 实际应用中的命名

### 1. 网格拓扑变量命名

虽然几何元素有标准名称，但 **网格拓扑变量本身** 可以有不同的命名方式：

#### 推荐的命名模式

```cdl
// 方式 1: 使用 Mesh + 维度 + 编号
integer Mesh1 ;  // 1D 网格
integer Mesh2 ;  // 2D 网格
integer Mesh3D ; // 3D 网格

// 方式 2: 使用描述性名称
integer river_network ;  // 河流网络
integer ocean_mesh ;      // 海洋网格
integer atmospheric_mesh ; // 大气网格
```

✅ **最佳实践**: 使用一致的、描述性的名称，并包含网格的维度信息。

### 2. 坐标变量命名

坐标变量通常遵循以下命名模式：

```cdl
// 标准模式: <MeshPrefix>_<Element>_<Coord>
// 1D 网格示例
int Mesh1 ;
  Mesh1:cf_role = "mesh_topology" ;
  Mesh1:node_coordinates = "Mesh1_node_x Mesh1_node_y" ;

double Mesh1_node_x(nMesh1_node) ;
double Mesh1_node_y(nMesh1_node) ;

// 2D 网格示例
int Mesh2 ;
  Mesh2:cf_role = "mesh_topology" ;
  Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y Mesh2_node_z" ;

double Mesh2_node_x(nMesh2_node) ;
double Mesh2_node_y(nMesh2_node) ;
double Mesh2_node_z(nMesh2_node) ;  // 可选的高程坐标
```

### 3. 连接性变量命名

连接性变量通常遵循以下命名模式：

```cdl
// 标准模式: <MeshPrefix>_<FromElement>_<ToElement>
// 2D 网格示例
int Mesh2 ;
  Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
  Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;

int Mesh2_face_nodes(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_nodes:cf_role = "face_node_connectivity" ;

int Mesh2_edge_nodes(nMesh2_edge, 2) ;
  Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
```

### 4. 特征坐标变量命名

特征坐标变量（定义在几何元素上的坐标）通常遵循：

```cdl
// 标准模式: <MeshPrefix>_<Element>_<Coord>
// 2D 网格示例
double Mesh2_face_x(nMesh2_face) ;
  Mesh2_face_x:long_name = "Characteristic longitude of mesh face" ;

double Mesh2_face_y(nMesh2_face) ;
  Mesh2_face_y:long_name = "Characteristic latitude of mesh face" ;

double Mesh2_edge_x(nMesh2_edge) ;
double Mesh2_edge_y(nMesh2_edge) ;
```

## 📋 维度命名

UGRID 对维度命名没有严格的要求，但推荐以下约定：

```cdl
// 标准模式: n<MeshPrefix>_<Element>
dimensions:
  nMesh1_node = 100 ;   // 1D 网格的节点数
  nMesh1_edge = 99 ;    // 1D 网格的边数
  
  nMesh2_node = 500 ;   // 2D 网格的节点数
  nMesh2_edge = 800 ;   // 2D 网格的边数
  nMesh2_face = 300 ;   // 2D 网格的面数
  nMaxMesh2_face_nodes = 4 ; // 2D 网格每个面的最大节点数
  
  nMesh3D_node = 2000 ;  // 3D 网格的节点数
  nMesh3D_edge = 4000 ;  // 3D 网格的边数
  nMesh3D_face = 3000 ;  // 3D 网格的面数
  nMesh3D_vol = 1000 ;   // 3D 网格的体积数
```

✅ **最佳实践**: 
- 使用 `n` 前缀表示计数
- 包含网格前缀和元素类型
- 对于可变长度的连接性，使用 `nMax*` 表示最大值

## 🎯 cf_role 属性值

UGRID 定义了标准化的 `cf_role` 属性值，用于标识变量的角色：

### 网格拓扑角色
| cf_role 值 | 描述 | 变量类型 |
|------------|------|----------|
| `mesh_topology` | 网格拓扑变量 | integer |

### 连接性角色
| cf_role 值 | 描述 | 变量类型 |
|------------|------|----------|
| `edge_node_connectivity` | 边-节点连接性 | integer |
| `face_node_connectivity` | 面-节点连接性 | integer |
| `volume_node_connectivity` | 体积-节点连接性 | integer |
| `face_edge_connectivity` | 面-边连接性 | integer |
| `face_face_connectivity` | 面-面连接性 | integer |
| `edge_face_connectivity` | 边-面连接性 | integer |
| `volume_face_connectivity` | 体积-面连接性 | integer |
| `volume_edge_connectivity` | 体积-边连接性 | integer |
| `boundary_node_connectivity` | 边界-节点连接性 | integer |
| `volume_shape_type` | 体积形状类型 | integer |

### 特殊角色
| cf_role 值 | 描述 | 变量类型 |
|------------|------|----------|
| `location_index_set` | 位置索引集 | integer |

## 📊 体积形状类型 (Volume Shape Types)

对于 3D 网格中的体积元素，UGRID 定义了标准的形状类型：

### 标准形状类型
| 标记值 | 形状名称 | 节点数 | 描述 | VTK 对应类型 |
|--------|----------|--------|------|----------------|
| 0 | tetrahedron | 4 | 四面体 | VTK_TETRA |
| 1 | pyramid | 5 | 金字塔 (方形底) | VTK_PYRAMID |
| 2 | wedge | 6 | 棱柱 (三角形底) | VTK_WEDGE |
| 3 | hexahedron | 8 | 六面体 (扭曲的立方体) | VTK_HEXAHEDRON |

### 形状类型定义

```cdl
int Mesh3D_vol_types(nMesh3D_vol) ;
  Mesh3D_vol_types:cf_role = "volume_shape_type" ;
  Mesh3D_vol_types:long_name = "Specifies the shape of the individual volumes." ;
  Mesh3D_vol_types:flag_values = 0, 1, 2, 3 ;
  Mesh3D_vol_types:flag_meanings = "tetrahedron pyramid wedge hexahedron" ;
```

## ✅ 命名最佳实践

### 1. 保持一致性
- ✅ 在同一个 NetCDF 文件中使用一致的命名前缀
- ✅ 所有相关的变量使用相同的网格前缀
- ❌ 避免混合使用不同的命名风格

### 2. 使用描述性名称
- ✅ 使用有意义的变量名 (如 `Mesh2_face_nodes`)
- ✅ 包含元素类型信息 (node, edge, face, volume)
- ❌ 避免使用模糊的名称 (如 `var1`, `data`)

### 3. 包含维度信息
- ✅ 在变量名中包含维度信息 (2D, 3D)
- ✅ 使用 `nMax*` 表示最大值
- ❌ 避免让用户猜测变量的维度

### 4. 遵循标准约定
- ✅ 使用 UGRID 定义的标准几何元素名称
- ✅ 使用 UGRID 定义的标准 cf_role 值
- ✅ 使用 UGRID 定义的标准体积形状类型
- ❌ 避免使用自定义的元素名称

### 5. 考虑兼容性
- ✅ 使用常见的、广泛接受的命名方式
- ✅ 考虑现有工具的命名约定
- ❌ 避免使用可能引起混淆的名称

## 🔍 命名示例

### 1D 网络示例

```cdl
dimensions:
  nMesh1_node = 5 ;   // 5 个节点
  nMesh1_edge = 4 ;   // 4 条边
  Two = 2 ;            // 每条边连接 2 个节点

variables:
  // 网格拓扑变量
  integer Mesh1 ;
    Mesh1:cf_role = "mesh_topology" ;
    Mesh1:long_name = "Topology data of 1D network" ;
    Mesh1:topology_dimension = 1 ;
    Mesh1:node_coordinates = "Mesh1_node_x Mesh1_node_y" ;
    Mesh1:edge_node_connectivity = "Mesh1_edge_nodes" ;

  // 连接性变量
  integer Mesh1_edge_nodes(nMesh1_edge, Two) ;
    Mesh1_edge_nodes:cf_role = "edge_node_connectivity" ;
    Mesh1_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;

  // 坐标变量
  double Mesh1_node_x(nMesh1_node) ;
    Mesh1_node_x:standard_name = "longitude" ;
    Mesh1_node_x:long_name = "Longitude of 1D network nodes." ;
    Mesh1_node_x:units = "degrees_east" ;

  double Mesh1_node_y(nMesh1_node) ;
    Mesh1_node_y:standard_name = "latitude" ;
    Mesh1_node_y:long_name = "Latitude of 1D network nodes." ;
    Mesh1_node_y:units = "degrees_north" ;
```

### 2D 三角形网格示例

```cdl
dimensions:
  nMesh2_node = 4 ;    // 4 个节点
  nMesh2_edge = 5 ;    // 5 条边
  nMesh2_face = 2 ;    // 2 个面 (三角形)
  Three = 3 ;          // 每个三角形有 3 个节点

variables:
  // 网格拓扑变量
  integer Mesh2 ;
    Mesh2:cf_role = "mesh_topology" ;
    Mesh2:long_name = "Topology data of 2D triangular mesh" ;
    Mesh2:topology_dimension = 2 ;
    Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;
    Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;
    Mesh2:edge_node_connectivity = "Mesh2_edge_nodes" ;

  // 连接性变量
  integer Mesh2_face_nodes(nMesh2_face, Three) ;
    Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
    Mesh2_face_nodes:long_name = "Maps every triangular face to its three corner nodes." ;

  integer Mesh2_edge_nodes(nMesh2_edge, 2) ;
    Mesh2_edge_nodes:cf_role = "edge_node_connectivity" ;
    Mesh2_edge_nodes:long_name = "Maps every edge to the two nodes that it connects." ;

  // 坐标变量
  double Mesh2_node_x(nMesh2_node) ;
    Mesh2_node_x:standard_name = "longitude" ;
    Mesh2_node_x:long_name = "Longitude of 2D mesh nodes." ;

  double Mesh2_node_y(nMesh2_node) ;
    Mesh2_node_y:standard_name = "latitude" ;
    Mesh2_node_y:long_name = "Latitude of 2D mesh nodes." ;
```

## 📚 相关文档

- [核心概念](core-concepts.md) - UGRID 的基础概念
- [1D 网络拓扑](1d-network.md) - 1D 网格的详细定义
- [2D 三角形拓扑](2d-triangular.md) - 2D 三角形网格的详细定义
- [UGRID 官方文档](https://ugrid-conventions.github.io/ugrid-conventions/) - 官方命名约定

---

*下一步*: [1D 网络拓扑](1d-network.md) | [2D 三角形拓扑](2d-triangular.md)
