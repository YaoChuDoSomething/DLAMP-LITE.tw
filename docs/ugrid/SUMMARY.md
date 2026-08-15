# UGRID Conventions 文档导航

## 📚 UGRID 文档集合

本文档集合提供了 **UGRID Conventions** 的完整技术文档和参考资料。UGRID 是 **NetCDF Climate and Forecast (CF) Metadata Conventions** 的官方扩展，用于在 NetCDF 文件中存储非结构化网格数据。

---

## 📖 **文档结构**

### 🎓 **入门指南**
- [概述](introduction/overview.md) - UGRID 的基本概念和应用
- [开发历史](introduction/history.md) - UGRID 的起源、发展和里程碑
- [与 CF 的关系](introduction/relationship-with-cf.md) - UGRID 与 CF Conventions 的集成

### 🏗️ **核心规范**
- [核心概念](conventions/core-concepts.md) - 几何元素、连接性、数据位置等基础概念

#### 🔗 **拓扑定义**
- [命名约定](conventions/topology/naming-conventions.md) - 几何元素的标准命名
- [1D 网络拓扑](conventions/topology/1d-network.md) - 河流、管道等一维网络
- [2D 三角形网格](conventions/topology/2d-triangular.md) - 三角形网格拓扑 (待创建)
- [2D 灵活网格](conventions/topology/2d-flexible.md) - 混合形状的二维网格 (待创建)
- [3D 分层网格](conventions/topology/3d-layered.md) - 2D 网格 + 垂直分层 (待创建)
- [3D 完全非结构化网格](conventions/topology/3d-unstructured.md) - 完全三维非结构化网格 (待创建)

#### 📍 **数据定义**
- [数据在非结构化网格上的定义](conventions/data-location.md) (待创建)
- [体积与通量变量](conventions/volume-flux-variables.md) (待创建)
- [位置索引集](conventions/location-index-set.md) (待创建)

### ⚙️ **实现指南**
- [符合性要求](implementation/conformance.md) (待创建)
- [最佳实践](implementation/best-practices.md) (待创建)

#### 📄 **代码示例**
- [1D 网络示例](implementation/examples/1d-network-example.md) (待创建)
- [2D 三角形网格示例](implementation/examples/2d-triangular-example.md) (待创建)
- [3D 分层网格示例](implementation/examples/3d-layered-example.md) (待创建)

### 🔬 **技术细节**
- [索引方式](technical-details/indexing.md) - 0-based vs 1-based 索引 (待创建)
- [元数据属性](technical-details/metadata-attributes.md) - 所有标准化属性详解 (待创建)
- [坐标系统](technical-details/coordinate-systems.md) - 坐标定义和转换 (待创建)

### 🌐 **资源与工具**
- [参考资源](resources/references.md) (待创建)
- [工具与库](resources/tools-libraries.md) (待创建)
- [常见问题解答](resources/faqs.md) (待创建)

---

## 🎯 **快速入门**

### 对于初学者
1. 从 [概述](introduction/overview.md) 开始了解 UGRID 的基本概念
2. 阅读 [与 CF 的关系](introduction/relationship-with-cf.md) 了解集成方式
3. 学习 [核心概念](conventions/core-concepts.md) 掌握基础知识

### 对于开发者
1. 查看 [命名约定](conventions/topology/naming-conventions.md) 了解标准命名
2. 学习 [1D 网络拓扑](conventions/topology/1d-network.md) 从简单示例开始
3. 深入 [2D 三角形网格](conventions/topology/2d-triangular.md) 了解复杂拓扑

### 对于实践者
1. 查看 [示例代码](implementation/examples/) 获取实际代码
2. 学习 [最佳实践](implementation/best-practices.md) 掌握最佳方法
3. 使用 [符合性检查](implementation/conformance.md) 验证文件

---

## 🔑 **核心关键字**

本文档集合涵盖了以下所有关键概念：

### 基础概念
- ✅ **netCDF** - UGRID 基于的文件格式
- ✅ **Metadata** - 完整的元数据定义标准
- ✅ **Grid Cells** (网格单元) - 2D 面元素 (Faces)
- ✅ **Grid Edges** (网格边) - 1D 边元素 (Edges)
- ✅ **Grid Vertices** (网格顶点) - 0D 节点元素 (Nodes/Vertices)
- ✅ **CF Conventions** - UGRID 的母标准

### 高级概念
- ✅ **Mesh Topology** (网格拓扑) - 元素之间的连接关系
- ✅ **Unstructured Grid** (非结构化网格) - 主要应用场景
- ✅ **Flexible Mesh** (灵活网格) - 支持多种网格类型
- ✅ **Connectivity** (连接性) - 元素之间的映射关系
- ✅ **Data Location** (数据位置) - 数据定义在哪个元素上

### 实现相关
- ✅ **Conventions Attribute** - 标准声明
- ✅ **cf_role** - 变量角色定义
- ✅ **topology_dimension** - 网格维度
- ✅ **node_coordinates** - 节点坐标
- ✅ **face_node_connectivity** - 面-节点连接性

---

## ✅ **UGRID 定义状态**

**UGRID Conventions 已被清楚定义！**

| 方面 | 状态 | 说明 |
|------|------|------|
| **官方标准** | ✅ 已定义 | UGRID v1.0 是官方标准 |
| **CF 集成** | ✅ 已集成 | 自 CF v1.11 起完全集成 |
| **文档完整性** | ✅ 完整 | 官方文档齐全 |
| **社区采用** | ✅ 广泛 | 多个领域采用 |
| **工具支持** | ✅ 成熟 | 多个工具支持 |

### 官方信息

- **官方版本**: v1.0
- **官方文档**: [ugrid-conventions.github.io](https://ugrid-conventions.github.io/ugrid-conventions/)
- **GitHub 仓库**: [ugrid-conventions/ugrid-conventions](https://github.com/ugrid-conventions/ugrid-conventions)
- **CF 集成版本**: CF v1.11+

---

## 📊 **文档统计**

| 分类 | 文件数 | 状态 |
|------|--------|------|
| 入门指南 | 3/3 | ✅ 完成 |
| 核心规范 | 1/6 | 🟡 进行中 |
| 实现指南 | 0/3 | ⏳ 待创建 |
| 技术细节 | 0/3 | ⏳ 待创建 |
| 资源工具 | 0/3 | ⏳ 待创建 |
| **总计** | **4/18** | 🟡 进行中 |

---

## 🎓 **学习路径**

### 🐣 **新手路径** (预计时间: 1-2 小时)
```
概述 → 与 CF 的关系 → 核心概念 → 1D 网络拓扑
   ↓
快速验证 → 简单示例
```

### 👨‍💻 **开发者路径** (预计时间: 3-5 小时)
```
核心概念 → 命名约定 → 1D 网络 → 2D 三角形
   ↓
数据定义 → 体积通量 → 位置索引集
   ↓
符合性检查 → 最佳实践
```

### 🏗️ **专家路径** (预计时间: 8+ 小时)
```
所有核心规范 → 所有拓扑类型 → 所有数据定义
   ↓
技术细节 → 实现指南 → 工具使用
   ↓
高级应用 → 贡献代码
```

---

## 🔗 **官方资源链接**

### UGRID 官方资源
- [UGRID Conventions 官方文档](https://ugrid-conventions.github.io/ugrid-conventions/)
- [UGRID GitHub 仓库](https://github.com/ugrid-conventions/ugrid-conventions)
- [UGRID 符合性文档](https://ugrid-conventions.github.io/ugrid-conventions/conformance/)

### CF 官方资源
- [CF Conventions 官方网站](https://cfconventions.org/)
- [CF 文档 - UGRID 部分](https://cfconventions.org/cf-conventions/cf-conventions.html#ugrid-conventions)
- [CF GitHub 仓库](https://github.com/cf-convention/cf-conventions)

### 工具与验证
- [IOOS Compliance Checker](https://compliance.ioos.us/)
- [cf-checker](https://github.com/cedadev/cf-checker)
- [NetCDF 官方网站](https://www.unidata.ucar.edu/software/netcdf/)

---

## 📝 **文档约定**

### 符号说明
- ✅ - 推荐/最佳实践
- ⚠️ - 重要注意事项
- ❌ - 禁止/错误做法
- 🔗 - 相关链接
- 📖 - 文档/参考
- 🎯 - 核心概念

### 代码格式
- `code` - 变量名、属性名
- **`bold code`** - 关键字、标准值
- ```cdl - CDL 代码块
- ```python - Python 代码块

### 结构约定
- 每个文档都有 **概述** 部分
- 每个概念都有 **定义** 和 **示例**
- 每个部分都有 **最佳实践** 建议

---

## 🤝 **贡献指南**

### 如何贡献
1. Fork 仓库
2. 创建特性分支
3. 提交变更
4. 创建 Pull Request

### 文档标准
- 使用 Markdown 格式
- 保持一致的结构和风格
- 包含示例和代码
- 提供清晰的解释

### 贡献者
- [用户名] - 初始文档创建
- (欢迎更多贡献者加入!)

---

*文档集合维护中... 最后更新: 2026-08-16*
