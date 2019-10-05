import geopandas as gpd
import json
import pandas as pd
import io
from hurry.filesize import size
import numpy as np

# Load firearm records
firearms = pd.read_csv("2019.csv", index_col=0)
firearms = firearms.set_index('postcode')

# Load postal areas shape file
geodf = gpd.read_file("shapes/POA_2016_AUST.shp")
geodf['POA_CODE16'] = geodf['POA_CODE16'].astype(int)
geodf = geodf.set_index('POA_CODE16', drop=False)

# Restrict shapes to NSW for performance
nsw = geodf[(geodf['POA_CODE16'] >=2000) & (geodf['POA_CODE16'] < 3000)]

# Insert firearm data in the geo records
nsw = nsw.merge(firearms, left_index=True, right_index=True)

tols = {
    "live": 0.00035,
    "debug": 0.01
}

for k,v in tols.items():

    geo_copy = nsw.copy()
    geo_copy['geometry'] = geo_copy['geometry'].simplify(tolerance=v)

    # Convert to JSON, load as dictionary, insert id then save to disk
    proxyIO = io.BytesIO()
    geo_copy.to_file(proxyIO, driver='GeoJSON')

    post_areas = json.loads(proxyIO.getvalue().decode('utf-8'))

    for feat in post_areas['features']:
        feat['id'] = feat['properties']['POA_NAME16']

    json.dump(post_areas, open(f"nsw_{k}.json", "w"))
