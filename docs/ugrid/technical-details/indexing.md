# UGRID 索引技術細節 (Indexing Technical Details)

## 📖 概述

索引（Indexing）是 UGRID 連線性系統的核心。本文件深入說明 UGRID 的索引機制、`start_index` 屬性的運作方式，以及在實際讀取和寫入時的注意事項。

## 1. 索引基礎

### 1.1 什麼是索引？

UGRID 連線性變數使用**整數索引**來引用其他維度的元素。例如：

```cdl
// 面-節點連線性：每個面 → 它的三個節點的索引
integer Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:start_index = 0 ;

data:
  Mesh2_face_nodes =
    0, 1, 3,   // Face 0 由 Node 0, Node 1, Node 3 組成
    1, 2, 3 ;  // Face 1 由 Node 1, Node 2, Node 3 組成
```

```text
           Node 2
            ○
           /|
          / |
         /  |
Node 0 ○───────○ Node 1
        Face 0  Face 1
```

### 1.2 start_index 屬性

`start_index` 定義了**索引的起始值**：

| `start_index` | 第一個元素的索引 | 最後一個元素的索引（共 N 個） |
| --------------- | ----------------- | ------------------------------ |
| 0 | 0 | N-1 |
| 1 | 1 | N |

```cdl
// ── 0-based 索引（推薦）────────────────────────
integer Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:start_index = 0 ;

data:
  // nMesh2_node = 5 → 有效索引為 0, 1, 2, 3, 4
  Mesh2_face_nodes = 0, 1, 3,   // ✅ 全部 ∈ [0, 4]
                     1, 2, 4 ;  // ✅

// ── 1-based 索引（Fortran 慣例）────────────────
integer Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:start_index = 1 ;

data:
  // nMesh2_node = 5 → 有效索引為 1, 2, 3, 4, 5
  Mesh2_face_nodes = 1, 2, 4,   // ✅ 全部 ∈ [1, 5]
                     2, 3, 5 ;  // ✅
```

## 2. 讀取索引的正確方式

### 2.1 Python（netCDF4）

```python
"""正確讀取 UGRID 連線性索引的方法。"""

import netCDF4 as nc
import numpy as np


def read_face_nodes_correctly(filename: str) -> np.ndarray:
    """讀取面-節點連線性並正規化為 0-based 索引。
    
    Args:
        filename: UGRID NetCDF 檔案路徑。
        
    Returns:
        0-based 的面-節點連線性陣列，shape: (nFace, nNodesPerFace)。
    """
    ds = nc.Dataset(filename)
    
    face_nodes_var = ds.variables['Mesh2_face_nodes']
    face_nodes = face_nodes_var[:].filled(-1)  # _FillValue → -1
    
    # ⚠️ 關鍵：讀取 start_index 屬性
    start_index = int(getattr(face_nodes_var, 'start_index', 0))
    
    # 正規化為 0-based
    if start_index != 0:
        # 只對有效（非 _FillValue）的索引做轉換
        valid_mask = face_nodes >= start_index
        face_nodes[valid_mask] -= start_index
    
    ds.close()
    return face_nodes


# ❌ 錯誤示例：忽略 start_index
def read_face_nodes_wrong(filename: str) -> np.ndarray:
    ds = nc.Dataset(filename)
    face_nodes = ds.variables['Mesh2_face_nodes'][:]
    # ← 如果 start_index=1，這裡的索引比實際大 1
    # 使用這些索引會造成「索引偏移」錯誤
    ds.close()
    return face_nodes
```

### 2.2 Python（xarray）

```python
import xarray as xr
import numpy as np


def read_with_xarray(filename: str) -> dict:
    """使用 xarray 讀取 UGRID 索引（注意 start_index 處理）。
    
    Args:
        filename: UGRID NetCDF 檔案路徑。
        
    Returns:
        包含 0-based 連線性的字典。
    """
    ds = xr.open_dataset(filename)
    
    face_nodes = ds['Mesh2_face_nodes'].values
    start_index = int(ds['Mesh2_face_nodes'].attrs.get('start_index', 0))
    
    if start_index != 0:
        fill_val = ds['Mesh2_face_nodes'].attrs.get('_FillValue', -9999)
        valid = face_nodes != fill_val
        face_nodes = np.where(valid, face_nodes - start_index, -1)
    
    return {'face_nodes': face_nodes, 'start_index': 0}
```

### 2.3 Fortran（NetCDF-4 介面）

```fortran
! 正確讀取 UGRID 連線性的 Fortran 示例
program read_ugrid
    use netcdf
    implicit none
    
    integer :: ncid, varid, status
    integer :: start_index
    integer, allocatable :: face_nodes(:,:)
    integer :: n_face, n_nodes_per_face
    
    ! 開啟檔案
    status = nf90_open('mesh.nc', NF90_NOWRITE, ncid)
    
    ! 取得連線性變數
    status = nf90_inq_varid(ncid, 'Mesh2_face_nodes', varid)
    
    ! ⚠️ 關鍵：讀取 start_index 屬性
    status = nf90_get_att(ncid, varid, 'start_index', start_index)
    if (status /= NF90_NOERR) start_index = 0   ! 預設為 0
    
    ! 讀取連線性資料
    allocate(face_nodes(n_nodes_per_face, n_face))
    status = nf90_get_var(ncid, varid, face_nodes)
    
    ! 正規化為 1-based（Fortran 慣例）
    if (start_index == 0) then
        face_nodes = face_nodes + 1   ! 0-based → 1-based
    end if
    ! 若 start_index == 1，無需調整（Fortran 自然 1-based）
    
    status = nf90_close(ncid)
end program
```

## 3. 寫入索引的正確方式

### 3.1 選擇索引約定

```python
"""選擇並一致使用索引約定的最佳實踐。"""

import netCDF4 as nc
import numpy as np


def write_ugrid_with_index_convention(
    filename: str,
    face_nodes_0based: np.ndarray,
    use_0based: bool = True
) -> None:
    """寫入 UGRID 連線性，明確指定索引約定。
    
    Args:
        filename: 輸出 NetCDF 檔案路徑。
        face_nodes_0based: 0-based 的面-節點連線性。
        use_0based: True 寫入 0-based（推薦），False 寫入 1-based。
    """
    ds = nc.Dataset(filename, 'w', format='NETCDF4')
    
    n_face, n_per_face = face_nodes_0based.shape
    ds.createDimension('nMesh2_face', n_face)
    ds.createDimension('Three', n_per_face)
    
    face_nodes_var = ds.createVariable(
        'Mesh2_face_nodes', 'i4', ('nMesh2_face', 'Three'))
    face_nodes_var.cf_role = "face_node_connectivity"
    
    if use_0based:
        face_nodes_var.start_index = 0
        face_nodes_var[:] = face_nodes_0based
    else:
        face_nodes_var.start_index = 1
        face_nodes_var[:] = face_nodes_0based + 1  # 轉換為 1-based
    
    ds.close()
```

## 4. 可變長度陣列與 _FillValue

當面的節點數不固定時（混合三角形和四邊形），需要使用 `_FillValue` 填充不需要的位置：

```python
"""處理可變長度陣列的示例。"""

import netCDF4 as nc
import numpy as np


def write_mixed_mesh(filename: str, faces: list[list[int]]) -> None:
    """寫入包含混合多邊形的網格。
    
    Args:
        filename: 輸出 NetCDF 檔案路徑。
        faces: 每個面的節點索引列表（長度可不同）。
    """
    FILL_VALUE = -9999   # 填充值（不得與有效索引混淆）
    
    # 計算最大節點數
    max_nodes = max(len(f) for f in faces)
    n_face = len(faces)
    
    # 建立填充後的陣列
    face_nodes = np.full((n_face, max_nodes), FILL_VALUE, dtype=np.int32)
    for i, face in enumerate(faces):
        face_nodes[i, :len(face)] = face
    
    ds = nc.Dataset(filename, 'w', format='NETCDF4')
    ds.createDimension('nMesh2_face', n_face)
    ds.createDimension('nMaxNodesPerFace', max_nodes)
    
    var = ds.createVariable(
        'Mesh2_face_nodes', 'i4', ('nMesh2_face', 'nMaxNodesPerFace'),
        fill_value=FILL_VALUE
    )
    var.cf_role = "face_node_connectivity"
    var.start_index = 0
    # ⚠️ 注意：_FillValue 必須不等於任何有效索引
    # 有效索引 ≥ 0（0-based），所以 FILL_VALUE = -9999 是安全的
    var[:] = face_nodes
    
    ds.close()


def read_mixed_mesh(filename: str) -> list[list[int]]:
    """讀取包含混合多邊形的網格，還原為 Python 列表。
    
    Args:
        filename: UGRID NetCDF 檔案路徑。
        
    Returns:
        每個面的節點索引列表（已去除填充值）。
    """
    ds = nc.Dataset(filename)
    var = ds.variables['Mesh2_face_nodes']
    face_nodes_raw = var[:].data  # 原始數據，包含 _FillValue
    fill_value = var._FillValue
    start_index = int(getattr(var, 'start_index', 0))
    
    faces = []
    for row in face_nodes_raw:
        # 過濾掉填充值，並轉換為 0-based
        valid = row[row != fill_value]
        faces.append((valid - start_index).tolist())
    
    ds.close()
    return faces
```

## 5. 位置索引集的索引語義

位置索引集（`cf_role = "location_index_set"`）中的索引含義稍有不同：

```python
"""正確使用位置索引集的示例。"""

import netCDF4 as nc
import numpy as np


def apply_location_index_set(filename: str) -> None:
    """示範位置索引集如何映射資料到完整網格。"""
    ds = nc.Dataset(filename)
    
    # 找到索引集變數
    obs_indices_var = ds.variables['obs_face_indices']
    obs_indices = obs_indices_var[:].data  # 例如: [10, 25, 42, 78]
    start_index = int(getattr(obs_indices_var, 'start_index', 0))
    obs_indices_0based = obs_indices - start_index
    
    # 讀取稀疏資料（只有 50 個面的溫度）
    sparse_temp = ds.variables['obs_temperature'][0, :]  # (nObs_face,)
    
    # 讀取完整網格的面座標
    all_face_lon = ds.variables['Mesh2_face_lon'][:]   # (nAllFace,)
    all_face_lat = ds.variables['Mesh2_face_lat'][:]
    
    # 用索引集提取對應位置的座標
    obs_lon = all_face_lon[obs_indices_0based]  # 50 個觀測站的經度
    obs_lat = all_face_lat[obs_indices_0based]  # 50 個觀測站的緯度
    
    # 如需要，也可以展開為完整網格（填充缺失值）
    n_total_face = len(all_face_lon)
    full_temp = np.full(n_total_face, np.nan)
    full_temp[obs_indices_0based] = sparse_temp  # 只填入有觀測的位置
    
    ds.close()
    print(f"觀測站數: {len(obs_indices_0based)}")
    print(f"完整網格面數: {n_total_face}")
    print(f"稀疏率: {len(obs_indices_0based)/n_total_face:.1%}")
```

## 6. 常見索引錯誤與除錯

### 6.1 索引偏移（off-by-one）

最常見的錯誤：忽略 `start_index`。

```python
# 診斷索引偏移的方法
def diagnose_index_error(filename: str) -> None:
    ds = nc.Dataset(filename)
    var = ds.variables['Mesh2_face_nodes']
    data = var[:].data
    start_idx = int(getattr(var, 'start_index', 0))
    
    # 對應的節點數量
    n_nodes = ds.dimensions['nMesh2_node'].size
    
    # 有效範圍
    valid_min = start_idx
    valid_max = start_idx + n_nodes - 1
    
    # 忽略 _FillValue 的有效索引
    fill_val = getattr(var, '_FillValue', -9999)
    valid_data = data[data != fill_val]
    
    print(f"start_index: {start_idx}")
    print(f"有效索引範圍: [{valid_min}, {valid_max}]")
    print(f"實際索引範圍: [{valid_data.min()}, {valid_data.max()}]")
    
    out_of_range = (valid_data < valid_min) | (valid_data > valid_max)
    if out_of_range.any():
        print(f"⚠️ 發現 {out_of_range.sum()} 個超出範圍的索引！")
    else:
        print("✅ 所有索引在有效範圍內")
    
    ds.close()
```

### 6.2 _FillValue 與有效索引重疊

```python
# 檢查 _FillValue 是否與有效索引衝突
def check_fill_value_conflict(filename: str) -> None:
    ds = nc.Dataset(filename)
    var = ds.variables['Mesh2_face_nodes']
    
    start_idx = int(getattr(var, 'start_index', 0))
    n_nodes = ds.dimensions['nMesh2_node'].size
    fill_val = getattr(var, '_FillValue', None)
    
    if fill_val is not None:
        valid_min = start_idx
        valid_max = start_idx + n_nodes - 1
        
        if valid_min <= fill_val <= valid_max:
            print(f"❌ 危險：_FillValue={fill_val} 落在有效索引範圍 "
                  f"[{valid_min}, {valid_max}] 內！")
            print(f"   建議改用負數 _FillValue，例如 -1 或 -9999")
        else:
            print(f"✅ _FillValue={fill_val} 安全（不在有效索引範圍內）")
    
    ds.close()
```

## 🔗 相關文件

- [位置索引集](../conventions/location-index-set.md) — 稀疏資料的索引集用法
- [符合性要求](../implementation/conformance.md) — 索引相關的規範要求
- [最佳實踐](../implementation/best-practices.md) — 索引選擇建議

## 📚 參考資源

- [UGRID 規範 - Connectivity](https://ugrid-conventions.github.io/ugrid-conventions/#connectivity)
- [CF Conventions - Compression by Gathering](https://cfconventions.org/cf-conventions/cf-conventions.html#compression-by-gathering)
- [NetCDF Best Practices - Fill Values](https://www.unidata.ucar.edu/software/netcdf/docs/fill_values.html)

---

*下一步*: [後設資料屬性](metadata-attributes.md) | [座標系統](coordinate-systems.md)
