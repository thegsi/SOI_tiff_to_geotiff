# inside python 3.7.5 venv pip install pyshp==1.2
# python3 SOI_grid.py
import shapefile
import csv

shp = shapefile.Reader('./grid_shp/Survey_of_India_output')

shapeRecs = shp.shapeRecords()

records = [['sheet_ref', 'west', 'south', 'east', 'north', 'number', 'letter', 'subnumber']]

for sR in shapeRecs:
    record = vars(sR)['record']
    # 'record': [44.0, 28.0, 44.25, 28.25, '003', 'D', '04']}
    record.insert(0, record[4] + record[5] + record[6])
    records.append(record)

with open('./SOI_grid.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerows(records)
