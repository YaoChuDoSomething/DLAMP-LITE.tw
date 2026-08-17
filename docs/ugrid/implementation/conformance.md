# UGRID 符合性要求 (Conformance Requirements)

## 📖 概述

本文件定義了一個 NetCDF 檔案**符合 UGRID 規範**的最低要求。這些要求分為三級：

- **✅ 必需 (Required)**：不滿足則不符合規範
- **⚠️ 建議 (Recommended)**：強烈建議，但非強制
- **💡 可選 (Optional)**：提供額外功能，視需求而定

> ⚠️ **前提**：UGRID 1.0 自 **CF v1.11** 起已整合入 CF 規範。全域屬性應使用 `Conventions = "CF-1.11"` 或更高版本。

## 📋 全域規範

### G1. Conventions 屬性

```cdl
// ✅ 必需
:Conventions = "CF-1.12" ;    // CF v1.11+ 自動支援 UGRID

// ❌ 錯誤示例
:Conventions = "UGRID-1.0" ; // 舊式寫法，不再適用
```

### G2. 全域後設資料

```cdl
// ⚠️ 建議提供以下全域屬性
:title = "..." ;
:institution = "..." ;
:source = "..." ;
:history = "..." ;
:references = "..." ;
:comment = "..." ;
```

## 📋 網格拓撲變數要求

### T1. cf_role 屬性

```cdl
// ✅ 必需：每個網格拓撲變數必須設置 cf_role
integer Mesh2 ;
  Mesh2:cf_role = "mesh_topology" ;  // ← 必需
```

**違規示例**：

```cdl
// ❌ 缺少 cf_role
integer Mesh2 ;
  Mesh2:topology_dimension = 2 ;
  Mesh2:node_coordinates = "..." ;
  // 無 cf_role → 工具無法識別此變數為網格拓撲
```

### T2. topology_dimension 屬性

```cdl
// ✅ 必需：必須為整數 1、2 或 3
Mesh:topology_dimension = 2 ;

// ❌ 錯誤：浮點數
Mesh:topology_dimension = 2.0 ;

// ❌ 錯誤：超出範圍
Mesh:topology_dimension = 4 ;
```

### T3. node_coordinates 屬性

```cdl
// ✅ 必需：指向至少兩個（2D/3D）或一個（1D）座標變數
Mesh2:node_coordinates = "Mesh2_node_x Mesh2_node_y" ;

// ✅ 3D 網格必須包含 z 座標
Mesh3:node_coordinates = "Mesh3_node_x Mesh3_node_y Mesh3_node_z" ;
```

### T4. 連線性屬性（依 topology_dimension）

| `topology_dimension` | 必需屬性 |
|----------------------|----------|
| 1 | `edge_node_connectivity` |
| 2 | `face_node_connectivity` |
| 3 | `volume_node_connectivity` |

```cdl
// topology_dimension = 1 的必需屬性
integer Mesh1 ;
  Mesh1:topology_dimension = 1 ;
  Mesh1:edge_node_connectivity = "Mesh1_edge_nodes" ;  // ✅ 必需

// topology_dimension = 2 的必需屬性
integer Mesh2 ;
  Mesh2:topology_dimension = 2 ;
  Mesh2:face_node_connectivity = "Mesh2_face_nodes" ;  // ✅ 必需

// topology_dimension = 3 的必需屬性
integer Mesh3 ;
  Mesh3:topology_dimension = 3 ;
  Mesh3:volume_node_connectivity = "Mesh3_volume_nodes" ;  // ✅ 必需
```

## 📋 連線性變數要求

### C1. cf_role 屬性

每個連線性變數必須攜帶 `cf_role` 屬性：

```cdl
// ✅ 必需
integer Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:cf_role = "face_node_connectivity" ;  // ← 必需
```

### C2. 允許的 cf_role 值

| cf_role 值 | 描述 |
|------------|------|
| `edge_node_connectivity` | 邊-節點 |
| `face_node_connectivity` | 面-節點 |
| `volume_node_connectivity` | 體積-節點 |
| `face_edge_connectivity` | 面-邊 |
| `face_face_connectivity` | 面-面 |
| `edge_face_connectivity` | 邊-面 |
| `volume_face_connectivity` | 體積-面 |
| `volume_edge_connectivity` | 體積-邊 |
| `volume_volume_connectivity` | 體積-體積 |
| `boundary_node_connectivity` | 邊界-節點 |
| `volume_shape_type` | 體積形狀型別 |
| `location_index_set` | 位置索引集 |

### C3. start_index 屬性

```cdl
// ✅ 建議明確設置
integer Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
  Mesh2_face_nodes:start_index = 0 ;  // 建議明確指定

// ⚠️ 未設置時，預設為 0
// 💡 建議：始終明確設置，避免歧義
```

### C4. 索引範圍有效性

```
// ✅ 對於 start_index = 0：
所有索引值必須在 [0, nElement - 1] 範圍內

// ✅ 對於 start_index = 1：
所有索引值必須在 [1, nElement] 範圍內

// 或者等於 _FillValue（缺失值，用於可變長度陣列）
```

### C5. 可變長度陣列的 _FillValue

```cdl
// ✅ 當使用 _FillValue 時，必須明確定義
integer Mesh2_face_nodes(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_nodes:_FillValue = -999 ;    // ← 必須明確設置

// ❌ 不能依賴預設的 _FillValue（不同工具的預設值不同）
```

## 📋 節點座標變數要求

### NC1. 維度

節點座標變數的唯一維度必須是**節點維度**：

```cdl
// ✅ 正確
double Mesh2_node_x(nMesh2_node) ;

// ❌ 錯誤：多維節點座標
double Mesh2_node_x(nMesh2_node, nTime) ;
```

### NC2. 座標屬性

```cdl
// ✅ 建議提供 standard_name 和 units
double Mesh2_node_x(nMesh2_node) ;
  Mesh2_node_x:standard_name = "longitude" ;   // 建議
  Mesh2_node_x:units = "degrees_east" ;         // 建議
  Mesh2_node_x:long_name = "..." ;              // 建議
```

### NC3. 座標系標識

```cdl
// ✅ 建議：使用 grid_mapping 屬性指定投影
double Mesh2_node_x(nMesh2_node) ;
  Mesh2_node_x:grid_mapping = "crs" ;

// 對應的座標參考系統變數
char crs ;
  crs:grid_mapping_name = "transverse_mercator" ;
  crs:semi_major_axis = 6378137.0 ;
  // ...
```

## 📋 資料變數要求

### D1. mesh 屬性

```cdl
// ✅ 必需：指向現有的網格拓撲變數
double temperature(time, nMesh2_face) ;
  temperature:mesh = "Mesh2" ;     // ← 必需，且 "Mesh2" 必須存在

// ❌ 錯誤：指向不存在的網格變數
  temperature:mesh = "NonExistentMesh" ;
```

### D2. location 屬性

```cdl
// ✅ 必需：必須是有效的位置型別
double temperature(time, nMesh2_face) ;
  temperature:location = "face" ;   // ✅ 有效

// ❌ 錯誤：無效的位置型別
  temperature:location = "cell" ;   // ❌ "cell" 不是 UGRID 位置
  temperature:location = "Face" ;   // ❌ 大小寫敏感
```

### D3. 維度與位置的一致性

資料變數的維度必須與 `location` 指定的位置一致：

```cdl
// ✅ 正確：location = "face"，維度包含 nMesh2_face
double temperature(time, nMesh2_face) ;
  temperature:location = "face" ;

// ❌ 錯誤：location = "face"，但使用了 nMesh2_node 維度
double temperature(time, nMesh2_node) ;
  temperature:location = "face" ;   // 矛盾！
```

### D4. coordinates 屬性（建議）

```cdl
// ✅ 建議：指定對應位置的座標
double temperature(time, nMesh2_face) ;
  temperature:location = "face" ;
  temperature:coordinates = "Mesh2_face_x Mesh2_face_y" ;  // 面座標

// 對於 3D 分層資料：
double salinity(time, nSigma, nMesh2_face) ;
  salinity:location = "face" ;
  salinity:coordinates = "sigma Mesh2_face_x Mesh2_face_y" ;
```

## 📋 位置索引集要求

### L1. cf_role 屬性

```cdl
// ✅ 必需
integer obs_indices(nObs) ;
  obs_indices:cf_role = "location_index_set" ;  // ← 必需
```

### L2. mesh 和 location 屬性

```cdl
// ✅ 必需
integer obs_indices(nObs) ;
  obs_indices:cf_role = "location_index_set" ;
  obs_indices:mesh = "Mesh2" ;        // ← 必需
  obs_indices:location = "face" ;     // ← 必需
```

### L3. 引用完整性

使用 `location_index_set` 的資料變數所引用的索引集必須存在：

```cdl
// ✅ 正確：obs_face_indices 已定義
integer obs_face_indices(nObs_face) ;
  obs_face_indices:cf_role = "location_index_set" ;
  obs_face_indices:mesh = "Mesh2" ;
  obs_face_indices:location = "face" ;

double temperature(time, nObs_face) ;
  temperature:location_index_set = "obs_face_indices" ;  // ✅ 存在

// ❌ 錯誤：索引集變數不存在
double temperature(time, nObs_face) ;
  temperature:location_index_set = "undefined_indices" ; // ❌ 不存在
```

## 🔍 符合性驗證清單

### 快速檢查清單

```
網格拓撲變數
□ cf_role = "mesh_topology"
□ topology_dimension 為整數 1、2 或 3
□ node_coordinates 存在且指向有效變數
□ 依 topology_dimension 必需的連線性屬性已設置

連線性變數
□ cf_role 屬性存在且值有效
□ start_index 已明確設置
□ 可變長度陣列設置了 _FillValue
□ 索引值在有效範圍內

資料變數
□ mesh 屬性存在且指向有效網格拓撲變數
□ location 屬性存在且值為有效位置型別
□ 維度與 location 一致
□ coordinates 屬性正確（建議）

全域屬性
□ Conventions 包含 CF-1.11 或更高版本
□ 建議的後設資料屬性已提供
```

## 🛠️ 驗證工具

### cf-checker

CF Conventions 官方驗證工具，也支援 UGRID：

```bash
# 安裝
pip install cfchecker

# 驗證
cfchecker my_ugrid_file.nc
```

### UGRID 線上驗證器

- [CF Compliance Checker](https://cfconventions.org/compliance-checker.html)
- 支援上傳 NetCDF 檔案並自動驗證

### Python 手動驗證示例

```python
import netCDF4 as nc

def check_ugrid_conformance(filename):
    """基本 UGRID 符合性檢查。"""
    ds = nc.Dataset(filename)
    errors = []
    warnings = []
    
    # 全域屬性
    conventions = ds.getncattr('Conventions') if hasattr(ds, 'Conventions') else ''
    if 'CF-1.11' not in conventions and 'CF-1.12' not in conventions:
        warnings.append("Conventions 建議使用 CF-1.11 或更高版本")
    
    # 查找網格拓撲變數
    mesh_vars = []
    for vname, var in ds.variables.items():
        if hasattr(var, 'cf_role') and var.cf_role == 'mesh_topology':
            mesh_vars.append(vname)
    
    if not mesh_vars:
        errors.append("未找到網格拓撲變數 (cf_role = 'mesh_topology')")
        return errors, warnings
    
    for mesh_name in mesh_vars:
        mesh = ds.variables[mesh_name]
        
        # 檢查 topology_dimension
        if not hasattr(mesh, 'topology_dimension'):
            errors.append(f"{mesh_name}: 缺少 topology_dimension")
        else:
            dim = int(mesh.topology_dimension)
            if dim not in (1, 2, 3):
                errors.append(f"{mesh_name}: topology_dimension 必須為 1、2 或 3")
        
        # 檢查 node_coordinates
        if not hasattr(mesh, 'node_coordinates'):
            errors.append(f"{mesh_name}: 缺少 node_coordinates")
    
    ds.close()
    return errors, warnings
```

## 🔗 相關文件

- [核心概念](../conventions/core-concepts.md) — 屬性定義完整列表
- [最佳實踐](best-practices.md) — 超越最低要求的建議
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/) — 規範原文

## 📚 參考資源

- [UGRID Conformance Requirements](https://ugrid-conventions.github.io/ugrid-conventions/#conformance)
- [CF Conventions Conformance](https://cfconventions.org/cf-conventions/conformance.html)
- [cfchecker 工具](https://github.com/cedadev/cf-checker)

---

*下一步*: [最佳實踐](best-practices.md) | [1D 網路示例](examples/1d-network-example.md)
