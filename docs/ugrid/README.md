# UGRID Conventions 文档集合

## 概述

本目录收集了 **UGRID Conventions** 的完整技术文档和相关资源。UGRID 是 **NetCDF Climate and Forecast (CF) Metadata Conventions** 的官方扩展，专门用于在 NetCDF 文件中存储 **非结构化网格 (Unstructured Grid)** 或 **灵活网格 (Flexible Mesh)** 模型数据。

## 📚 文档结构

```
 docs/ugrid/
 ├── README.md                    # 本文件 - 文档集合概述
 ├── introduction/
 │   ├── overview.md              # UGRID 概述与背景
 │   ├── history.md               # 开发历史与版本演进
 │   └── relationship-with-cf.md   # 与 CF Conventions 的关系
 ├── conventions/
 │   ├── core-concepts.md         # 核心概念与术语定义
 │   ├── topology/
 │   │   ├── naming-conventions.md  # 几何元素命名规范
 │   │   ├── 1d-network.md         # 1D 网络拓扑
 │   │   ├── 2d-triangular.md      # 2D 三角形网格拓扑
 │   │   ├── 2d-flexible.md        # 2D 灵活网格拓扑
 │   │   ├── 3d-layered.md         # 3D 分层网格拓扑
 │   │   └── 3d-unstructured.md   # 3D 完全非结构化网格拓扑
 │   ├── data-location.md          # 数据在非结构化网格上的定义
 │   ├── volume-flux-variables.md  # 体积与通量变量
 │   └── location-index-set.md     # 位置索引集
 ├── implementation/
 │   ├── conformance.md            # 符合性要求
 │   ├── examples/
 │   │   ├── 1d-network-example.md  # 1D 网络示例
 │   │   ├── 2d-triangular-example.md # 2D 三角形网格示例
 │   │   └── 3d-layered-example.md   # 3D 分层网格示例
 │   └── best-practices.md         # 最佳实践
 ├── technical-details/
 │   ├── indexing.md               # 0-based vs 1-based 索引
 │   ├── metadata-attributes.md   # 元数据属性详解
 │   └── coordinate-systems.md     # 坐标系统
 ├── resources/
 │   ├── references.md             # 参考资源与链接
 │   ├── tools-libraries.md       # 支持 UGRID 的工具与库
 │   └── faqs.md                   # 常见问题解答
 └── SUMMARY.md                    # 文档导航
```

## 🎯 核心关键字关联

本文档集合涵盖了以下所有关键概念：

- **netCDF** - UGRID 基于 NetCDF 文件格式
- **Metadata** - 提供完整的元数据定义标准
- **Grid Cells** (网格单元) - 2D 面元素 (faces)
- **Grid Edges** (网格边) - 1D 边元素 (edges)
- **Grid Vertices** (网格顶点) - 0D 节点元素 (nodes/vertices)
- **CF Conventions** - UGRID 是 CF 的官方扩展
- **Mesh Topology** (网格拓扑) - 描述网格元素之间的连接关系
- **Unstructured Grid** (非结构化网格) - 主要应用场景
- **Flexible Mesh** (灵活网格) - 支持多种网格类型

## ✅ UGRID Conventions 定义状态

**UGRID Conventions 已被清楚定义！**

- **官方版本**: v1.0 (当前最新稳定版)
- **官方文档**: [ugrid-conventions.github.io](https://ugrid-conventions.github.io/ugrid-conventions/)
- **GitHub 仓库**: [ugrid-conventions/ugrid-conventions](https://github.com/ugrid-conventions/ugrid-conventions)
- **CF 集成状态**: 自 CF v1.11 起，UGRID 1.0 已被完全集成到 CF 规范中

### 官方声明

> "The UGRID conventions have their own conformance document, which should be used in conjunction with the CF conformance document when checking the validity of datasets."

## 📖 快速入门

### 什么是 UGRID？

UGRID 为非结构化网格数据提供了标准化的元数据定义，使得不同的建模社区（如海洋、大气、水文模型）可以在 NetCDF 文件中存储和交换复杂的网格数据。

### 主要特性

1. **多维度支持**: 支持 1D、2D、3D 各种维度的网格
2. **混合元素**: 支持三角形、四边形等混合网格类型
3. **拓扑描述**: 详细描述节点、边、面、体积之间的连接关系
4. **数据位置**: 支持在不同网格位置（节点、边、面、体积）上定义数据
5. **CF 兼容**: 完全兼容 CF Conventions，可无缝集成

### 基本概念层次

| 维度 | 名称 | 描述 |
|------|------|------|
| 0D | Node (节点/顶点) | 基本几何元素，坐标点 |
| 1D | Edge (边) | 由两个节点定义的线段 |
| 2D | Face (面) | 由多个边围成的平面区域 |
| 3D | Volume (体积) | 由多个面围成的三维空间 |

## 🔗 相关标准

- **CF Conventions**: [cfconventions.org](https://cfconventions.org/)
- **NetCDF**: [unidata.ucar.edu/software/netcdf](https://www.unidata.ucar.edu/software/netcdf/)
- **COARDS**: CF 的前身标准

## 📝 文档约定

- 所有技术术语使用 **粗体** 标出
- 代码示例使用 ``` 标记
- 重要注意事项使用 ⚠️ 符号
- 最佳实践使用 ✅ 符号

## 🎓 学习路径

1. **初学者**: 从 [introduction/overview.md](introduction/overview.md) 开始
2. **开发者**: 查看 [conventions/core-concepts.md](conventions/core-concepts.md)
3. **实践者**: 学习 [implementation/examples/](implementation/examples/) 中的示例
4. **专家**: 深入 [technical-details/](technical-details/) 了解细节

---

*最后更新: 2026-08-16*  
*维护者: [ugrid-conventions](https://github.com/ugrid-conventions)*
