# UGRID Conventions 文件導航

## 📚 UGRID 文件集合

本文件集合提供了 **UGRID Conventions** 的完整技術文件和參考資料。UGRID 是 **NetCDF Climate and Forecast (CF) Metadata Conventions** 的官方擴充套件，用於在 NetCDF 檔案中儲存非結構化網格資料。

---

## 📖 **文件結構**

### 🎓 **入門指南**

- [概述](introduction/overview.md) - UGRID 的基本概念和應用
- [開發歷史](introduction/history.md) - UGRID 的起源、發展和里程碑
- [與 CF 的關係](introduction/relationship-with-cf.md) - UGRID 與 CF Conventions 的整合

### 🏗️ **核心規範**

- [核心概念](conventions/core-concepts.md) - 幾何元素、連線性、資料位置等基礎概念

#### 🔗 **拓撲定義**

- [命名約定](conventions/topology/naming-conventions.md) - 幾何元素的標準命名
- [1D 網路拓撲](conventions/topology/1d-network.md) - 河流、管道等一維網路
- [2D 三角形網格](conventions/topology/2d-triangular.md) - 三角形網格拓撲 (待建立)
- [2D 靈活網格](conventions/topology/2d-flexible.md) - 混合形狀的二維網格 (待建立)
- [3D 分層網格](conventions/topology/3d-layered.md) - 2D 網格 + 垂直分層 (待建立)
- [3D 完全非結構化網格](conventions/topology/3d-unstructured.md) - 完全三維非結構化網格 (待建立)

#### 📍 **資料定義**

- [資料在非結構化網格上的定義](conventions/data-location.md) (待建立)
- [體積與通量變數](conventions/volume-flux-variables.md) (待建立)
- [位置索引集](conventions/location-index-set.md) (待建立)

### ⚙️ **實現指南**

- [符合性要求](implementation/conformance.md) (待建立)
- [最佳實踐](implementation/best-practices.md) (待建立)

#### 📄 **程式碼示例**

- [1D 網路示例](implementation/examples/1d-network-example.md) (待建立)
- [2D 三角形網格示例](implementation/examples/2d-triangular-example.md) (待建立)
- [3D 分層網格示例](implementation/examples/3d-layered-example.md) (待建立)

### 🔬 **技術細節**

- [索引方式](technical-details/indexing.md) - 0-based vs 1-based 索引 (待建立)
- [後設資料屬性](technical-details/metadata-attributes.md) - 所有標準化屬性詳解 (待建立)
- [座標系統](technical-details/coordinate-systems.md) - 座標定義和轉換 (待建立)

### 🌐 **資源與工具**

- [參考資源](resources/references.md) (待建立)
- [工具與庫](resources/tools-libraries.md) (待建立)
- [常見問題解答](resources/faqs.md) (待建立)

---

## 🎯 **快速入門**

### 對於初學者

1. 從 [概述](introduction/overview.md) 開始瞭解 UGRID 的基本概念
2. 閱讀 [與 CF 的關係](introduction/relationship-with-cf.md) 瞭解整合方式
3. 學習 [核心概念](conventions/core-concepts.md) 掌握基礎知識

### 對於開發者

1. 檢視 [命名約定](conventions/topology/naming-conventions.md) 瞭解標準命名
2. 學習 [1D 網路拓撲](conventions/topology/1d-network.md) 從簡單示例開始
3. 深入 [2D 三角形網格](conventions/topology/2d-triangular.md) 瞭解複雜拓撲

### 對於實踐者

1. 檢視 [示例程式碼](implementation/examples/) 獲取實際程式碼
2. 學習 [最佳實踐](implementation/best-practices.md) 掌握最佳方法
3. 使用 [符合性檢查](implementation/conformance.md) 驗證檔案

---

## 🔑 **核心關鍵字**

本文件集合涵蓋了以下所有關鍵概念：

### 基礎概念

- ✅ **netCDF** - UGRID 基於的檔案格式
- ✅ **Metadata** - 完整的後設資料定義標準
- ✅ **Grid Cells** (網格單元) - 2D 面元素 (Faces)
- ✅ **Grid Edges** (網格邊) - 1D 邊元素 (Edges)
- ✅ **Grid Vertices** (網格頂點) - 0D 節點元素 (Nodes/Vertices)
- ✅ **CF Conventions** - UGRID 的母標準

### 高階概念

- ✅ **Mesh Topology** (網格拓撲) - 元素之間的連線關係
- ✅ **Unstructured Grid** (非結構化網格) - 主要應用場景
- ✅ **Flexible Mesh** (靈活網格) - 支援多種網格型別
- ✅ **Connectivity** (連線性) - 元素之間的對映關係
- ✅ **Data Location** (資料位置) - 資料定義在哪個元素上

### 實現相關

- ✅ **Conventions Attribute** - 標準宣告
- ✅ **cf_role** - 變數角色定義
- ✅ **topology_dimension** - 網格維度
- ✅ **node_coordinates** - 節點座標
- ✅ **face_node_connectivity** - 面-節點連線性

---

## ✅ **UGRID 定義狀態**

**UGRID Conventions 已被清楚定義！**

| 方面 | 狀態 | 說明 |
| ------ | ------ | ------ |
| **官方標準** | ✅ 已定義 | UGRID v1.0 是官方標準 |
| **CF 整合** | ✅ 已整合 | 自 CF v1.11 起完全整合 |
| **文件完整性** | ✅ 完整 | 官方文件齊全 |
| **社群採用** | ✅ 廣泛 | 多個領域採用 |
| **工具支援** | ✅ 成熟 | 多個工具支援 |

### 官方資訊

- **官方版本**: v1.0
- **官方文件**: [ugrid-conventions.github.io](https://ugrid-conventions.github.io/ugrid-conventions/)
- **GitHub 倉庫**: [ugrid-conventions/ugrid-conventions](https://github.com/ugrid-conventions/ugrid-conventions)
- **CF 整合版本**: CF v1.11+

---

## 📊 **文件統計**

| 分類 | 檔案數 | 狀態 |
| ------ | -------- | ------ |
| 入門指南 | 3/3 | ✅ 完成 |
| 核心規範 | 1/6 | 🟡 進行中 |
| 實現指南 | 0/3 | ⏳ 待建立 |
| 技術細節 | 0/3 | ⏳ 待建立 |
| 資源工具 | 0/3 | ⏳ 待建立 |
| **總計** | **4/18** | 🟡 進行中 |

---

## 🎓 **學習路徑**

### 🐣 **新手路徑** (預計時間: 1-2 小時)

```text
概述 → 與 CF 的關係 → 核心概念 → 1D 網路拓撲
   ↓
快速驗證 → 簡單示例
```

### 👨‍💻 **開發者路徑** (預計時間: 3-5 小時)

```text
核心概念 → 命名約定 → 1D 網路 → 2D 三角形
   ↓
資料定義 → 體積通量 → 位置索引集
   ↓
符合性檢查 → 最佳實踐
```

### 🏗️ **專家路徑** (預計時間: 8+ 小時)

```text
所有核心規範 → 所有拓撲型別 → 所有資料定義
   ↓
技術細節 → 實現指南 → 工具使用
   ↓
高階應用 → 貢獻程式碼
```

---

## 🔗 **官方資源連結**

### UGRID 官方資源

- [UGRID Conventions 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/)
- [UGRID GitHub 倉庫](https://github.com/ugrid-conventions/ugrid-conventions)
- [UGRID 符合性文件](https://ugrid-conventions.github.io/ugrid-conventions/conformance/)

### CF 官方資源

- [CF Conventions 官方網站](https://cfconventions.org/)
- [CF 文件 - UGRID 部分](https://cfconventions.org/cf-conventions/cf-conventions.html#ugrid-conventions)
- [CF GitHub 倉庫](https://github.com/cf-convention/cf-conventions)

### 工具與驗證

- [IOOS Compliance Checker](https://compliance.ioos.us/)
- [cf-checker](https://github.com/cedadev/cf-checker)
- [NetCDF 官方網站](https://www.unidata.ucar.edu/software/netcdf/)

---

## 📝 **文件約定**

### 符號說明

- ✅ - 推薦/最佳實踐
- ⚠️ - 重要注意事項
- ❌ - 禁止/錯誤做法
- 🔗 - 相關連結
- 📖 - 文件/參考
- 🎯 - 核心概念

### 程式碼格式

- `code` - 變數名、屬性名
- **`bold code`** - 關鍵字、標準值

- ```cdl - CDL 程式碼塊

- ```python - Python 程式碼塊

### 結構約定

- 每個文件都有 **概述** 部分
- 每個概念都有 **定義** 和 **示例**
- 每個部分都有 **最佳實踐** 建議

---

## 🤝 **貢獻指南**

### 如何貢獻

1. Fork 倉庫
2. 建立特性分支
3. 提交變更
4. 建立 Pull Request

### 文件標準

- 使用 Markdown 格式
- 保持一致的結構和風格
- 包含示例和程式碼
- 提供清晰的解釋

### 貢獻者

- [使用者名稱] - 初始文件建立
- (歡迎更多貢獻者加入!)

---

*文件集合維護中... 最後更新: 2026-08-16*
