# UGRID Conventions 文件集合

## 概述

本目錄收集了 **UGRID Conventions** 的完整技術文件和相關資源。UGRID 是 **NetCDF Climate and Forecast (CF) Metadata Conventions** 的官方擴充套件，專門用於在 NetCDF 檔案中儲存 **非結構化網格 (Unstructured Grid)** 或 **靈活網格 (Flexible Mesh)** 模型資料。

## 📚 文件結構

```test
 docs/ugrid/
 ├── README.md                    # 本檔案 - 文件集合概述
 ├── introduction/
 │   ├── overview.md              # UGRID 概述與背景
 │   ├── history.md               # 開發歷史與版本演進
 │   └── relationship-with-cf.md   # 與 CF Conventions 的關係
 ├── conventions/
 │   ├── core-concepts.md         # 核心概念與術語定義
 │   ├── topology/
 │   │   ├── naming-conventions.md  # 幾何元素命名規範
 │   │   ├── 1d-network.md         # 1D 網路拓撲
 │   │   ├── 2d-triangular.md      # 2D 三角形網格拓撲
 │   │   ├── 2d-flexible.md        # 2D 靈活網格拓撲
 │   │   ├── 3d-layered.md         # 3D 分層網格拓撲
 │   │   └── 3d-unstructured.md   # 3D 完全非結構化網格拓撲
 │   ├── data-location.md          # 資料在非結構化網格上的定義
 │   ├── volume-flux-variables.md  # 體積與通量變數
 │   └── location-index-set.md     # 位置索引集
 ├── implementation/
 │   ├── conformance.md            # 符合性要求
 │   ├── examples/
 │   │   ├── 1d-network-example.md  # 1D 網路示例
 │   │   ├── 2d-triangular-example.md # 2D 三角形網格示例
 │   │   └── 3d-layered-example.md   # 3D 分層網格示例
 │   └── best-practices.md         # 最佳實踐
 ├── technical-details/
 │   ├── indexing.md               # 0-based vs 1-based 索引
 │   ├── metadata-attributes.md   # 後設資料屬性詳解
 │   └── coordinate-systems.md     # 座標系統
 ├── resources/
 │   ├── references.md             # 參考資源與連結
 │   ├── tools-libraries.md       # 支援 UGRID 的工具與庫
 │   └── faqs.md                   # 常見問題解答
 └── SUMMARY.md                    # 文件導航
```

## 🎯 核心關鍵字關聯

本文件集合涵蓋了以下所有關鍵概念：

- **netCDF** - UGRID 基於 NetCDF 檔案格式
- **Metadata** - 提供完整的後設資料定義標準
- **Grid Cells** (網格單元) - 2D 面元素 (faces)
- **Grid Edges** (網格邊) - 1D 邊元素 (edges)
- **Grid Vertices** (網格頂點) - 0D 節點元素 (nodes/vertices)
- **CF Conventions** - UGRID 是 CF 的官方擴充套件
- **Mesh Topology** (網格拓撲) - 描述網格元素之間的連線關係
- **Unstructured Grid** (非結構化網格) - 主要應用場景
- **Flexible Mesh** (靈活網格) - 支援多種網格型別

## ✅ UGRID Conventions 定義狀態

**UGRID Conventions 已被清楚定義！**

- **官方版本**: v1.0 (當前最新穩定版)
- **官方文件**: [ugrid-conventions.github.io](https://ugrid-conventions.github.io/ugrid-conventions/)
- **GitHub 倉庫**: [ugrid-conventions/ugrid-conventions](https://github.com/ugrid-conventions/ugrid-conventions)
- **CF 整合狀態**: 自 CF v1.11 起，UGRID 1.0 已被完全整合到 CF 規範中

### 官方宣告

> "The UGRID conventions have their own conformance document, which should be used in conjunction with the CF conformance document when checking the validity of datasets."

## 📖 快速入門

### 什麼是 UGRID？

UGRID 為非結構化網格資料提供了標準化的後設資料定義，使得不同的建模社群（如海洋、大氣、水文模型）可以在 NetCDF 檔案中儲存和交換複雜的網格資料。

### 主要特性

1. **多維度支援**: 支援 1D、2D、3D 各種維度的網格
2. **混合元素**: 支援三角形、四邊形等混合網格型別
3. **拓撲描述**: 詳細描述節點、邊、面、體積之間的連線關係
4. **資料位置**: 支援在不同網格位置（節點、邊、面、體積）上定義資料
5. **CF 相容**: 完全相容 CF Conventions，可無縫整合

### 基本概念層次

| 維度 | 名稱 | 描述 |
|------|------|------|
| 0D | Node (節點/頂點) | 基本幾何元素，座標點 |
| 1D | Edge (邊) | 由兩個節點定義的線段 |
| 2D | Face (面) | 由多個邊圍成的平面區域 |
| 3D | Volume (體積) | 由多個面圍成的三維空間 |

## 🔗 相關標準

- **CF Conventions**: [cfconventions.org](https://cfconventions.org/)
- **NetCDF**: [unidata.ucar.edu/software/netcdf](https://www.unidata.ucar.edu/software/netcdf/)
- **COARDS**: CF 的前身標準

## 📝 文件約定

- 所有技術術語使用 **粗體** 標出
- 程式碼示例使用 ``` 標記
- 重要注意事項使用 ⚠️ 符號
- 最佳實踐使用 ✅ 符號

## 🎓 學習路徑

1. **初學者**: 從 [introduction/overview.md](introduction/overview.md) 開始
2. **開發者**: 檢視 [conventions/core-concepts.md](conventions/core-concepts.md)
3. **實踐者**: 學習 [implementation/examples/](implementation/examples/) 中的示例
4. **專家**: 深入 [technical-details/](technical-details/) 瞭解細節

---

*最後更新: 2026-08-16*  
*維護者: [ugrid-conventions](https://github.com/ugrid-conventions)*
