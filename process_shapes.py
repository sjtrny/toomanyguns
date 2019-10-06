import geopandas as gpd
import json
import pandas as pd
import io

# Load firearm records
firearms = pd.read_csv("data_generated/firearms_2019.csv", index_col=0)
firearms = firearms.set_index('postcode')

# Load postal areas shape file
geodf = gpd.read_file("data_static/POA_2016_AUST.shp")
geodf['POA_CODE16'] = geodf['POA_CODE16'].astype(int)
geodf = geodf.set_index('POA_CODE16', drop=False)

# Restrict shapes to NSW for performance
nsw = geodf[(geodf['POA_CODE16'] >=2000) & (geodf['POA_CODE16'] < 3000)]

# Insert firearm data in the geo records
nsw = nsw.merge(firearms, left_index=True, right_index=True)

geo_copy = nsw.copy()

min_tol = 0.00035
# min_tol = 0.0007
max_tol = 0.025

tol_range = max_tol - min_tol

min_area = nsw.geometry.area.min()
area_range = nsw.geometry.area.max() - min_area

geo_list = []

ans = geo_copy.iloc[0, :].geometry
# ans2 = gpd.GeoSeries(geo_list, index=[2000])

for index, row in geo_copy.iterrows():
    area_px = (row.geometry.area - min_area) / area_range

    tol = area_px * tol_range + min_tol

    geo_list.append(row.geometry.simplify(tolerance=tol))

geo_copy.geometry = gpd.GeoSeries(geo_list, index=geo_copy.index)

# geo_copy['geometry'] = geo_copy['geometry'].simplify(tolerance=v)

# Convert to JSON, load as dictionary, insert id then save to disk
proxyIO = io.BytesIO()
geo_copy.to_file(proxyIO, driver='GeoJSON')

post_areas = json.loads(proxyIO.getvalue().decode('utf-8'))

for feat in post_areas['features']:
    feat['id'] = feat['properties']['POA_NAME16']

json.dump(post_areas, open(f"data_generated/nsw.json", "w"))