# UGRID 常見問題 (Frequently Asked Questions)

## 📖 一般問題

### Q: UGRID 是什麼？它和 CF 規範是什麼關係？

**A:** UGRID（Unstructured Grid conventions）是一套在 NetCDF 檔案中表達**非結構化網格**資料的命名和後設資料規範。

自 **CF Conventions v1.11**（2023 年）起，UGRID 1.0 已正式整合入 CF 規範，成為其一部分。這意味著：

- 不需要再同時聲明 `Conventions = "CF-1.x UGRID-1.0"` — 只需 `CF-1.11` 或更高版本即可
- CF 的工具（如 cfchecker）已原生支援 UGRID 驗證

---

### Q: 非結構化網格和結構化網格有什麼區別？

**A:**

| 類別 | 結構化網格 | 非結構化網格 |
| --- | --- | --- |
| 拓撲 | 規則的行列（i,j,k） | 任意連線 |
| 元素 | 四邊形、六面體 | 三角形、多邊形、稜柱體 |
| 索引 | `(i, j)` 隱含連線 | 需要顯式連線性陣列 |
| 適用 | 大範圍、規則邊界 | 複雜海岸線、局部加密 |
| 例子 | ROMS, WRF | FVCOM, SCHISM, ADCIRC |

UGRID 專門處理非結構化網格（後者）。

---

### Q: UGRID 支援哪些維度的網格？

**A:** UGRID 支援 1D、2D 和 3D 網格：

- **1D 網格**（`topology_dimension = 1`）：節點（Nodes）+ 邊（Edges）→ 河道網路、管線
- **2D 網格**（`topology_dimension = 2`）：節點 + 邊 + 面（Faces）→ 三角形/四邊形網格
- **3D 網格**（`topology_dimension = 3`）：節點 + 邊 + 面 + 體積（Volumes）→ 真正 3D 網格

---

## 📋 規範問題

### Q: `start_index` 應該用 0 還是 1？

**A:** 強烈建議使用 **`start_index = 0`**（C 語言慣例），原因如下：

1. Python、C 等主流語言原生使用 0-based 索引，不需要轉換
2. UGRID 官方示例大多使用 0-based
3. 一致性：整個檔案只使用一種索引基準，避免混用錯誤

Fortran 使用者可能偏好 `start_index = 1`，但需要在讀取時做適當轉換。

> **最重要的原則**：在整個檔案中保持一致，並且**始終顯式設置** `start_index`，不要依賴預設值。

---

### Q: 面-節點連線性的節點順序（CCW vs CW）有規定嗎？

**A:** UGRID 規範**未強制**規定節點順序，但：

- **建議使用逆時針（CCW）順序**，因為許多有限體積法（FVM）依靠 CCW 順序計算面法向量
- FVCOM 等主流模型使用 CCW 順序
- 若使用順時針（CW）順序，應在 `long_name` 或全域屬性中說明

---

### Q: 一個 NetCDF 檔案可以包含多個 UGRID 網格嗎？

**A:** 可以。每個網格拓撲變數（`cf_role = "mesh_topology"`）代表一個獨立的網格。資料變數透過 `mesh` 屬性指定它屬於哪個網格：

```cdl
// 兩個網格
integer Mesh2_coarse ;   Mesh2_coarse:cf_role = "mesh_topology" ; ...
integer Mesh2_fine ;     Mesh2_fine:cf_role = "mesh_topology" ; ...

// 各自的資料
double temp_coarse(...) ; temp_coarse:mesh = "Mesh2_coarse" ;
double temp_fine(...) ;   temp_fine:mesh = "Mesh2_fine" ;
```

---

### Q: `_FillValue` 可以用在連線性陣列中嗎？在哪些情況下？

**A:** 可以，主要用於**可變長度多邊形**（網格中混合三角形和四邊形時）：

```cdl
// 混合三角形和四邊形：最多 4 個節點
integer Mesh2_face_nodes(nMesh2_face, nMaxNodesPerFace) ;
  Mesh2_face_nodes:_FillValue = -9999 ;

data:
  Mesh2_face_nodes =
    0, 1, 3, -9999,    // 三角形（第 4 欄用 _FillValue）
    1, 2, 5, 4 ;       // 四邊形（4 個節點）
```

注意：`_FillValue` 必須是**不可能出現的有效索引值**。對 0-based 索引，`_FillValue = -1` 或 `-9999` 是安全的選擇（不能用 `0`！）

---

## 🔧 實作問題

### Q: Python 讀取 UGRID 連線性時，為什麼索引看起來都「偏大 1」？

**A:** 這是最常見的錯誤——忘記處理 `start_index`。

```python
# ❌ 錯誤：忽略 start_index
face_nodes = ds.variables['Mesh2_face_nodes'][:]  # 可能是 1-based！

# ✅ 正確：讀取並應用 start_index
face_nodes_var = ds.variables['Mesh2_face_nodes']
face_nodes = face_nodes_var[:].data
start_idx = int(getattr(face_nodes_var, 'start_index', 0))
face_nodes -= start_idx   # 正規化為 0-based
```

---

### Q: 如何在 Python 中快速驗證一個 UGRID 檔案是否合規？

**A:** 使用 `compliance-checker`：

```bash
pip install compliance-checker cc-plugin-ugrid
compliance-checker -t cf:1.12 my_file.nc
```

或用 Python 腳本做基本檢查：

```python
import netCDF4 as nc

def quick_check(filename: str) -> None:
    ds = nc.Dataset(filename)
    
    # 找網格拓撲
    meshes = [v for v in ds.variables.values()
              if getattr(v, 'cf_role', '') == 'mesh_topology']
    
    print(f"找到 {len(meshes)} 個網格拓撲變數")
    for m in meshes:
        print(f"  {m.name}: topology_dimension={m.topology_dimension}")
    
    if not meshes:
        print("❌ 未找到網格拓撲！")
    
    ds.close()

quick_check('my_file.nc')
```

---

### Q: `face_face_connectivity` 是必需的嗎？對效能有什麼影響？

**A:** 不是必需的（可選屬性），但對於需要鄰接面查詢的應用（如有限體積法的通量計算）有顯著效能優勢：

- **不提供時**：工具需要在讀取時自行計算面-面連線性（O(n log n) 時間）
- **提供時**：直接讀取，O(1) 查詢時間

建議在生成網格時同步計算並存入檔案，特別是大型網格（>100 萬個面）。

---

### Q: 如何表達 3D 資料——使用 2D mesh + 垂直維度，還是真正的 3D mesh？

**A:** 兩種方法都支援，選擇依賴應用場景：

| 方法 | topology_dimension | 適用場景 |
| ------ | -------------------- | --------- |
| 2D + 垂直維度 | 2 | 水平 σ/z 層分析、大多數海洋模型 |
| 真正 3D mesh | 3 | 體積有限元素、地質模型、不規則 3D 剖分 |

**建議**：多數海洋/大氣模型選擇**方法一（2D + 垂直維度）**，因為：

- 水平和垂直方向通常分開求解
- 大幅減少連線性陣列的複雜度
- 與現有 σ/z 座標框架相容

---

### Q: 位置索引集（location_index_set）適合在什麼情況使用？

**A:** 當資料只定義在網格的**一個子集**上時：

- 觀測站資料（稀疏分布在少數格點）
- 邊界條件（只在邊界邊/面上定義）
- 子域分析（只關注某個區域的面）

如果資料密度 > 80%（大多數元素都有值），直接用完整陣列+填充值更簡單。
如果資料密度 < 20%（大多數元素是缺失值），使用 `location_index_set` 更高效。

---

## 🛠️ 工具與環境問題

### Q: QGIS 能讀取 UGRID 資料嗎？

**A:** 是的，QGIS 3.x 支援讀取 UGRID NetCDF 資料：

```text
Layer → Add Layer → Add Mesh Layer → 選擇 .nc 檔案
```

如果無法讀取，確認：

1. QGIS 版本 ≥ 3.12
2. NetCDF 是用 NETCDF4 格式寫入（不是 NETCDF3）
3. 必要的 UGRID 屬性（`cf_role`, `mesh`, `location`）都已設置

---

### Q: cfchecker 報告「未知屬性 mesh」，這是問題嗎？

**A:** 如果使用 CF 1.10 或更舊版本的 cfchecker，它不識別 UGRID 屬性是正常的。
請確認 cfchecker 版本 ≥ 1.11，或在全域屬性中指定 `Conventions = "CF-1.11"` 或更高版本。

```bash
cfchecker --version 1.12 my_file.nc   # 明確指定版本
```

---

### Q: 在 DLAMP 專案中，預測結果輸出的 NetCDF 是否符合 UGRID？

**A:** 請查看 `predict.py` 和 `src/dlamp/analysis/` 中的輸出代碼。目前 DLAMP 的輸出格式以 CF 規範為基礎，如需完整的 UGRID 符合性，可在後處理步驟中添加必要的拓撲變數。

DLAMP 的輸入數據（ERA5/RWRF）使用規則網格，輸出結果目前不需要非結構化網格格式。如需要 UGRID 輸出，需要在網格轉換步驟中加入。

---

## 📊 資料問題

### Q: 如何從規則網格（如 ERA5）轉換為非結構化網格？

**A:** 需要以下步驟：

1. **建立目標非結構化網格**（使用 Gmsh 或 Triangle）
2. **插值**：從規則網格插值到非結構化節點/面中心

```python
from scipy.interpolate import RegularGridInterpolator
import numpy as np

# ERA5 規則網格的溫度
# regular_lon, regular_lat: 1D 陣列
# regular_temp: shape (nLat, nLon)

interp = RegularGridInterpolator(
    (regular_lat, regular_lon), regular_temp,
    method='linear', bounds_error=False
)

# 在非結構化網格的節點位置插值
ugrid_node_points = np.column_stack([ugrid_node_lat, ugrid_node_lon])
ugrid_node_temp = interp(ugrid_node_points)
```

---

### Q: 如何合併多個 UGRID 時步檔案？

**A:** 使用 NCO 的 `ncrcat`（沿時間軸連接）：

```bash
ncrcat step_*.nc merged.nc
```

或用 Python：

```python
import netCDF4 as nc
import numpy as np

# 假設每個檔案有相同的網格，只是時間步驟不同
output = nc.Dataset('merged.nc', 'w', format='NETCDF4')

# ... 複製維度和靜態變數 ...

for i, filename in enumerate(sorted(glob.glob('step_*.nc'))):
    ds = nc.Dataset(filename)
    temp = ds.variables['temperature'][:]
    output.variables['temperature'][i:i+len(temp)] = temp
    ds.close()

output.close()
```

---

## 🔗 相關文件

- [符合性要求](../implementation/conformance.md) — 規範問題的詳細解答
- [最佳實踐](../implementation/best-practices.md) — 常見問題的最佳解決方案
- [工具與函式庫](tools-libraries.md) — 工具使用詳細指南
- [索引技術細節](../technical-details/indexing.md) — 索引偏移問題的根本解答

## 📞 尋求幫助

- **UGRID 規範問題**：[GitHub Issues](https://github.com/ugrid-conventions/ugrid-conventions/issues)
- **CF 規範問題**：[CF Conventions GitHub Discussions](https://github.com/cf-convention/cf-conventions/discussions)
- **NetCDF 工具問題**：[Unidata Community Forum](https://discourse.unidata.ucar.edu/)

---

*最後更新*：2024 年 6 月 | *相關文件*: [工具與函式庫](tools-libraries.md) | [參考文獻](references.md)
