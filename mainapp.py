'''
MIT License
Copyright (c) 2019 Ivan D'Ortenzio
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Created on 24/03/2019

@author: Ivan D'Ortenzio
'''

import re
import geojson
import requests

app_id = "YOUR_APP_ID"
app_code = "YOUR_APP_CODE"

outresult = 'out_isoline.geojson'

# What area I can reach in 5,10 and 20 minutes from given position?
lon,lat = 13.37749,52.51578
url = 'https://isoline.route.cit.api.here.com/routing/7.2/calculateisoline.json'
parameters = dict()
parameters['app_id'] = app_id
parameters['app_code'] = app_code
parameters['mode'] = "shortest;car;traffic:disabled"
parameters['rangetype'] = "time"
# range in seconds
parameters['range'] = '300,600,1200'
parameters['start'] = 'geo!{1},{0}'.format(lon, lat)

isoline_json = requests.get(url,params = parameters).json()

isoline_data = isoline_json["response"]["isoline"][::-1]

# Define the crs
crs = {
    "type": "name",
    "properties": {
        "name": "EPSG:4326"
    }
}

feature_collection = []
for i,isoline in enumerate(isoline_data):
    coordinates = []
    for i,coord in enumerate(isoline["component"][0]["shape"]):
        lon_i,lat_i = [float(j) for j in re.findall("\\d+\\.\\d+",coord)][::-1]
        coordinates.append([lon_i,lat_i])                    
    feature = geojson.Feature(geometry = geojson.Polygon(geojson.LineString(coordinates)),
                              crs=crs,properties={"travel_time":int(isoline["range"])})
    feature_collection.append(feature)

feature_collection = geojson.FeatureCollection(feature_collection,crs=crs)

# Save the output to a geosjon file
with open(outresult, 'w') as outfile:
    geojson.dump(feature_collection, outfile)