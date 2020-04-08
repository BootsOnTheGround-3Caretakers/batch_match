import requests
import zipfile
import io
import csv
import json

from elasticsearch import Elasticsearch

"""
country code      : iso country code, 2 characters
postal code       : varchar(20)
place name        : varchar(180)
admin name1       : 1. order subdivision (state) varchar(100)
admin code1       : 1. order subdivision (state) varchar(20)
admin name2       : 2. order subdivision (county/province) varchar(100)
admin code2       : 2. order subdivision (county/province) varchar(20)
admin name3       : 3. order subdivision (community) varchar(100)
admin code3       : 3. order subdivision (community) varchar(20)
latitude          : estimated latitude (wgs84)
longitude         : estimated longitude (wgs84)
accuracy          : accuracy of lat/lng from 1=estimated, 4=geonameid, 6=centroid of addresses or shape
"""

iso_2_to_3 = {}
with open('iso.json') as f:
    for line in f:
        j = json.loads(line)
        iso_2_to_3[j["802"]] = j["824"]

es = Elasticsearch()
geocode_file = io.BytesIO(requests.get('http://download.geonames.org/export/zip/allCountries.zip').content)
with zipfile.ZipFile(geocode_file) as geocode_zip:
    with geocode_zip.open('allCountries.txt') as all_countries_fh:
        for line in all_countries_fh:
            line = line.decode("utf-8").strip()
            fields = line.split('\t')
            try:
                record = {
                    "countryCode": iso_2_to_3[fields[0]],
                    "countryCode-2Alpha": fields[0],
                    "postalCode": fields[1],
                    "city": fields[2],
                    "state": fields[3],
                    "stateCode": fields[4],
                    "lat": fields[9],
                    "lon": fields[10]
                }
            except IndexError:
                continue
            es.index("geocode", body=record)