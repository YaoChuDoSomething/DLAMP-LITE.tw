# UGRID 參考文獻 (References)

## 📖 官方規範文件

### UGRID 規範

| 資源 | 連結 | 描述 |
| --- | --- | --- |
| UGRID 官方文件 | [ugrid-conventions.github.io](https://ugrid-conventions.github.io/ugrid-conventions/) | 完整規範，包含所有屬性和示例 |
| UGRID GitHub | [github.com/ugrid-conventions](https://github.com/ugrid-conventions/ugrid-conventions) | 規範的原始碼和議題追蹤 |
| UGRID 規範 PDF | [ugrid-1.0.pdf](https://ugrid-conventions.github.io/ugrid-conventions/ugrid_conventions.pdf) | 可下載的 PDF 版本 |

### CF 規範

| 資源 | 連結 | 描述 |
| --- | --- | --- |
| CF Conventions v1.12 | [cfconventions.org](https://cfconventions.org/cf-conventions/cf-conventions.html) | 完整 CF 規範（UGRID 已整合自 v1.11） |
| CF Standard Names | [cfconventions.org/standard-names](https://cfconventions.org/standard-names.html) | 標準名稱查詢工具 |
| CF 符合性檢查器 | [compliance.ioos.us](https://compliance.ioos.us/index.html) | 線上 CF/UGRID 符合性驗證工具 |

### NetCDF

| 資源 | 連結 | 描述 |
| --- | --- | --- |
| NetCDF 官方文件 | [unidata.ucar.edu/netcdf](https://www.unidata.ucar.edu/software/netcdf/) | Unidata NetCDF 主頁 |
| NetCDF 最佳實踐 | [esipfed.org/netcdf](https://wiki.esipfed.org/Attribute_Convention_for_Data_Discovery) | ACDD 屬性約定 |
| NetCDF-4 特性 | [docs.unidata.ucar.edu](https://docs.unidata.ucar.edu/netcdf-c/current/guide.html) | NetCDF-4 功能指南 |

## 📄 學術論文

### UGRID 規範原始論文

> Hascoet, F., Roshan, G., Casulli, V., et al. (2011).
> **Conventions for CF-Metadata and Unstructured Grids**.
> Proceedings of the ESIP Summer Meeting 2011.

---

> Blanton, B., et al. (2013).
> **UGRID - Conventions for Unstructured Grid Metadata**.
> *NOAA Technical Report*.
> [doi:10.25923/epy9-jx86](https://repository.library.noaa.gov/view/noaa/6726)

### 相關海洋模型論文

> Chen, C., Liu, H., & Beardsley, R. C. (2003).
> **An Unstructured Grid, Finite-Volume, Three-Dimensional, Primitive Equations Ocean Model: Application to Coastal Ocean and Estuaries**.
> *Journal of Atmospheric and Oceanic Technology*, 20(1), 159-186.
> [doi:10.1175/1520-0426(2003)020<0159:AUGFVT>2.0.CO;2](https://doi.org/10.1175/1520-0426(2003)020<0159:AUGFVT>2.0.CO;2)
> *(FVCOM 模型，廣泛使用 UGRID 格式)*

---

> Zhang, Y. J., Stanev, E. V., & Grashorn, S. (2016).
> **Unstructured-grid model for the North Sea and Baltic Sea: validation against observations**.
> *Ocean Modelling*, 97, 91-108.
> [doi:10.1016/j.ocemod.2015.11.009](https://doi.org/10.1016/j.ocemod.2015.11.009)
> *(SCHISM 模型)*

---

> Danilov, S. (2013).
> **Ocean modeling on unstructured meshes**.
> *Ocean Modelling*, 69, 195-210.
> [doi:10.1016/j.ocemod.2013.05.005](https://doi.org/10.1016/j.ocemod.2013.05.005)

## 🔧 主要工具與函式庫

### NetCDF 讀寫

| 工具 | 語言 | 連結 | 說明 |
| ------ | ------ | ------ | ------ |
| netCDF4-python | Python | [unidata.github.io/netcdf4-python](https://unidata.github.io/netcdf4-python/) | Unidata 官方 Python 介面 |
| xarray | Python | [xarray.pydata.org](https://xarray.pydata.org/) | 標注陣列，支援 NetCDF |
| scipy.io.netcdf | Python | [scipy.org](https://docs.scipy.org/doc/scipy/reference/generated/scipy.io.netcdf_file.html) | scipy 內建（較簡單） |
| netcdf-java | Java | [unidata.ucar.edu](https://www.unidata.ucar.edu/software/netcdf-java/) | CDM/THREDDS |
| nco | CLI | [nco.sourceforge.net](http://nco.sourceforge.net/) | NetCDF 命令列工具集 |
| cdo | CLI | [code.mpimet.mpg.de/cdo](https://code.mpimet.mpg.de/projects/cdo) | 氣候資料算子（CDO） |

### 符合性驗證

| 工具 | 語言 | 連結 | 說明 |
| --- | --- | --- | --- |
| cfchecker | Python | [github.com/cedadev/cf-checker](https://github.com/cedadev/cf-checker) | CF 規範驗證工具 |
| IOOS Compliance Checker | Python | [github.com/ioos/compliance-checker](https://github.com/ioos/compliance-checker) | 多規範驗證（CF, UGRID, ACDD） |

### 視覺化

| 工具 | 語言 | 連結 | 說明 |
| ------ | ------ | ------ | ------ |
| matplotlib.tri | Python | [matplotlib.org](https://matplotlib.org/stable/api/tri_api.html) | 三角形網格繪圖 |
| cartopy | Python | [scitools.org.uk/cartopy](https://scitools.org.uk/cartopy/) | 地圖投影視覺化 |
| QGIS | GUI | [qgis.org](https://qgis.org/) | 支援 UGRID NetCDF 的 GIS |
| ParaView | GUI | [paraview.org](https://www.paraview.org/) | 科學資料視覺化（支援 UGRID） |
| VisIt | GUI | [visit-dav.github.io](https://visit-dav.github.io/visit-website/) | 大規模資料視覺化（支援 UGRID） |

### 網格生成

| 工具 | 語言 | 連結 | 說明 |
| ------ | ------ | ------ | ------ |
| Gmsh | C++/Python | [gmsh.info](https://gmsh.info/) | 開源網格生成工具 |
| Triangle | C | [cs.cmu.edu/~quake/triangle](https://www.cs.cmu.edu/~quake/triangle.html) | Delaunay 三角化 |
| Qhull | C | [qhull.org](http://www.qhull.org/) | 凸包和 Delaunay 三角化 |
| SMS/ADCIRC | GUI | [aquaveo.com](https://www.aquaveo.com/) | 海岸洪水模型網格工具（商業） |

## 📦 海洋/水動力模型（使用 UGRID）

| 模型 | 連結 | 說明 |
| ------ | ------ | ------ |
| FVCOM | [fvcom.smast.umassd.edu](http://fvcom.smast.umassd.edu/) | 有限體積近岸海洋模型 |
| SCHISM | [schism.wiki](https://schism.wiki/) | 半隱式跨尺度水動力海洋模型 |
| Delft3D-FM | [oss.deltares.nl](https://oss.deltares.nl/web/delft3dfm/) | 三角形彈性網格 |
| ADCIRC | [adcirc.org](https://adcirc.org/) | 潮汐與颶風海浪模型 |
| ROMS | [myroms.org](https://www.myroms.org/) | 區域海洋模型系統 |
| SELFE/ELCIRC | [selfe.science](http://selfe.science/) | 半隱式歐拉-拉格朗日有限元素 |

## 🗺️ 台灣相關資料來源

| 資料集 | 來源 | 說明 |
| -------- | ------ | ------ |
| TPESF 台灣近海高解析地形 | [ocean.cwa.gov.tw](https://ocean.cwa.gov.tw/) | 中央氣象署海洋資料 |
| ETOPO1 全球地形 | [ngdc.noaa.gov](https://www.ngdc.noaa.gov/mgg/global/) | NOAA 全球高解析地形 |
| GEBCO 海底地形 | [gebco.net](https://www.gebco.net/) | 全球海底地形資料集 |
| 台灣海洋資料庫 | [todb.re.ntou.edu.tw](https://todb.re.ntou.edu.tw/) | 國立台灣海洋大學 |
| TWD97 EPSG:3826 | [epsg.io/3826](https://epsg.io/3826) | 台灣大地基準投影 |

## 📚 教學資源

| 資源 | 連結 | 說明 |
| ------ | ------ | ------ |
| Unidata NetCDF Workshop | [unidata.ucar.edu](https://www.unidata.ucar.edu/software/netcdf/workshop/) | NetCDF 教學工作坊材料 |
| CF Conventions Tutorial | [cfconventions.org](https://cfconventions.org/faq.html) | CF 規範常見問題解答 |
| UGRID GitHub Issues | [github.com/ugrid-conventions/ugrid-conventions/issues](https://github.com/ugrid-conventions/ugrid-conventions/issues) | 規範討論和問題回報 |
| Unidata Community Forum | [discourse.unidata.ucar.edu](https://discourse.unidata.ucar.edu/) | NetCDF/CF 社群論壇 |

---

*相關文件*: [工具與函式庫](tools-libraries.md) | [常見問題](faqs.md) | [核心概念](../conventions/core-concepts.md)
