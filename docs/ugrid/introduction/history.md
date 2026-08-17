# UGRID 開發歷史與版本演進

## 📜 起源與背景

### 問題的提出

在 2000 年代早期，環境建模社群（特別是海洋和水文模型）開始廣泛使用 **非結構化網格 (Unstructured Meshes)**。這些模型需要更靈活的空間離散化方法來處理：

- 複雜的海岸線
- 不規則的地形
- 區域性精細化的網格
- 多尺度的物理過程

然而，當時的 **CF Conventions (v1.0-1.4)** 主要針對 **結構化網格 (Structured Grids)**，即規則的經緯度網格或曲線座標網格。對於非結構化網格資料，缺乏標準化的後設資料定義，導致：

- ❌ 資料交換困難
- ❌ 不同軟體之間相容性差
- ❌ 缺乏統一的資料描述方式
- ❌ 難以開發通用的視覺化和分析工具

### 早期嘗試

在 UGRID 之前，有幾個嘗試試圖解決非結構化網格資料的標準化問題：

1. **GridSpec (2004)**
   - 由 Venkatramani Balaji (GFDL/NOAA) 提出
   - 提供了非結構化網格的後設資料框架
   - 但未被廣泛採用

2. **各模型自定義格式**
   - SELFE、FVCOM、ADCIRC 等模型各自開發了自己的 NetCDF 輸出格式
   - 導致資料碎片化

3. **CF 的擴充套件討論**
   - CF 社群意識到需要支援非結構化網格
   - 但直接擴充套件 CF 被認為過於複雜

## 🤝 社群協作

### UGRID Google Group (2007-2010)

2007 年左右，一群來自不同建模社群的研究人員和工程師組建了 **UGRID Interoperability Google Group**，目標是開發一個通用的非結構化網格資料標準。

**主要參與者包括**：

- Bert Jagers (Deltares) - 主要貢獻者
- David Stuebe (USGS)
- Tom Gross (USGS)
- Chris Barker (NOAA)
- Brian Zelenke (ACES)
- Rich Signell (USGS)
- Bob Oehmke (PNNL)
- 以及來自 SELFE、ELCIRC、FVCOM、ADCIRC 等模型社群的成員

### 討論焦點

社群討論主要集中在以下問題：

1. **幾何元素命名**: node/vertex, edge, face, volume
2. **連線性表示**: 如何描述元素之間的關係
3. **資料位置**: 如何表示資料定義在哪個幾何元素上
4. **CF 相容性**: 如何與現有 CF 規範整合
5. **索引方式**: 0-based vs 1-based 索引
6. **座標系統**: 支援各種座標系

## 🏗️ 標準開發

### 初始草案 (2008-2009)

Bert Jagers 基於社群討論，建立了 UGRID 的第一個草案版本。這個草案：

- 定義了基本的幾何元素層次 (node, edge, face)
- 提出了連線性變數的概念
- 定義了網格拓撲變數的屬性
- 提供了簡單的 2D 示例

### 公開徵求意見 (2009-2010)

草案版本在社群中廣泛徵求意見，收到了來自各個模型社群的反饋和建議。主要修改包括：

- 增加了 3D 支援
- 完善了連線性變數的定義
- 增加了資料位置屬性 (`mesh`, `location`)
- 改進了與 CF 的整合方式
- 增加了各種網格型別的示例

### 正式釋出 v1.0 (2010)

經過多輪修訂和社群驗證，UGRID Conventions **v1.0** 於 2010 年正式釋出。

**v1.0 的主要特性**：

- ✅ 支援 1D、2D、3D 網格
- ✅ 支援混合網格型別
- ✅ 詳細的拓撲描述
- ✅ 與 CF v1.6 相容
- ✅ 完整的符合性定義

## 🔄 版本演進

### v1.0 (2010) - 初始版本

- **狀態**: 穩定版
- **CF 相容性**: CF-1.6 (需要顯式宣告)
- **主要貢獻者**: Bert Jagers, David Stuebe, Tom Gross 等
- **文件位置**: [ugrid-conventions.github.io](https://ugrid-conventions.github.io/ugrid-conventions/)

**v1.0 的核心貢獻**：

1. 定義了標準的幾何元素命名
2. 建立了連線性變數的框架
3. 定義了網格拓撲變數的屬性
4. 提供了資料在網格上的定義方式
5. 確立了與 CF 的整合路徑

### CF 整合過程

| CF 版本 | UGRID 狀態 | 說明 |
| ---------- | ------------ | ------ |
| CF-1.0-1.5 | ❌ 未整合 | 需要獨立使用 UGRID |
| CF-1.6 | ✅ 引用 | 可以宣告 `Conventions = "CF-1.6, UGRID-1.0"` |
| CF-1.7-1.10 | ✅ 引用 | UGRID 1.0 被引用但未完全整合 |
| **CF-1.11+** | **✅ 完全整合** | **UGRID 1.0 作為 CF 的一部分** |

### CF v1.11 的里程碑 (2023)

2023年12月，CF v1.11 正式釋出，其中 **完全整合了 UGRID 1.0 規範**：

> "These conventions implicitly incorporate parts of the UGRID conventions for storing unstructured (or flexible mesh) data in netCDF files using mesh topologies. Only version 1.0 of the UGRID conventions is allowed."

這意味著：

- ✅ 使用 `Conventions = "CF-1.11"` 就自動支援 UGRID 1.0
- ✅ 不再需要顯式宣告 UGRID
- ✅ UGRID 1.0 成為 CF 的官方組成部分
- ✅ UGRID 的所有標準化屬性都被 CF 採納

## 📊 影響與採用

### 社群採用

UGRID 被廣泛採用的領域：

1. **海洋模型**
   - SELFE 模型完全支援 UGRID
   - FVCOM 社群採用 UGRID
   - ADCIRC 社群採用 UGRID
   - ELCIRC 社群採用 UGRID

2. **水文模型**
   - USGS 的多個水文模型
   - Deltares 的 Delft3D 模型
   - TELEMAC 系統

3. **大氣模型**
   - 區域氣候模型 (RCM)
   - 空氣質量模型 (AQM)

4. **工具與庫**
   - xarray (透過 cf-xarray)
   - NetCDF-Fortran 庫
   - ParaView (透過 VTK)
   - VisIt
   - CDAT/CDO
   - NCO (NetCDF Operators)

### 標準影響

UGRID 對網格資料標準化的影響：

1. **統一了非結構化網格的後設資料定義**
2. **促進了不同模型之間的資料交換**
3. **推動了 CF 規範的發展**
4. **為其他網格標準提供了參考**
5. **促進了科學資料的 FAIR 原則 (Findable, Accessible, Interoperable, Reusable)**

## 🎓 主要貢獻者

以下人員對 UGRID 的開發做出了重要貢獻（按字母順序排列）：

### 核心貢獻者

- **Bert Jagers** (Deltares) - 主要作者，v1.0 的主要設計者
- **David Stuebe** (USGS) - 重要貢獻者
- **Tom Gross** (USGS) - 重要貢獻者

### 其他重要貢獻者

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

### 社群參與者

來自以下機構的研究人員和工程師參與了討論和測試：

- Deltares (荷蘭)
- USGS (美國地質調查局)
- NOAA (美國國家海洋和大氣管理局)
- PNNL (太平洋西北國家實驗室)
- 多個大學和研究機構
- 多個模型開發團隊

## 🏆 里程碑事件

| 日期 | 事件 | 重要性 |
| ------ | ------ | -------- |
| ~2007 | UGRID Google Group 成立 | 🌱 起源 |
| 2008 | Bert Jagers 建立初始草案 | 📝 起草 |
| 2009 | 社群廣泛討論和反饋 | 🗣️ 協作 |
| 2010 | **UGRID v1.0 正式釋出** | 🎉 里程碑 |
| 2010 | 官方文件網站上線 | 🌐 釋出 |
| 2010-2020 | 社群採用和工具支援 | 📈 增長 |
| 2023 | **CF v1.11 整合 UGRID** | 🏆 整合 |
| 2024 | 多個主流工具支援 UGRID | ✅ 成熟 |

## 🔮 未來展望

雖然 UGRID v1.0 已經非常穩定和廣泛採用，但仍然有一些改進空間：

### 已知限制 (Known Issues)

根據官方文件，以下功能在當前版本中尚未完全支援：

1. **自適應網格拓撲** (Adaptive mesh topology)
   - 可能透過定義 `time_concatenation` 屬性支援
   - 計劃在未來版本中增加

2. **高階元素資料** (Higher order element data)
   - 需要其他方案來儲存
   - 有提議但未實現

3. **子網格資料** (Subgrid data)
   - Bundesanstalt für Wasserbau (BAW) 有相關提議
   - 需要進一步開發

4. **3D 完全非結構化網格** (Fully 3D unstructured meshes)
   - 一些概念已包含，但範圍有限
   - 需要擴充套件

5. **多連通域** (Multiply-connected domains)
   - 當前支援有限

6. **幽靈元素** (Ghost elements)
   - 平行計算中的處理

### 可能的發展方向

1. **UGRID v2.0**
   - 解決已知限制
   - 增加新功能
   - 改進現有定義

2. **更好的 CF 整合**
   - 增加更多 UGRID 功能到 CF
   - 改進符合性檢查

3. **工具支援**
   - 更多視覺化工具
   - 更好的資料處理庫
   - 改進的驗證工具

4. **應用擴充套件**
   - 更多領域的採用
   - 更多模型的支援
   - 更好的最佳實踐

## 📚 參考資源

- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/)
- [UGRID GitHub 倉庫](https://github.com/ugrid-conventions/ugrid-conventions)
- [CF 官方文件 - UGRID 部分](https://cfconventions.org/cf-conventions/cf-conventions.html#ugrid-conventions)
- [UGRID Google Group (存檔)](https://groups.google.com/forum/#!forum/ugrid-interoperability)

---

*下一步*: [概述](overview.md) | [與 CF 的關係](relationship-with-cf.md)
