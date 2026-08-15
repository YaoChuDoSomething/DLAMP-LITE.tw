# UGRID 概述

## 🎯 什么是 UGRID Conventions？

**UGRID Conventions** 是一个用于在 **NetCDF** 文件中存储 **非结构化网格 (Unstructured Grid)** 或 **灵活网格 (Flexible Mesh)** 模型数据的标准。它是 **Climate and Forecast (CF) Metadata Conventions** 的官方扩展，为 CF 规范增加了对复杂网格拓扑的支持能力。

## 🏗️ 解决的问题

传统的 CF Conventions 主要针对结构化网格（如规则的经纬度网格），但现代的环境建模（海洋、大气、水文等）中，越来越多地使用非结构化网格，例如：

- **三角形网格**: 常用于海岸线复杂的区域
- **四边形混合网格**: 结合不同形状的网格单元
- **1D 网络**: 河流、管道系统
- **3D 分层网格**: 垂直方向分层的非结构化水平网格
- **完全 3D 非结构化网格**: 复杂的三维结构

UGRID 为这些复杂的网格类型提供了标准化的元数据定义。

## 🔧 技术特点

### 1. 几何元素层次

UGRID 定义了一个清晰的几何元素层次结构：

```
Volume (体积, 3D)
    ↓
Face (面, 2D)
    ↓
Edge (边, 1D)
    ↓
Node (节点/顶点, 0D)
```

每个维度的元素都有明确的定义和连接关系。

### 2. 拓扑描述

UGRID 使用 **连接性变量 (Connectivity Variables)** 来描述网格元素之间的关系：

- **`node_coordinates`**: 指向节点坐标变量
- **`edge_node_connectivity`**: 描述边与节点的连接
- **`face_node_connectivity`**: 描述面与节点的连接
- **`face_edge_connectivity`**: 描述面与边的连接
- **`volume_node_connectivity`**: 描述体积与节点的连接

### 3. 数据位置

UGRID 支持在不同网格位置上定义数据：

- **节点数据**: 定义在网格节点上
- **边数据**: 定义在网格边上
- **面数据**: 定义在网格面上
- **体积数据**: 定义在网格体积上

## 📋 UGRID 文件结构

一个典型的 UGRID 文件包含以下组件：

### 1. 网格拓扑变量 (Mesh Topology Variable)

这是一个 **虚拟变量 (Dummy Variable)**，包含描述网格拓扑的属性：

```cdl
topology_dimension = 2 ;
cf_role = "mesh_topology" ;
node_coordinates = "mesh_node_x mesh_node_y" ;
face_node_connectivity = "mesh_face_nodes" ;
edge_node_connectivity = "mesh_edge_nodes" ;  // 可选
```

### 2. 坐标变量 (Coordinate Variables)

描述网格节点的空间位置：

```cdl
double mesh_node_x(nMesh_node) ;
  mesh_node_x:standard_name = "longitude" ;
  mesh_node_x:units = "degrees_east" ;

double mesh_node_y(nMesh_node) ;
  mesh_node_y:standard_name = "latitude" ;
  mesh_node_y:units = "degrees_north" ;
```

### 3. 连接性变量 (Connectivity Variables)

描述网格元素之间的连接关系：

```cdl
int mesh_face_nodes(nMesh_face, nMaxNodesPerFace) ;
  mesh_face_nodes:cf_role = "face_node_connectivity" ;
  mesh_face_nodes:start_index = 0 ;  // 0-based 或 1-based 索引
  mesh_face_nodes:_FillValue = 999999 ;
```

### 4. 数据变量 (Data Variables)

实际的模型数据，关联到特定的网格位置：

```cdl
double water_level(time, nMesh_face) ;
  water_level:standard_name = "sea_surface_height_above_geoid" ;
  water_level:units = "m" ;
  water_level:mesh = "mesh2d" ;  // 关联到网格拓扑
  water_level:location = "face" ;  // 数据定义在面上
  water_level:coordinates = "mesh_face_x mesh_face_y" ;
```

## 🔄 与 CF Conventions 的集成

UGRID 与 CF Conventions 的关系经历了几个阶段：

### CF v1.6 及之前
- 需要显式声明: `Conventions = "CF-1.6, UGRID-1.0"`
- UGRID 是独立的扩展

### CF v1.7 - v1.10
- UGRID 1.0 被引用但未完全集成
- 仍然推荐显式声明 UGRID

### CF v1.11 及之后 ✅
- **UGRID 1.0 完全集成到 CF 规范中**
- 只需要声明: `Conventions = "CF-1.11"` 或更高版本
- 不需要显式声明 UGRID

## 🎯 主要应用领域

UGRID 广泛应用于以下领域：

1. **海洋模型**
   - SELFE (Semi-implicit Eulerian-Lagrangian Finite-Element)
   - ELCIRC (Eulerian-Lagrangian Circulation)
   - FVCOM (Finite Volume Community Ocean Model)
   - ADCIRC (ADvanced CIRCulation)

2. **水文模型**
   - 河流网络
   - 洪水模拟
   - 地下水模型

3. **大气模型**
   - 区域气候模型
   - 空气质量模型

4. **其他领域**
   - 工程模拟
   - 地质建模
   - 生物地球化学模型

## 📊 UGRID vs 其他网格标准

| 特性 | UGRID | CF (传统) | GridSpec | SGRID |
|------|-------|-----------|----------|-------|
| 非结构化网格 | ✅ | ❌ | ✅ | ✅ |
| 结构化网格 | ✅ | ✅ | ✅ | ❌ |
| CF 集成 | ✅ | ✅ | ❌ | ❌ |
| 拓扑描述 | ✅ | ❌ | ✅ | ✅ |
| 多维度支持 | ✅ | ❌ | ✅ | ✅ |
| 官方标准 | ✅ | ✅ | ❌ | ❌ |

## 🚀 为什么选择 UGRID？

1. **官方认可**: CF 官方扩展，具有权威性
2. **社区支持**: 广泛的建模社区采用
3. **灵活性**: 支持各种复杂的网格类型
4. **兼容性**: 与现有 CF 工具完全兼容
5. **标准化**: 提供清晰的元数据定义
6. **互操作性**: 不同软件之间可以交换数据

## 📚 学习资源

- [官方文档](https://ugrid-conventions.github.io/ugrid-conventions/)
- [GitHub 仓库](https://github.com/ugrid-conventions/ugrid-conventions)
- [CF 官方文档](https://cfconventions.org/)
- [UGRID Google Group](https://groups.google.com/forum/#!forum/ugrid-interoperability)

## 💡 快速验证

要验证一个 NetCDF 文件是否符合 UGRID 标准：

1. 检查是否有 `cf_role = "mesh_topology"` 属性
2. 检查是否有 `topology_dimension` 属性
3. 检查是否有 `node_coordinates` 属性
4. 检查是否有 `*_node_connectivity` 属性
5. 检查数据变量是否有 `mesh` 和 `location` 属性

✅ 如果以上条件都满足，那么文件很可能符合 UGRID 标准。

---

*下一步*: [开发历史](history.md) | [与 CF 的关系](relationship-with-cf.md)
