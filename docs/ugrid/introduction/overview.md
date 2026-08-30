# UGRID 概述

## 🎯 什麼是 UGRID Conventions？

**UGRID Conventions** 是一個用於在 **NetCDF** 檔案中儲存 **非結構化網格 (Unstructured Grid)** 或 **靈活網格 (Flexible Mesh)** 模型資料的標準。它是 **Climate and Forecast (CF) Metadata Conventions** 的官方擴充套件，為 CF 規範增加了對複雜網格拓撲的支援能力。

## 🏗️ 解決的問題

傳統的 CF Conventions 主要針對結構化網格（如規則的經緯度網格），但現代的環境建模（海洋、大氣、水文等）中，越來越多地使用非結構化網格，例如：

- **三角形網格**: 常用於海岸線複雜的區域
- **四邊形混合網格**: 結合不同形狀的網格單元
- **1D 網路**: 河流、管道系統
- **3D 分層網格**: 垂直方向分層的非結構化水平網格
- **完全 3D 非結構化網格**: 複雜的三維結構

UGRID 為這些複雜的網格型別提供了標準化的後設資料定義。

## 🔧 技術特點

### 1. 幾何元素層次

UGRID 定義了一個清晰的幾何元素層次結構：

```test
Node (節點/頂點, 0D)
    ↓
Volume (體積, 3D)
    ↓
Face (面, 2D)
    ↓
Edge (邊, 1D)
    ↓
Node (節點/頂點, 0D)
```

每個維度的元素都有明確的定義和連線關係。

### 2. 拓撲描述

UGRID 使用 **連線性變數 (Connectivity Variables)** 來描述網格元素之間的關係：

- **`node_coordinates`**: 指向節點座標變數
- **`edge_node_connectivity`**: 描述邊與節點的連線
- **`face_node_connectivity`**: 描述面與節點的連線
- **`face_edge_connectivity`**: 描述面與邊的連線
- **`volume_node_connectivity`**: 描述體積與節點的連線

### 3. 資料位置

UGRID 支援在不同網格位置上定義資料：

- **節點資料**: 定義在網格節點上
- **邊資料**: 定義在網格邊上
- **面資料**: 定義在網格面上
- **體積資料**: 定義在網格體積上

## 📋 UGRID 檔案結構

一個典型的 UGRID 檔案包含以下元件：

### 1. 網格拓撲變數 (Mesh Topology Variable)

這是一個 **虛擬變數 (Dummy Variable)**，包含描述網格拓撲的屬性：

```cdl
topology_dimension = 2 ;
cf_role = "mesh_topology" ;
node_coordinates = "mesh_node_x mesh_node_y" ;
face_node_connectivity = "mesh_face_nodes" ;
edge_node_connectivity = "mesh_edge_nodes" ;  // 可選
```

### 2. 座標變數 (Coordinate Variables)

描述網格節點的空間位置：

```cdl
double mesh_node_x(nMesh_node) ;
  mesh_node_x:standard_name = "longitude" ;
  mesh_node_x:units = "degrees_east" ;

double mesh_node_y(nMesh_node) ;
  mesh_node_y:standard_name = "latitude" ;
  mesh_node_y:units = "degrees_north" ;
```

### 3. 連線性變數 (Connectivity Variables)

描述網格元素之間的連線關係：

```cdl
int mesh_face_nodes(nMesh_face, nMaxNodesPerFace) ;
  mesh_face_nodes:cf_role = "face_node_connectivity" ;
  mesh_face_nodes:start_index = 0 ;  // 0-based 或 1-based 索引
  mesh_face_nodes:_FillValue = 999999 ;
```

### 4. 資料變數 (Data Variables)

實際的模型資料，關聯到特定的網格位置：

```cdl
double water_level(time, nMesh_face) ;
  water_level:standard_name = "sea_surface_height_above_geoid" ;
  water_level:units = "m" ;
  water_level:mesh = "mesh2d" ;  // 關聯到網格拓撲
  water_level:location = "face" ;  // 資料定義在面上
  water_level:coordinates = "mesh_face_x mesh_face_y" ;
```

## 🔄 與 CF Conventions 的整合

UGRID 與 CF Conventions 的關係經歷了幾個階段：

### CF v1.6 及之前

- 需要顯式宣告: `Conventions = "CF-1.6, UGRID-1.0"`
- UGRID 是獨立的擴充套件

### CF v1.7 - v1.10

- UGRID 1.0 被引用但未完全整合
- 仍然推薦顯式宣告 UGRID

### CF v1.11 及之後 ✅

- **UGRID 1.0 完全整合到 CF 規範中**
- 只需要宣告: `Conventions = "CF-1.11"` 或更高版本
- 不需要顯式宣告 UGRID

## 🎯 主要應用領域

UGRID 廣泛應用於以下領域：

1. **海洋模型**
   - SELFE (Semi-implicit Eulerian-Lagrangian Finite-Element)
   - ELCIRC (Eulerian-Lagrangian Circulation)
   - FVCOM (Finite Volume Community Ocean Model)
   - ADCIRC (ADvanced CIRCulation)

2. **水文模型**
   - 河流網路
   - 洪水模擬
   - 地下水模型

3. **大氣模型**
   - 區域氣候模型
   - 空氣質量模型

4. **其他領域**
   - 工程模擬
   - 地質建模
   - 生物地球化學模型

## 📊 UGRID vs 其他網格標準

| 特性 | UGRID | CF (傳統) | GridSpec | SGRID |
| --- | --- | --- | --- | --- |
| 非結構化網格 | ✅ | ❌ | ✅ | ✅ |
| 結構化網格 | ✅ | ✅ | ✅ | ❌ |
| CF 整合 | ✅ | ✅ | ❌ | ❌ |
| 拓撲描述 | ✅ | ❌ | ✅ | ✅ |
| 多維度支援 | ✅ | ❌ | ✅ | ✅ |
| 官方標準 | ✅ | ✅ | ❌ | ❌ |

## 🚀 為什麼選擇 UGRID？

1. **官方認可**: CF 官方擴充套件，具有權威性
2. **社群支援**: 廣泛的建模社群採用
3. **靈活性**: 支援各種複雜的網格型別
4. **相容性**: 與現有 CF 工具完全相容
5. **標準化**: 提供清晰的後設資料定義
6. **互操作性**: 不同軟體之間可以交換資料

## 📚 學習資源

- [官方文件](https://ugrid-conventions.github.io/ugrid-conventions/)
- [GitHub 倉庫](https://github.com/ugrid-conventions/ugrid-conventions)
- [CF 官方文件](https://cfconventions.org/)
- [UGRID Google Group](https://groups.google.com/forum/#!forum/ugrid-interoperability)

## 💡 快速驗證

要驗證一個 NetCDF 檔案是否符合 UGRID 標準：

1. 檢查是否有 `cf_role = "mesh_topology"` 屬性
2. 檢查是否有 `topology_dimension` 屬性
3. 檢查是否有 `node_coordinates` 屬性
4. 檢查是否有 `*_node_connectivity` 屬性
5. 檢查資料變數是否有 `mesh` 和 `location` 屬性

✅ 如果以上條件都滿足，那麼檔案很可能符合 UGRID 標準。

---

*下一步*: [開發歷史](history.md) | [與 CF 的關係](relationship-with-cf.md)
