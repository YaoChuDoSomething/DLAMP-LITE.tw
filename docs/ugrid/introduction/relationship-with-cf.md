# UGRID 与 CF Conventions 的关系

## 🔗 官方集成状态

**UGRID Conventions 已被 CF Conventions 官方集成！**

自 **CF v1.11** 起，UGRID 1.0 已成为 CF 规范的正式组成部分。这意味着 UGRID 不再是一个独立的扩展，而是 CF 的一部分。

## 📋 官方声明

来自 CF v1.12 文档的官方声明：

> ### 1.6. UGRID Conventions
> These conventions implicitly incorporate parts of the UGRID conventions for storing unstructured (or flexible mesh) data in netCDF files using mesh topologies [[UGRID](#UGRID)]. **Only version 1.0 of the UGRID conventions is allowed.** The UGRID conventions description is referenced from, rather than rewritten into, this document and the canonical description of how to store mesh topologies is only to be found at [[UGRID](#UGRID)].

---

> A summary indicating how UGRID relates to other parts of the CF conventions, and which features of UGRID are excluded from CF, can be found in [Section 5.9, "Mesh Topology Variables"](#mesh-topology-variables). To reduce the chance of ambiguities arising from their accidental re-use, all of the UGRID standardized attributes are specified in [Appendix K, Mesh Topology Attributes](#appendix-mesh-topology-attributes) and [Appendix A, Attributes](#attribute-appendix).

---

> The UGRID conventions have their own conformance document, which should be used in conjunction with the CF conformance document when checking the validity of datasets.

## 🔄 集成时间线

| CF 版本 | 发布日期 | UGRID 状态 | Conventions 属性要求 |
|----------|----------|------------|--------------------|
| CF-1.0-1.5 | 2003-2011 | ❌ 未集成 | 需要独立工具支持 |
| CF-1.6 | 2011-12-05 | ✅ 引用 | `Conventions = "CF-1.6, UGRID-1.0"` |
| CF-1.7 | 2017-08-07 | ✅ 引用 | `Conventions = "CF-1.7, UGRID-1.0"` |
| CF-1.8 | 2020-02-11 | ✅ 引用 | `Conventions = "CF-1.8, UGRID-1.0"` |
| CF-1.9 | 2021-09-10 | ✅ 引用 | `Conventions = "CF-1.9, UGRID-1.0"` |
| CF-1.10 | 2022-08-31 | ✅ 引用 | `Conventions = "CF-1.10, UGRID-1.0"` |
| **CF-1.11** | **2023-12-05** | **✅ 完全集成** | **`Conventions = "CF-1.11"`** ✅ |
| CF-1.12 | 2024-12-04 | ✅ 完全集成 | `Conventions = "CF-1.12"` |
| CF-1.13 | 2025-12-17 | ✅ 完全集成 | `Conventions = "CF-1.13"` |
| CF-1.14-draft | 2026-07-30 | ✅ 完全集成 | `Conventions = "CF-1.14-draft"` |

## 🎯 关键转变

### CF v1.10 及之前

在 CF v1.10 及之前，UGRID 是一个 **独立的扩展**，需要显式声明：

```netcdf
:Conventions = "CF-1.8, UGRID-1.0" ;
```

**特点**：
- UGRID 是 CF 的扩展
- 需要单独维护符合性
- 工具需要同时支持 CF 和 UGRID

### CF v1.11 及之后 ✅

从 CF v1.11 开始，UGRID 1.0 **完全集成到 CF 规范中**：

```netcdf
:Conventions = "CF-1.11" ;  // 自动支持 UGRID 1.0
```

**特点**：
- UGRID 1.0 是 CF 的一部分
- 不需要显式声明 UGRID
- 使用 CF v1.11+ 的文件自动支持网格拓扑
- 符合性检查统一

## 📐 CF 中的 UGRID 集成点

### 1. 属性标准化 (Appendix A & K)

CF 文档在 **Appendix A (Attributes)** 和 **Appendix K (Mesh Topology Attributes)** 中列出了所有 UGRID 标准化的属性：

**UGRID 标准化属性包括**：

#### 网格拓扑属性 (Mesh Topology Attributes)
- `cf_role` - 定义变量的角色 (如 `mesh_topology`, `edge_node_connectivity`)
- `topology_dimension` - 网格的最高维度
- `node_coordinates` - 指向节点坐标变量
- `edge_node_connectivity` - 指向边-节点连接性变量
- `face_node_connectivity` - 指向面-节点连接性变量
- `volume_node_connectivity` - 指向体积-节点连接性变量
- `face_dimension` - 面的维度
- `edge_dimension` - 边的维度
- `volume_dimension` - 体积的维度
- `face_edge_connectivity` - 指向面-边连接性变量
- `face_face_connectivity` - 指向面-面连接性变量
- `edge_face_connectivity` - 指向边-面连接性变量
- `boundary_node_connectivity` - 指向边界-节点连接性变量
- `volume_shape_type` - 体积形状类型
- `start_index` - 索引起始值 (0 或 1)

#### 数据位置属性
- `mesh` - 指向关联的网格拓扑变量
- `location` - 数据定义的位置 (node, edge, face, volume)
- `location_index_set` - 位置索引集

### 2. 网格拓扑变量 (Section 5.9)

CF v1.11+ 在 **Section 5.9 "Mesh Topology Variables"** 中详细描述了网格拓扑变量的要求和用法。

**核心要求**：
- 网格拓扑变量必须有 `cf_role = "mesh_topology"`
- 必须有 `topology_dimension` 属性
- 必须有 `node_coordinates` 属性
- 必须有至少一个 `*_node_connectivity` 属性

### 3. 符合性要求

UGRID 保留了自己的符合性文档，但 CF 文档现在也包含了相关的符合性要求：

- UGRID 符合性文档应该与 CF 符合性文档一起使用
- 使用 CF v1.11+ 检查 UGRID 文件时，两个文档都需要参考

## 🔧 技术集成详情

### 1. 属性集成

UGRID 的所有标准化属性都被 CF v1.11+ 采纳，这意味着：

- ✅ CF 工具可以识别 UGRID 属性
- ✅ UGRID 属性在 CF 文档中有定义
- ✅ 不会与 CF 现有属性冲突
- ✅ 属性的语义在 CF 和 UGRID 中一致

### 2. 规范引用

CF v1.11+ 文档 **引用** UGRID 规范，而不是重写：

> "The UGRID conventions description is referenced from, rather than rewritten into, this document and the canonical description of how to store mesh topologies is only to be found at [[UGRID](#UGRID)]."

这意味着：
- UGRID 的官方定义在 [ugrid-conventions.github.io](https://ugrid-conventions.github.io/ugrid-conventions/)
- CF 文档提供了 UGRID 的概述和集成方式
- 详细的技术细节仍然在 UGRID 文档中

### 3. 版本限制

CF v1.11+ **只允许 UGRID v1.0**：

> "Only version 1.0 of the UGRID conventions is allowed."

这意味着：
- ✅ UGRID v1.0 是官方支持的版本
- ❌ UGRID v0.9 及更早版本不被 CF v1.11+ 支持
- ⚠️ 未来的 UGRID v2.0 需要 CF 的更新

## 📊 UGRID 在 CF 中的定位

### CF 的扩展机制

CF 采用了 **引用扩展** 的机制来集成 UGRID：

1. **引用外部标准**: CF 文档引用 UGRID 规范
2. **采纳属性定义**: CF 采纳 UGRID 的标准化属性
3. **提供集成指导**: CF 提供如何在 CF 文件中使用 UGRID
4. **统一符合性**: CF 和 UGRID 的符合性检查可以一起使用

### UGRID 相对于 CF 的其他部分

| CF 组件 | UGRID 集成 | 说明 |
|----------|------------|------|
| 核心属性 | ✅ 完全集成 | 如 `Conventions`, `title`, `history` |
| 坐标变量 | ✅ 完全集成 | UGRID 使用 CF 的坐标变量定义 |
| 坐标系统 | ✅ 完全集成 | 支持各种坐标系统 |
| 单位定义 | ✅ 完全集成 | 使用 CF 的单位定义 |
| 标准名称 | ✅ 完全集成 | 使用 CF 的标准名称表 |
| 时间坐标 | ✅ 完全集成 | 使用 CF 的时间坐标定义 |
| 网格拓扑 | ✅ **UGRID 扩展** | UGRID 提供的功能 |
| 非结构化网格 | ✅ **UGRID 扩展** | UGRID 的核心功能 |

## ✅ 最佳实践

### 对于数据生产者

1. **使用最新的 CF 版本**
   ```netcdf
   :Conventions = "CF-1.12" ;  // 推荐
   ```

2. **不需要显式声明 UGRID**
   ```netcdf
   // ✅ 正确 (CF v1.11+)
   :Conventions = "CF-1.12" ;
   
   // ❌ 不必要 (CF v1.11+)
   :Conventions = "CF-1.12, UGRID-1.0" ;
   ```

3. **确保符合 UGRID v1.0**
   - 使用 `cf_role = "mesh_topology"`
   - 定义 `topology_dimension`
   - 定义 `node_coordinates`
   - 定义连接性变量

4. **验证文件符合性**
   - 使用 CF 符合性检查器
   - 使用 UGRID 符合性检查器
   - 确保同时满足 CF 和 UGRID 的要求

### 对于数据使用者

1. **检查 CF 版本**
   ```python
   import netCDF4
   nc = netCDF4.Dataset('file.nc')
   conventions = nc.Conventions
   
   if 'CF-1.11' in conventions or 'CF-1.12' in conventions:
       # 支持 UGRID
       supports_ugrid = True
   else:
       # 需要检查是否显式声明 UGRID
       supports_ugrid = 'UGRID' in conventions
   ```

2. **查找网格拓扑变量**
   ```python
   # 查找 cf_role = "mesh_topology" 的变量
   for var in nc.variables.values():
       if hasattr(var, 'cf_role') and var.cf_role == 'mesh_topology':
           mesh_var = var
           break
   ```

3. **使用 UGRID 相关工具**
   - xarray + cf-xarray
   - NetCDF-Fortran 库
   - ParaView
   - VisIt

## 🔍 兼容性检查

### 检查文件是否支持 UGRID

1. **检查 Conventions 属性**
   ```bash
   ncdump -h file.nc | grep Conventions
   ```

2. **检查网格拓扑变量**
   ```bash
   ncdump -h file.nc | grep cf_role
   ```

3. **使用 Python 检查**
   ```python
   import netCDF4
   
   def is_ugrid_compliant(filepath):
       nc = netCDF4.Dataset(filepath)
       
       # 检查 Conventions
       conventions = getattr(nc, 'Conventions', '')
       if 'CF-1.11' in conventions or 'UGRID' in conventions:
           # 检查网格拓扑变量
           for var in nc.variables.values():
               if hasattr(var, 'cf_role') and var.cf_role == 'mesh_topology':
                   if hasattr(var, 'topology_dimension') and hasattr(var, 'node_coordinates'):
                       return True
       return False
   ```

### 验证 UGRID 符合性

1. **官方 UGRID 符合性检查器**
   - [ugrid-conventions/conformance](https://github.com/ugrid-conventions/ugrid-conventions/tree/master/conformance)

2. **CF 符合性检查器**
   - [cf-checker](https://github.com/cedadev/cf-checker)
   - [Compliance Checker](https://compliance.ioos.us/)

3. **在线验证工具**
   - [IOOS Compliance Checker](https://compliance.ioos.us/)

## 📖 CF 文档中的 UGRID 参考

### CF v1.12 中的 UGRID 相关部分

1. **Section 1.6 - UGRID Conventions**
   - UGRID 集成的概述
   - 版本要求
   - 符合性说明

2. **Section 5.9 - Mesh Topology Variables**
   - 网格拓扑变量的定义
   - 必需和可选属性
   - 示例

3. **Appendix A - Attributes**
   - UGRID 标准化属性的定义
   - 属性值和用法

4. **Appendix K - Mesh Topology Attributes**
   - 所有 UGRID 属性的详细定义
   - 属性之间的关系

## 🔗 重要链接

### CF 官方资源
- [CF Conventions 官方网站](https://cfconventions.org/)
- [CF v1.12 文档](https://cfconventions.org/cf-conventions/cf-conventions.html)
- [CF GitHub 仓库](https://github.com/cf-convention/cf-conventions)

### UGRID 官方资源
- [UGRID Conventions 官方文档](https://ugrid-conventions.github.io/ugrid-conventions/)
- [UGRID GitHub 仓库](https://github.com/ugrid-conventions/ugrid-conventions)
- [UGRID 符合性文档](https://ugrid-conventions.github.io/ugrid-conventions/conformance/)

### 集成资源
- [CF 文档中关于 UGRID 的部分](https://cfconventions.org/cf-conventions/cf-conventions.html#ugrid-conventions)
- [CF 文档中关于网格拓扑的部分](https://cfconventions.org/cf-conventions/cf-conventions.html#mesh-topology-variables)
- [CF Appendix K - Mesh Topology Attributes](https://cfconventions.org/cf-conventions/cf-conventions.html#appendix-mesh-topology-attributes)

## ❓ 常见问题

### Q1: CF v1.11+ 是否完全兼容 UGRID v1.0？
**A**: 是的。CF v1.11+ 完全集成了 UGRID v1.0，所有 UGRID v1.0 的功能都被支持。

### Q2: 我是否可以在 CF v1.8 文件中使用 UGRID？
**A**: 可以，但需要显式声明：`Conventions = "CF-1.8, UGRID-1.0"`。

### Q3: 使用 CF v1.12 时是否还需要声明 UGRID？
**A**: 不需要。CF v1.11+ 自动支持 UGRID 1.0，只需要声明 CF 版本即可。

### Q4: 我如何知道我的文件是否符合 UGRID 标准？
**A**: 使用 UGRID 符合性检查器，或者检查是否有 `cf_role = "mesh_topology"` 变量和相应的属性。

### Q5: UGRID 是否支持 4D 网格？
**A**: UGRID v1.0 支持 1D、2D、3D 网格。4D 网格（如时间变化的网格）在当前版本中支持有限，属于未来发展方向。

### Q6: 我可以使用 UGRID v0.9 吗？
**A**: 在 CF v1.11+ 中，只有 UGRID v1.0 被官方支持。UGRID v0.9 被认为是过时的。

---

*下一步*: [概述](overview.md) | [历史](history.md)
