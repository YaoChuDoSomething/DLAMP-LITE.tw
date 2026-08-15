# UGRID 开发历史与版本演进

## 📜 起源与背景

### 问题的提出

在 2000 年代早期，环境建模社区（特别是海洋和水文模型）开始广泛使用 **非结构化网格 (Unstructured Meshes)**。这些模型需要更灵活的空间离散化方法来处理：

- 复杂的海岸线
- 不规则的地形
- 局部精细化的网格
- 多尺度的物理过程

然而，当时的 **CF Conventions (v1.0-1.4)** 主要针对 **结构化网格 (Structured Grids)**，即规则的经纬度网格或曲线坐标网格。对于非结构化网格数据，缺乏标准化的元数据定义，导致：

- ❌ 数据交换困难
- ❌ 不同软件之间兼容性差
- ❌ 缺乏统一的数据描述方式
- ❌ 难以开发通用的可视化和分析工具

### 早期尝试

在 UGRID 之前，有几个尝试试图解决非结构化网格数据的标准化问题：

1. **GridSpec (2004)**
   - 由 Venkatramani Balaji (GFDL/NOAA) 提出
   - 提供了非结构化网格的元数据框架
   - 但未被广泛采用

2. **各模型自定义格式**
   - SELFE、FVCOM、ADCIRC 等模型各自开发了自己的 NetCDF 输出格式
   - 导致数据碎片化

3. **CF 的扩展讨论**
   - CF 社区意识到需要支持非结构化网格
   - 但直接扩展 CF 被认为过于复杂

## 🤝 社区协作

### UGRID Google Group (2007-2010)

2007 年左右，一群来自不同建模社区的研究人员和工程师组建了 **UGRID Interoperability Google Group**，目标是开发一个通用的非结构化网格数据标准。

**主要参与者包括**：
- Bert Jagers (Deltares) - 主要贡献者
- David Stuebe (USGS)
- Tom Gross (USGS)
- Chris Barker (NOAA)
- Brian Zelenke (ACES)
- Rich Signell (USGS)
- Bob Oehmke (PNNL)
- 以及来自 SELFE、ELCIRC、FVCOM、ADCIRC 等模型社区的成员

### 讨论焦点

社区讨论主要集中在以下问题：

1. **几何元素命名**: node/vertex, edge, face, volume
2. **连接性表示**: 如何描述元素之间的关系
3. **数据位置**: 如何表示数据定义在哪个几何元素上
4. **CF 兼容性**: 如何与现有 CF 规范集成
5. **索引方式**: 0-based vs 1-based 索引
6. **坐标系统**: 支持各种坐标系

## 🏗️ 标准开发

### 初始草案 (2008-2009)

Bert Jagers 基于社区讨论，创建了 UGRID 的第一个草案版本。这个草案：

- 定义了基本的几何元素层次 (node, edge, face)
- 提出了连接性变量的概念
- 定义了网格拓扑变量的属性
- 提供了简单的 2D 示例

### 公开征求意见 (2009-2010)

草案版本在社区中广泛征求意见，收到了来自各个模型社区的反馈和建议。主要修改包括：

- 增加了 3D 支持
- 完善了连接性变量的定义
- 增加了数据位置属性 (`mesh`, `location`)
- 改进了与 CF 的集成方式
- 增加了各种网格类型的示例

### 正式发布 v1.0 (2010)

经过多轮修订和社区验证，UGRID Conventions **v1.0** 于 2010 年正式发布。

**v1.0 的主要特性**：
- ✅ 支持 1D、2D、3D 网格
- ✅ 支持混合网格类型
- ✅ 详细的拓扑描述
- ✅ 与 CF v1.6 兼容
- ✅ 完整的符合性定义

## 🔄 版本演进

### v1.0 (2010) - 初始版本

- **状态**: 稳定版
- **CF 兼容性**: CF-1.6 (需要显式声明)
- **主要贡献者**: Bert Jagers, David Stuebe, Tom Gross 等
- **文档位置**: [ugrid-conventions.github.io](https://ugrid-conventions.github.io/ugrid-conventions/)

**v1.0 的核心贡献**：
1. 定义了标准的几何元素命名
2. 建立了连接性变量的框架
3. 定义了网格拓扑变量的属性
4. 提供了数据在网格上的定义方式
5. 确立了与 CF 的集成路径

### CF 集成过程

| CF 版本 | UGRID 状态 | 说明 |
|----------|------------|------|
| CF-1.0-1.5 | ❌ 未集成 | 需要独立使用 UGRID |
| CF-1.6 | ✅ 引用 | 可以声明 `Conventions = "CF-1.6, UGRID-1.0"` |
| CF-1.7-1.10 | ✅ 引用 | UGRID 1.0 被引用但未完全集成 |
| **CF-1.11+** | **✅ 完全集成** | **UGRID 1.0 作为 CF 的一部分** |

### CF v1.11 的里程碑 (2023)

2023年12月，CF v1.11 正式发布，其中 **完全集成了 UGRID 1.0 规范**：

> "These conventions implicitly incorporate parts of the UGRID conventions for storing unstructured (or flexible mesh) data in netCDF files using mesh topologies. Only version 1.0 of the UGRID conventions is allowed."

这意味着：
- ✅ 使用 `Conventions = "CF-1.11"` 就自动支持 UGRID 1.0
- ✅ 不再需要显式声明 UGRID
- ✅ UGRID 1.0 成为 CF 的官方组成部分
- ✅ UGRID 的所有标准化属性都被 CF 采纳

## 📊 影响与采用

### 社区采用

UGRID 被广泛采用的领域：

1. **海洋模型**
   - SELFE 模型完全支持 UGRID
   - FVCOM 社区采用 UGRID
   - ADCIRC 社区采用 UGRID
   - ELCIRC 社区采用 UGRID

2. **水文模型**
   - USGS 的多个水文模型
   - Deltares 的 Delft3D 模型
   - TELEMAC 系统

3. **大气模型**
   - 区域气候模型 (RCM)
   - 空气质量模型 (AQM)

4. **工具与库**
   - xarray (通过 cf-xarray)
   - NetCDF-Fortran 库
   - ParaView (通过 VTK)
   - VisIt
   - CDAT/CDO
   - NCO (NetCDF Operators)

### 标准影响

UGRID 对网格数据标准化的影响：

1. **统一了非结构化网格的元数据定义**
2. **促进了不同模型之间的数据交换**
3. **推动了 CF 规范的发展**
4. **为其他网格标准提供了参考**
5. **促进了科学数据的 FAIR 原则 (Findable, Accessible, Interoperable, Reusable)**

## 🎓 主要贡献者

以下人员对 UGRID 的开发做出了重要贡献（按字母顺序排列）：

### 核心贡献者
- **Bert Jagers** (Deltares) - 主要作者，v1.0 的主要设计者
- **David Stuebe** (USGS) - 重要贡献者
- **Tom Gross** (USGS) - 重要贡献者

### 其他重要贡献者
- Alex Crosby
- Bill Howe
- Brian Blanton
- Brian Zelenke
- Charles Seaton
- Chris Barker (NOAA)
- Cristina Forbes
- Dave Forrest
- Geoff Cowles
- Karen Schuchardt
- Phil Elson
- Rich Signell (USGS)
- Bob Oehmke (PNNL)

### 社区参与者
来自以下机构的研究人员和工程师参与了讨论和测试：
- Deltares (荷兰)
- USGS (美国地质调查局)
- NOAA (美国国家海洋和大气管理局)
- PNNL (太平洋西北国家实验室)
- 多个大学和研究机构
- 多个模型开发团队

## 🏆 里程碑事件

| 日期 | 事件 | 重要性 |
|------|------|--------|
| ~2007 | UGRID Google Group 成立 | 🌱 起源 |
| 2008 | Bert Jagers 创建初始草案 | 📝 起草 |
| 2009 | 社区广泛讨论和反馈 | 🗣️ 协作 |
| 2010 | **UGRID v1.0 正式发布** | 🎉 里程碑 |
| 2010 | 官方文档网站上线 | 🌐 发布 |
| 2010-2020 | 社区采用和工具支持 | 📈 增长 |
| 2023 | **CF v1.11 集成 UGRID** | 🏆 集成 |
| 2024 | 多个主流工具支持 UGRID | ✅ 成熟 |

## 🔮 未来展望

虽然 UGRID v1.0 已经非常稳定和广泛采用，但仍然有一些改进空间：

### 已知限制 (Known Issues)

根据官方文档，以下功能在当前版本中尚未完全支持：

1. **自适应网格拓扑** (Adaptive mesh topology)
   - 可能通过定义 `time_concatenation` 属性支持
   - 计划在未来版本中增加

2. **高阶元素数据** (Higher order element data)
   - 需要其他方案来存储
   - 有提议但未实现

3. **子网格数据** (Subgrid data)
   - Bundesanstalt für Wasserbau (BAW) 有相关提议
   - 需要进一步开发

4. **3D 完全非结构化网格** (Fully 3D unstructured meshes)
   - 一些概念已包含，但范围有限
   - 需要扩展

5. **多连通域** (Multiply-connected domains)
   - 当前支持有限

6. **幽灵元素** (Ghost elements)
   - 并行计算中的处理

### 可能的发展方向

1. **UGRID v2.0**
   - 解决已知限制
   - 增加新功能
   - 改进现有定义

2. **更好的 CF 集成**
   - 增加更多 UGRID 功能到 CF
   - 改进符合性检查

3. **工具支持**
   - 更多可视化工具
   - 更好的数据处理库
   - 改进的验证工具

4. **应用扩展**
   - 更多领域的采用
   - 更多模型的支持
   - 更好的最佳实践

## 📚 参考资源

- [UGRID 官方文档](https://ugrid-conventions.github.io/ugrid-conventions/)
- [UGRID GitHub 仓库](https://github.com/ugrid-conventions/ugrid-conventions)
- [CF 官方文档 - UGRID 部分](https://cfconventions.org/cf-conventions/cf-conventions.html#ugrid-conventions)
- [UGRID Google Group (存档)](https://groups.google.com/forum/#!forum/ugrid-interoperability)

---

*下一步*: [概述](overview.md) | [与 CF 的关系](relationship-with-cf.md)
