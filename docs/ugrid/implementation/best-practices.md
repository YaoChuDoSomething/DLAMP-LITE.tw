# UGRID 最佳實踐 (Best Practices)

## 📖 概述

本文件整理了在實際應用中遵循 UGRID 規範時的最佳實踐與常見錯誤。這些建議來自於科學計算社群的實際經驗，旨在確保 NetCDF 檔案的**互操作性、可讀性與長期維護性**。

## 1. 命名規範

### 1.1 網格拓撲變數

```cdl
// ✅ 建議：使用描述性名稱，帶有維度後綴
integer Mesh2D ;               // 2D 三角形/四邊形網格
integer Mesh1D_network ;       // 1D 河道網路
integer Mesh3D_sigma ;         // 3D σ 層網格

// ⚠️ 可接受但不夠清晰
integer Mesh ;                 // 過於通用
integer topology ;             // 可接受

// ❌ 不建議：不直觀的名稱
integer m1 ;
integer topo_var ;
```

### 1.2 連線性變數

遵循 `{MeshName}_{connectivity_type}` 的命名模式：

```cdl
// ✅ 標準命名
integer Mesh2_face_nodes(nMesh2_face, nMaxFaceNodes) ;
integer Mesh2_edge_nodes(nMesh2_edge, Two) ;
integer Mesh2_face_edges(nMesh2_face, nMaxFaceNodes) ;

// ✅ 有前綴的 1D 網格
integer Mesh1D_edge_nodes(nMesh1D_edge, Two) ;
```

### 1.3 座標變數

```cdl
// ✅ 地理座標（經緯度）
double Mesh2_node_lon(nMesh2_node) ;  // 使用 lon/lat
double Mesh2_node_lat(nMesh2_node) ;

// ✅ 投影座標（公尺）
double Mesh2_node_x(nMesh2_node) ;   // 使用 x/y
double Mesh2_node_y(nMesh2_node) ;

// ✅ 面/邊的幾何中心（可選）
double Mesh2_face_x(nMesh2_face) ;
double Mesh2_face_y(nMesh2_face) ;
```

### 1.4 維度命名

```cdl
// ✅ 建議：明確包含網格名稱和元素類型
nMesh2_node    // 2D 網格的節點數
nMesh2_edge    // 2D 網格的邊數
nMesh2_face    // 2D 網格的面數
Three          // 固定大小的輔助維度（三角形）
Four           // 固定大小的輔助維度（四邊形）
nMaxFaceNodes  // 可變面的最大節點數
```

## 2. 索引規範

### 2.1 一致使用 0-based 索引

**強烈建議**在整個檔案中統一使用 `start_index = 0`：

```cdl
// ✅ 統一 0-based（建議）
integer Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:start_index = 0 ;

integer Mesh2_edge_nodes(nMesh2_edge, Two) ;
  Mesh2_edge_nodes:start_index = 0 ;

// ⚠️ 混用 0-based 和 1-based（強烈不建議）
integer Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:start_index = 0 ;

integer Mesh2_edge_nodes(nMesh2_edge, Two) ;
  Mesh2_edge_nodes:start_index = 1 ;  // 不一致！容易出錯
```

### 2.2 始終顯式設置 start_index

```cdl
// ✅ 始終顯式設置，即使是預設值
integer Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
  Mesh2_face_nodes:start_index = 0 ;  // ← 明確，無歧義

// ❌ 不要依賴預設值
integer Mesh2_face_nodes(nMesh2_face, Three) ;
  Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
  // 無 start_index → 假設為 0，但不清晰
```

### 2.3 可變長度陣列的 _FillValue

對於非固定大小的連線性陣列，必須明確定義 `_FillValue`：

```cdl
// ✅ 正確：明確定義且值不與有效索引重疊
integer Mesh2_face_nodes(nMesh2_face, nMaxFaceNodes) ;
  Mesh2_face_nodes:cf_role = "face_node_connectivity" ;
  Mesh2_face_nodes:start_index = 0 ;
  Mesh2_face_nodes:_FillValue = -9999 ;  // 負數不與非負索引重疊

// ❌ 錯誤：_FillValue 可能與有效索引重疊
integer Mesh2_face_nodes(nMesh2_face, nMaxFaceNodes) ;
  Mesh2_face_nodes:_FillValue = 0 ;      // 0 是有效的 0-based 索引！
```

## 3. 後設資料最佳實踐

### 3.1 必要的後設資料

每個資料變數都應有充分的後設資料：

```cdl
// ✅ 完整後設資料
double temperature(time, nMesh2_face) ;
  temperature:standard_name = "sea_water_potential_temperature" ;
  temperature:long_name = "Potential Temperature at Sea Surface" ;
  temperature:units = "degree_Celsius" ;
  temperature:mesh = "Mesh2" ;
  temperature:location = "face" ;
  temperature:coordinates = "Mesh2_face_x Mesh2_face_y" ;
  temperature:_FillValue = -9999.0 ;
  temperature:valid_range = -5.0, 40.0 ;

// ❌ 不完整的後設資料
double temperature(time, nMesh2_face) ;
  temperature:mesh = "Mesh2" ;
  temperature:location = "face" ;
  // 缺少 standard_name, units, _FillValue → 難以使用
```

### 3.2 CF standard_name 的使用

優先使用 CF 標準名稱：

```cdl
// ✅ 使用 CF 標準名稱
temperature:standard_name = "sea_water_potential_temperature" ;

// ⚠️ 當沒有對應的標準名稱時
temperature:standard_name = "sea_water_temperature" ;  // 若有對應標準名
temperature:long_name = "My custom temperature" ;       // 否則用 long_name

// ❌ 自造標準名稱（CF 不認可）
temperature:standard_name = "my_custom_temperature" ;   // 無效
```

### 3.3 時間座標

```cdl
// ✅ 最佳實踐
double time(time) ;
  time:standard_name = "time" ;
  time:units = "seconds since 2024-01-01 00:00:00 +00:00" ;  // 帶時區
  time:calendar = "proleptic_gregorian" ;                     // 明確指定
  time:axis = "T" ;

// ⚠️ 可接受但不完整
double time(time) ;
  time:units = "days since 2024-01-01" ;  // 缺少時區和 calendar
```

### 3.4 座標參考系統

當使用投影座標（非地理座標）時，必須提供 CRS 資訊：

```cdl
// ✅ 提供 CRS 資訊
double Mesh2_node_x(nMesh2_node) ;
  Mesh2_node_x:standard_name = "projection_x_coordinate" ;
  Mesh2_node_x:units = "m" ;
  Mesh2_node_x:grid_mapping = "crs" ;

char crs ;
  crs:grid_mapping_name = "transverse_mercator" ;
  crs:semi_major_axis = 6378137.0 ;
  crs:inverse_flattening = 298.257223563 ;
  crs:latitude_of_projection_origin = 0.0 ;
  crs:longitude_of_central_meridian = 121.0 ;
  crs:scale_factor_at_central_meridian = 0.9999 ;
  crs:false_easting = 250000.0 ;
  crs:false_northing = 0.0 ;
  crs:projected_coordinate_system_name = "TWD97 / TM2 zone 121" ;
  crs:geographic_coordinate_system_name = "TWD97" ;

// ✅ 同時提供地理座標作為輔助
double Mesh2_node_lon(nMesh2_node) ;
  Mesh2_node_lon:standard_name = "longitude" ;
  Mesh2_node_lon:units = "degrees_east" ;

double Mesh2_node_lat(nMesh2_node) ;
  Mesh2_node_lat:standard_name = "latitude" ;
  Mesh2_node_lat:units = "degrees_north" ;
```

## 4. 效能最佳化

### 4.1 壓縮

對大型陣列使用 NetCDF-4 的內建壓縮：

```python
import netCDF4 as nc

ds = nc.Dataset('output.nc', 'w', format='NETCDF4')

# 建立壓縮後的連線性變數
face_nodes = ds.createVariable(
    'Mesh2_face_nodes', 'i4', ('nMesh2_face', 'Three'),
    zlib=True,          # 啟用壓縮
    complevel=4,        # 壓縮等級 1-9（建議 4）
    shuffle=True        # 預處理，提高壓縮率
)

# 建立壓縮後的資料變數
temperature = ds.createVariable(
    'temperature', 'f4', ('time', 'nMesh2_face'),
    zlib=True,
    complevel=4,
    shuffle=True,
    chunksizes=(10, 10000)  # 時間步驟小，空間大
)
```

### 4.2 分塊（Chunking）

根據存取模式選擇分塊大小：

```python
# 時間序列存取（逐時步讀取所有空間）
temperature = ds.createVariable(
    'temperature', 'f4', ('time', 'nMesh2_face'),
    chunksizes=(1, nFace)      # 每次讀一個時步的全部空間
)

# 空間局部存取（讀取少量時步，大量空間）
temperature = ds.createVariable(
    'temperature', 'f4', ('time', 'nMesh2_face'),
    chunksizes=(100, 1000)     # 100 個時步，1000 個面
)
```

### 4.3 避免冗餘的面座標

只在確實需要面中心座標時才定義：

```cdl
// 若資料從不需要面座標，不必定義
Mesh2:face_coordinates = "Mesh2_face_x Mesh2_face_y" ;  // ← 可選，視需求而定
```

## 5. 多網格場景

### 5.1 明確區分每個網格的元素

當一個檔案包含多個網格時，命名必須保持唯一且易於辨別：

```cdl
// ✅ 清晰的多網格
integer Mesh2_coarse ;          // 粗解析度 2D 網格
  Mesh2_coarse:node_coordinates = "Mesh2_coarse_node_x Mesh2_coarse_node_y" ;
  Mesh2_coarse:face_node_connectivity = "Mesh2_coarse_face_nodes" ;

integer Mesh2_fine ;            // 細解析度 2D 網格
  Mesh2_fine:node_coordinates = "Mesh2_fine_node_x Mesh2_fine_node_y" ;
  Mesh2_fine:face_node_connectivity = "Mesh2_fine_face_nodes" ;

// ✅ 各自的維度也需要區分
nMesh2_coarse_node = 1000 ;
nMesh2_coarse_face = 1800 ;
nMesh2_fine_node   = 10000 ;
nMesh2_fine_face   = 18000 ;
```

### 5.2 資料變數引用正確的網格

```cdl
// ✅ 粗網格資料
double temperature_coarse(time, nMesh2_coarse_face) ;
  temperature_coarse:mesh = "Mesh2_coarse" ;    // 指向粗網格
  temperature_coarse:location = "face" ;

// ✅ 細網格資料
double temperature_fine(time, nMesh2_fine_face) ;
  temperature_fine:mesh = "Mesh2_fine" ;        // 指向細網格
  temperature_fine:location = "face" ;
```

## 6. 全域屬性最佳實踐

```cdl
// ✅ 建議的全域屬性
:Conventions = "CF-1.12" ;
:title = "Taiwan Regional Ocean Model - 2024 Hindcast" ;
:institution = "National Taiwan University, Dept. of Atmospheric Sciences" ;
:source = "DLAMP v2.0 / UGRID 1.0" ;
:history = "2024-06-01 Created by model run troam_2024_hincast_v1.py" ;
:references = "Author et al. (2024) Journal of XX, doi:10.xxx/yyy" ;
:comment = "Hindcast simulation for validation purposes only" ;
:featureType = "unstructuredGrid" ;  // 建議添加，表示資料類型
```

## 7. 工具互操作性驗證

在發布資料前，建議用以下工具驗證：

```bash
# 1. CF 規範驗證
cfchecker --version 1.12 my_ugrid_file.nc

# 2. ncdump 快速查看結構（確認屬性無誤）
ncdump -h my_ugrid_file.nc | head -100

# 3. 使用 xarray 測試讀取
python -c "import xarray as xr; ds = xr.open_dataset('my_ugrid_file.nc'); print(ds)"

# 4. 使用 QGIS 或 ParaView 視覺化驗證（可選）
```

## 🔗 相關文件

- [符合性要求](conformance.md) — 最低要求清單
- [1D 網路示例](examples/1d-network-example.md) — 實際範例
- [2D 三角形示例](examples/2d-triangular-example.md) — 實際範例
- [技術細節 - 索引](../technical-details/indexing.md) — 索引的深入說明

## 📚 參考資源

- [CF Conventions Best Practices](https://cfconventions.org/cf-conventions/cf-conventions.html)
- [UGRID 官方文件](https://ugrid-conventions.github.io/ugrid-conventions/)
- [NetCDF Best Practices Guide](https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery)

---

*下一步*: [1D 網路示例](examples/1d-network-example.md) | [符合性要求](conformance.md)
