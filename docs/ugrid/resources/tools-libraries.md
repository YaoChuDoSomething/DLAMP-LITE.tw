# UGRID 工具與函式庫 (Tools and Libraries)

## 📖 概述

本文件提供用於讀取、寫入、驗證和視覺化 UGRID NetCDF 資料的主要工具和函式庫的安裝與使用指南。

## 1. Python 生態系統

### 1.1 netCDF4-python

Unidata 官方的 NetCDF Python 介面，UGRID 操作的首選工具：

```bash
# 安裝
pip install netCDF4
# 或
conda install -c conda-forge netcdf4
```

```python
"""netCDF4 基本使用示例。"""

import netCDF4 as nc

# 讀取
ds = nc.Dataset('mesh.nc', 'r')
face_nodes = ds.variables['Mesh2_face_nodes'][:]
start_idx = ds.variables['Mesh2_face_nodes'].start_index
ds.close()

# 寫入
ds = nc.Dataset('output.nc', 'w', format='NETCDF4')
ds.Conventions = "CF-1.12"
ds.createDimension('nMesh2_face', 1000)
ds.createDimension('Three', 3)

var = ds.createVariable(
    'Mesh2_face_nodes', 'i4', ('nMesh2_face', 'Three'),
    zlib=True, complevel=4
)
var.cf_role = "face_node_connectivity"
var.start_index = 0
ds.close()
```

**官方文件**：[unidata.github.io/netcdf4-python](https://unidata.github.io/netcdf4-python/)

### 1.2 xarray

標注陣列函式庫，提供更高層次的介面：

```bash
pip install xarray
conda install -c conda-forge xarray
```

```python
"""xarray 讀取 UGRID 的示例。"""

import xarray as xr

# 讀取（注意：xarray 預設不完全支援 UGRID 語義）
ds = xr.open_dataset('mesh.nc', mask_and_scale=True)

# 讀取特定變數
temp = ds['temperature']    # DataArray
print(temp.dims)            # ('time', 'nSigma', 'nMesh2_face')
print(temp.attrs['mesh'])   # "Mesh2"
print(temp.attrs['location'])  # "face"

# 選取時步
temp_t0 = temp.isel(time=0)

ds.close()
```

**官方文件**：[xarray.pydata.org](https://xarray.pydata.org/)

### 1.3 xugrid（UGRID 專用）

專為 UGRID 設計的 xarray 延伸函式庫：

```bash
pip install xugrid
conda install -c conda-forge xugrid
```

```python
"""xugrid 使用示例（UGRID 感知的 xarray）。"""

import xugrid as xu

# 讀取（自動解析 UGRID 結構）
uds = xu.open_dataset('mesh.nc')

# 取得 UGRID 網格物件
grid = uds.ugrid.grid
print(f"節點數: {grid.n_node}")
print(f"面數: {grid.n_face}")

# 像 xarray 一樣操作，但有 UGRID 感知
temp = uds['temperature']
print(temp.ugrid.location)  # "face"

# 插值：從面到節點
temp_at_nodes = temp.ugrid.interpolate_to(xu.InterpolationMethod.BARYCENTRIC)
```

**GitHub**：[github.com/Deltares/xugrid](https://github.com/Deltares/xugrid)

### 1.4 pyproj（座標轉換）

```bash
pip install pyproj
conda install -c conda-forge pyproj
```

```python
"""pyproj 座標轉換示例。"""

from pyproj import Transformer
import numpy as np

# TWD97 TM2 zone 121 → WGS84
transformer = Transformer.from_crs(3826, 4326, always_xy=True)

x = np.array([306000.0, 248000.0])   # 東向座標
y = np.array([2769000.0, 2758000.0]) # 北向座標

lon, lat = transformer.transform(x, y)
print(f"經度: {lon}")   # [121.xxx, ...]
print(f"緯度: {lat}")   # [25.xxx, ...]
```

**官方文件**：[pyproj4.github.io/pyproj](https://pyproj4.github.io/pyproj/)

## 2. 符合性驗證工具

### 2.1 cfchecker

```bash
pip install cfchecker
```

```bash
# 驗證 CF 規範符合性（包含 UGRID）
cfchecker --version 1.12 my_ugrid_file.nc

# 輸出詳細資訊
cfchecker -v 1.12 my_ugrid_file.nc

# 輸出 JSON 格式（方便程式解析）
cfchecker --output json -v 1.12 my_ugrid_file.nc
```

**GitHub**：[github.com/cedadev/cf-checker](https://github.com/cedadev/cf-checker)

### 2.2 IOOS Compliance Checker

```bash
pip install compliance-checker

# 安裝 UGRID 插件
pip install cc-plugin-ugrid
```

```bash
# 驗證 CF 和 UGRID
compliance-checker -t cf:1.12 -t ugrid my_ugrid_file.nc

# 輸出 HTML 報告
compliance-checker -f html -t cf:1.12 my_ugrid_file.nc > report.html

# 列出可用的測試
compliance-checker -l
```

**GitHub**：[github.com/ioos/compliance-checker](https://github.com/ioos/compliance-checker)

### 2.3 線上驗證器

- **CF Compliance Checker**：[compliance.ioos.us](https://compliance.ioos.us/index.html)
  - 支援 URL 或上傳檔案
  - 支援 CF 1.6–1.12 和 ACDD

## 3. 命令列工具

### 3.1 ncdump（查看結構）

```bash
# 查看完整結構（header + data）
ncdump -h my_file.nc | head -100   # 只看 header，取前 100 行

# 查看指定變數的資料
ncdump -v Mesh2_face_nodes my_file.nc

# 以 CDL 格式輸出完整內容（可用於驗證）
ncdump -c my_file.nc > my_file.cdl
```

### 3.2 nco（NetCDF Operators）

```bash
# 安裝
conda install -c conda-forge nco

# 列出所有變數
ncks -m my_file.nc

# 提取特定變數
ncks -v temperature,Mesh2_face_nodes my_file.nc output.nc

# 選取時步範圍
ncks -d time,0,10 my_file.nc subset.nc

# 修改屬性
ncatted -a long_name,temperature,o,c,"Sea water temperature" my_file.nc

# 合併多個檔案（時間軸）
ncrcat file1.nc file2.nc merged.nc

# 計算時間平均
ncra my_file.nc time_mean.nc
```

**官方文件**：[nco.sourceforge.net](http://nco.sourceforge.net/)

### 3.3 cdo（Climate Data Operators）

```bash
# 安裝
conda install -c conda-forge cdo

# 查看檔案資訊
cdo info my_file.nc | head -50

# 時間平均
cdo timmean my_file.nc time_mean.nc

# 選取時步
cdo seltimestep,1,10 my_file.nc subset.nc
```

**官方文件**：[code.mpimet.mpg.de/cdo](https://code.mpimet.mpg.de/projects/cdo)

## 4. 視覺化工具

### 4.1 QGIS（GUI）

QGIS 從 3.x 版本起支援讀取 UGRID NetCDF 檔案：

```text
安裝：下載 QGIS 3.x 安裝包
使用：
  1. Layer → Add Layer → Add Mesh Layer
  2. 選擇 NetCDF 檔案
  3. 選擇網格變數（如 Mesh2）
  4. 套用顏色映射
```

**官方文件**：[qgis.org](https://qgis.org/)

### 4.2 ParaView（GUI）

支援大規模 UGRID 資料的科學視覺化：

```text
安裝：下載 ParaView 5.x
使用：
  1. File → Open → 選擇 NetCDF 檔案
  2. 在 Properties 選擇 Variables
  3. Apply → 選擇 Surface 渲染
  4. Edit → Color → 選擇變數
```

**官方文件**：[paraview.org](https://www.paraview.org/)

### 4.3 Python 視覺化（matplotlib + cartopy）

```python
"""使用 matplotlib 和 cartopy 視覺化 UGRID 資料。"""

import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def plot_ugrid_map(
    filename: str,
    var_name: str = 'temperature',
    time_idx: int = 0
) -> None:
    """在地圖上繪製 UGRID 資料。
    
    Args:
        filename: UGRID NetCDF 檔案路徑。
        var_name: 要繪製的變數名稱。
        time_idx: 時步索引。
    """
    ds = nc.Dataset(filename)
    
    node_lon = ds.variables['Mesh2_node_lon'][:]
    node_lat = ds.variables['Mesh2_node_lat'][:]
    face_nodes = ds.variables['Mesh2_face_nodes'][:]
    start_idx = int(getattr(ds.variables['Mesh2_face_nodes'], 'start_index', 0))
    face_nodes -= start_idx   # 轉換為 0-based
    
    var = ds.variables[var_name]
    data = var[time_idx]
    if data.ndim == 2:
        data = data[-1]  # 取最後一層（表面）
    
    units = getattr(var, 'units', '')
    ds.close()
    
    # 建立三角化物件
    tri = mtri.Triangulation(node_lon, node_lat, face_nodes)
    
    # 建立地圖
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111,
                         projection=ccrs.PlateCarree(central_longitude=121.0))
    
    # 繪製資料
    contourf = ax.tricontourf(tri, data,
                               levels=20, cmap='RdYlBu_r',
                               transform=ccrs.PlateCarree())
    plt.colorbar(contourf, ax=ax, shrink=0.8,
                 label=f'{var_name} ({units})')
    
    # 地圖裝飾
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.7)
    
    plt.title(f'{var_name} Distribution (t={time_idx})')
    plt.tight_layout()
    plt.savefig(f'{var_name}_map.png', dpi=150, bbox_inches='tight')
    plt.show()
```

## 5. 網格工具

### 5.1 建立三角形網格（Triangle + scipy）

```python
"""使用 scipy 的 Delaunay 三角化建立簡單三角形網格。"""

import numpy as np
from scipy.spatial import Delaunay


def create_triangular_mesh(
    lon_min: float, lon_max: float,
    lat_min: float, lat_max: float,
    n_points: int = 200
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """建立均勻三角形網格（僅用於測試）。
    
    Args:
        lon_min, lon_max: 經度範圍。
        lat_min, lat_max: 緯度範圍。
        n_points: 隨機點數量。
        
    Returns:
        (node_lon, node_lat, face_nodes) 的 tuple。
    """
    # 隨機生成節點（實際應用中應使用專業網格生成工具）
    np.random.seed(42)
    node_lon = np.random.uniform(lon_min, lon_max, n_points)
    node_lat = np.random.uniform(lat_min, lat_max, n_points)
    
    # 加入四角節點確保邊界
    corners_lon = [lon_min, lon_max, lon_min, lon_max]
    corners_lat = [lat_min, lat_min, lat_max, lat_max]
    node_lon = np.concatenate([node_lon, corners_lon])
    node_lat = np.concatenate([node_lat, corners_lat])
    
    # Delaunay 三角化
    points = np.column_stack([node_lon, node_lat])
    tri = Delaunay(points)
    face_nodes = tri.simplices   # shape: (nFace, 3)，0-based
    
    return node_lon, node_lat, face_nodes
```

## 6. DLAMP 專案工具

### 6.1 從 DLAMP 輸出轉換為 UGRID

```bash
# DLAMP 的 ONNX 推理輸出 → UGRID NetCDF
python predict.py          # 預設使用 ONNX 引擎

# 查看 predict.py 輸出
ls outputs/$(date +%Y-%m-%d)/*/  # 查看最新輸出目錄
```

### 6.2 環境設置（DLAMP 工作環境）

```bash
# 進入 DLAMP repo 根目錄
cd /wk2/yaochu/main/dlamp

# 使用 DLAMP 的 venv
.venv/bin/python -c "import dlamp; print('OK')"

# 安裝額外工具
.venv/bin/pip install netCDF4 xarray pyproj compliance-checker
```

## 🔗 相關文件

- [參考文獻](references.md) — 學術論文和官方規範連結
- [常見問題](faqs.md) — 工具使用常見問題
- [符合性要求](../implementation/conformance.md) — 使用工具驗證符合性

---

*下一步*: [常見問題](faqs.md) | [參考文獻](references.md)
