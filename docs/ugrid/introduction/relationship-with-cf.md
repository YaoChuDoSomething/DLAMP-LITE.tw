# UGRID 與 CF Conventions 的關係

## 🔗 官方整合狀態

**UGRID Conventions 已被 CF Conventions 官方整合！**

自 **CF v1.11** 起，UGRID 1.0 已成為 CF 規範的正式組成部分。這意味著 UGRID 不再是一個獨立的擴充套件，而是 CF 的一部分。

## 📋 官方宣告

來自 CF v1.12 文件的官方宣告：

> ### 1.6. UGRID Conventions
>
> These conventions implicitly incorporate parts of the UGRID conventions for storing unstructured (or flexible mesh) data in netCDF files using mesh topologies [[UGRID](#UGRID)]. **Only version 1.0 of the UGRID conventions is allowed.** The UGRID conventions description is referenced from, rather than rewritten into, this document and the canonical description of how to store mesh topologies is only to be found at [[UGRID](#UGRID)].

---

> A summary indicating how UGRID relates to other parts of the CF conventions, and which features of UGRID are excluded from CF, can be found in [Section 5.9, "Mesh Topology Variables"](#mesh-topology-variables). To reduce the chance of ambiguities arising from their accidental re-use, all of the UGRID standardized attributes are specified in [Appendix K, Mesh Topology Attributes](#appendix-mesh-topology-attributes) and [Appendix A, Attributes](#attribute-appendix).

---

> The UGRID conventions have their own conformance document, which should be used in conjunction with the CF conformance document when checking the validity of datasets.

## 🔄 整合時間線

| CF 版本 | 釋出日期 | UGRID 狀態 | Conventions 屬性要求 |
| ---------- | ---------- | ------------ | -------------------- |
| CF-1.0-1.5 | 2003-2011 | ❌ 未整合 | 需要獨立工具支援 |
| CF-1.6 | 2011-12-05 | ✅ 引用 | `Conventions = "CF-1.6, UGRID-1.0"` |
| CF-1.7 | 2017-08-07 | ✅ 引用 | `Conventions = "CF-1.7, UGRID-1.0"` |
| CF-1.8 | 2020-02-11 | ✅ 引用 | `Conventions = "CF-1.8, UGRID-1.0"` |
| CF-1.9 | 2021-09-10 | ✅ 引用 | `Conventions = "CF-1.9, UGRID-1.0"` |
| CF-1.10 | 2022-08-31 | ✅ 引用 | `Conventions = "CF-1.10, UGRID-1.0"` |
| **CF-1.11** | **2023-12-05** | **✅ 完全整合** | **`Conventions = "CF-1.11"`** ✅ |
| CF-1.12 | 2024-12-04 | ✅ 完全整合 | `Conventions = "CF-1.12"` |
| CF-1.13 | 2025-12-17 | ✅ 完全整合 | `Conventions = "CF-1.13"` |
| CF-1.14-draft | 2026-07-30 | ✅ 完全整合 | `Conventions = "CF-1.14-draft"` |

## 🎯 關鍵轉變

### CF v1.10 及之前

在 CF v1.10 及之前，UGRID 是一個 **獨立的擴充套件**，需要顯式宣告：

```netcdf
:Conventions = "CF-1.8, UGRID-1.0" ;
```

**特點**：

- UGRID 是 CF 的擴充套件
- 需要單獨維護符合性
- 工具需要同時支援 CF 和 UGRID

### CF v1.11 及之後 ✅

從 CF v1.11 開始，UGRID 1.0 **完全整合到 CF 規範中**：

```netcdf
:Conventions = "CF-1.11" ;  // 自動支援 UGRID 1.0
```

**特點**：

- UGRID 1.0 是 CF 的一部分
- 不需要顯式宣告 UGRID
- 使用 CF v1.11+ 的檔案自動支援網格拓撲
- 符合性檢查統一

## 📐 CF 中的 UGRID 整合點

### 1. 屬性標準化 (Appendix A & K)

CF 文件在 **Appendix A (Attributes)** 和 **Appendix K (Mesh Topology Attributes)** 中列出了所有 UGRID 標準化的屬性：

**UGRID 標準化屬性包括**：

#### 網格拓撲屬性 (Mesh Topology Attributes)

- `cf_role` - 定義變數的角色 (如 `mesh_topology`, `edge_node_connectivity`)
- `topology_dimension` - 網格的最高維度
- `node_coordinates` - 指向節點座標變數
- `edge_node_connectivity` - 指向邊-節點連線性變數
- `face_node_connectivity` - 指向面-節點連線性變數
- `volume_node_connectivity` - 指向體積-節點連線性變數
- `face_dimension` - 面的維度
- `edge_dimension` - 邊的維度
- `volume_dimension` - 體積的維度
- `face_edge_connectivity` - 指向面-邊連線性變數
- `face_face_connectivity` - 指向面-面連線性變數
- `edge_face_connectivity` - 指向邊-面連線性變數
- `boundary_node_connectivity` - 指向邊界-節點連線性變數
- `volume_shape_type` - 體積形狀型別
- `start_index` - 索引起始值 (0 或 1)

#### 資料位置屬性

- `mesh` - 指向關聯的網格拓撲變數
- `location` - 資料定義的位置 (node, edge, face, volume)
- `location_index_set` - 位置索引集

### 2. 網格拓撲變數 (Section 5.9)

CF v1.11+ 在 **Section 5.9 "Mesh Topology Variables"** 中詳細描述了網格拓撲變數的要求和用法。

**核心要求**：

- 網格拓撲變數必須有 `cf_role = "mesh_topology"`
- 必須有 `topology_dimension` 屬性
- 必須有 `node_coordinates` 屬性
- 必須有至少一個 `*_node_connectivity` 屬性

### 3. 符合性要求

UGRID 保留了自己的符合性文件，但 CF 文件現在也包含了相關的符合性要求：

- UGRID 符合性文件應該與 CF 符合性文件一起使用
- 使用 CF v1.11+ 檢查 UGRID 檔案時，兩個文件都需要參考

## 🔧 技術整合詳情

### 1. 屬性整合

UGRID 的所有標準化屬性都被 CF v1.11+ 採納，這意味著：

- ✅ CF 工具可以識別 UGRID 屬性
- ✅ UGRID 屬性在 CF 文件中有定義
- ✅ 不會與 CF 現有屬性衝突
- ✅ 屬性的語義在 CF 和 UGRID 中一致

### 2. 規範引用

CF v1.11+ 文件 **引用** UGRID 規範，而不是重寫：

> "The UGRID conventions description is referenced from, rather than rewritten into, this document and the canonical description of how to store mesh topologies is only to be found at [[UGRID](#UGRID)]."

這意味著：

- UGRID 的官方定義在 [ugrid-conventions.github.io](https://ugrid-conventions.github.io/ugrid-conventions/)
- CF 文件提供了 UGRID 的概述和整合方式
- 詳細的技術細節仍然在 UGRID 文件中

### 3. 版本限制

CF v1.11+ **只允許 UGRID v1.0**：

> "Only version 1.0 of the UGRID conventions is allowed."

這意味著：

- ✅ UGRID v1.0 是官方支援的版本
- ❌ UGRID v0.9 及更早版本不被 CF v1.11+ 支援
- ⚠️ 未來的 UGRID v2.0 需要 CF 的更新

## 📊 UGRID 在 CF 中的定位

### CF 的擴充套件機制

CF 採用了 **引用擴充套件** 的機制來整合 UGRID：

1. **引用外部標準**: CF 文件引用 UGRID 規範
2. **採納屬性定義**: CF 採納 UGRID 的標準化屬性
3. **提供整合指導**: CF 提供如何在 CF 檔案中使用 UGRID
4. **統一符合性**: CF 和 UGRID 的符合性檢查可以一起使用

### UGRID 相對於 CF 的其他部分

| CF 元件 | UGRID 整合 | 說明 |
| ---------- | ------------ | ------ |
| 核心屬性 | ✅ 完全整合 | 如 `Conventions`, `title`, `history` |
| 座標變數 | ✅ 完全整合 | UGRID 使用 CF 的座標變數定義 |
| 座標系統 | ✅ 完全整合 | 支援各種座標系統 |
| 單位定義 | ✅ 完全整合 | 使用 CF 的單位定義 |
| 標準名稱 | ✅ 完全整合 | 使用 CF 的標準名稱表 |
| 時間座標 | ✅ 完全整合 | 使用 CF 的時間座標定義 |
| 網格拓撲 | ✅ **UGRID 擴充套件** | UGRID 提供的功能 |
| 非結構化網格 | ✅ **UGRID 擴充套件** | UGRID 的核心功能 |

## ✅ 最佳實踐

### 對於資料生產者

1. **使用最新的 CF 版本**

   ```netcdf
   :Conventions = "CF-1.12" ;  // 推薦
   ```

2. **不需要顯式宣告 UGRID**

   ```netcdf
   // ✅ 正確 (CF v1.11+)
   :Conventions = "CF-1.12" ;
   
   // ❌ 不必要 (CF v1.11+)
   :Conventions = "CF-1.12, UGRID-1.0" ;
   ```

3. **確保符合 UGRID v1.0**
   - 使用 `cf_role = "mesh_topology"`
   - 定義 `topology_dimension`
   - 定義 `node_coordinates`
   - 定義連線性變數

4. **驗證檔案符合性**
   - 使用 CF 符合性檢查器
   - 使用 UGRID 符合性檢查器
   - 確保同時滿足 CF 和 UGRID 的要求

### 對於資料使用者

1. **檢查 CF 版本**

   ```python
   import netCDF4
   nc = netCDF4.Dataset('file.nc')
   conventions = nc.Conventions
   
   if 'CF-1.11' in conventions or 'CF-1.12' in conventions:
       # 支援 UGRID
       supports_ugrid = True
   else:
       # 需要檢查是否顯式宣告 UGRID
       supports_ugrid = 'UGRID' in conventions
   ```

2. **查詢網格拓撲變數**

   ```python
   # 查詢 cf_role = "mesh_topology" 的變數
   for var in nc.variables.values():
       if hasattr(var, 'cf_role') and var.cf_role == 'mesh_topology':
           mesh_var = var
           break
   ```

3. **使用 UGRID 相關工具**
   - xarray + cf-xarray
   - NetCDF-Fortran 庫
   - ParaView
   - VisIt

## 🔍 相容性檢查

### 檢查檔案是否支援 UGRID

1. **檢查 Conventions 屬性**

   ```bash
   ncdump -h file.nc | grep Conventions
   ```

2. **檢查網格拓撲變數**

   ```bash
   ncdump -h file.nc | grep cf_role
   ```

3. **使用 Python 檢查**

   ```python
   import netCDF4
   
   def is_ugrid_compliant(filepath):
       nc = netCDF4.Dataset(filepath)
       
       # 檢查 Conventions
       conventions = getattr(nc, 'Conventions', '')
       if 'CF-1.11' in conventions or 'UGRID' in conventions:
           # 檢查網格拓撲變數
           for var in nc.variables.values():
               if hasattr(var, 'cf_role') and var.cf_role == 'mesh_topology':
                   if hasattr(var, 'topology_dimension') and hasattr(var, 'node_coordinates'):
                       return True
       return False
   ```

### 驗證 UGRID 符合性

1. **官方 UGRID 符合性檢查器**
   - [ugrid-conventions/conformance](https://github.com/ugrid-conventions/ugrid-conventions/tree/master/conformance)

2. **CF 符合性檢查器**
   - [cf-checker](https://github.com/cedadev/cf-checker)
   - [Compliance Checker](https://compliance.ioos.us/)

3. **線上驗證工具**
   - [IOOS Compliance Checker](https://compliance.ioos.us/)

## 📖 CF 文件中的 UGRID 參考

### CF v1.12 中的 UGRID 相關部分

1. **Section 1.6 - UGRID Conventions**
   - UGRID 整合的概述
   - 版本要求
   - 符合性說明

2. **Section 5.9 - Mesh Topology Variables**
   - 網格拓撲變數的定義
   - 必需和可選屬性
   - 示例

3. **Appendix A - Attributes**
   - UGRID 標準化屬性的定義
   - 屬性值和用法

4. **Appendix K - Mesh Topology Attributes**
   - 所有 UGRID 屬性的詳細定義
   - 屬性之間的關係

## 🔗 重要連結

### CF 官方資源

- [CF Conventions 官方網站](https://cfconventions.org/)
- [CF v1.12 文件](https://cfconventions.org/cf-conventions/cf-conventions.html)
- [CF GitHub 倉庫](https://github.com/cf-convention/cf-conventions)

### UGRID 官方資源

- [UGRID Conventions 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/)
- [UGRID GitHub 倉庫](https://github.com/ugrid-conventions/ugrid-conventions)
- [UGRID 符合性文件](https://ugrid-conventions.github.io/ugrid-conventions/conformance/)

### 整合資源

- [CF 文件中關於 UGRID 的部分](https://cfconventions.org/cf-conventions/cf-conventions.html#ugrid-conventions)
- [CF 文件中關於網格拓撲的部分](https://cfconventions.org/cf-conventions/cf-conventions.html#mesh-topology-variables)
- [CF Appendix K - Mesh Topology Attributes](https://cfconventions.org/cf-conventions/cf-conventions.html#appendix-mesh-topology-attributes)

## ❓ 常見問題

### Q1: CF v1.11+ 是否完全相容 UGRID v1.0？

**A**: 是的。CF v1.11+ 完全整合了 UGRID v1.0，所有 UGRID v1.0 的功能都被支援。

### Q2: 我是否可以在 CF v1.8 檔案中使用 UGRID？

**A**: 可以，但需要顯式宣告：`Conventions = "CF-1.8, UGRID-1.0"`。

### Q3: 使用 CF v1.12 時是否還需要宣告 UGRID？

**A**: 不需要。CF v1.11+ 自動支援 UGRID 1.0，只需要宣告 CF 版本即可。

### Q4: 我如何知道我的檔案是否符合 UGRID 標準？

**A**: 使用 UGRID 符合性檢查器，或者檢查是否有 `cf_role = "mesh_topology"` 變數和相應的屬性。

### Q5: UGRID 是否支援 4D 網格？

**A**: UGRID v1.0 支援 1D、2D、3D 網格。4D 網格（如時間變化的網格）在當前版本中支援有限，屬於未來發展方向。

### Q6: 我可以使用 UGRID v0.9 嗎？

**A**: 在 CF v1.11+ 中，只有 UGRID v1.0 被官方支援。UGRID v0.9 被認為是過時的。

---

*下一步*: [概述](overview.md) | [歷史](history.md)
