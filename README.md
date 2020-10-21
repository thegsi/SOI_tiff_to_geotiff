# SOI_tiff_to_geotiff

Geolocate Survey of India maps.

Install dependencies
PIL `pip install pillow`. 
GDAL must match system gdal. 
gdainfo --version. 
`pip install gdal==2.4`. 
Pandas `pip install pandas`  

Add tiff files to SOI_tiffs. 
Name the files with map sheet number eg 044K03. 
See sheet_ref column in SOI_grid.csv. 

`python3 SOI_tiff_to_geotiff.py`. 

Click on four corners of map area in NW, NE, SE, SW order.  

SOI_create_gridcsv creates SOI_grid.csv from SOI fishnet shp file.  
