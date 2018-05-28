import os
import yaml
import json
import pandas as pd
import sqlalchemy

from sqlalchemy import create_engine, MetaData, func, cast
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry, shape, Geography
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.schema import CreateSchema
from urllib.request import urlretrieve
from geojson import FeatureCollection, Feature
from tools import osm2pgsql, add_primary_key, _walk

import logging

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)

conn = config['connection-options']

# download data
url = config['url']
filename = url.split('/')[-1]
filepath = config['directories']['cache'] + filename

if not os.path.exists(filepath):
    urlretrieve(url, filepath)

# setup database
engine = create_engine(
    "postgresql+psycopg2://{username}:{password}@{host}:{port}/{db}".\
    format(**conn))

session = sessionmaker(bind=engine)()

try:
    session.execute(CreateSchema(conn['schema']))
    session.commit()
except sqlalchemy.exc.ProgrammingError as e:
    pass

osm2pgsql(filepath, **conn, cache=config['cache'], latlon=True)
session.commit()

osmtables = ['planet_osm_line', 'planet_osm_polygon', 'planet_osm_point']

for tablename in osmtables:
    add_primary_key(session, tablename, conn['schema'])  # not done by osm2pgsql

# initiate orm
meta = MetaData(bind=engine)
meta.reflect(schema=conn['schema'], only=osmtables)
Base = automap_base(metadata=meta)
Base.prepare()

# apply buffering
# http://www.postgis.net/docs/ST_Buffer.html : For geography this may not behave as expected if object is sufficiently large that it falls between two UTM zones or crosses the dateline
with open("buffer.yml", 'r') as ymlfile:
    buffer_config = yaml.load(ymlfile)

features = []
for osmtab, osmkey, osmval, radius in _walk(buffer_config):
    ormclass = Base.classes[osmtab]

    fields = getattr(ormclass, 'id'), getattr(ormclass, 'osm_id'), \
        cast(func.ST_Buffer(cast(ormclass.way, Geography), radius), Geometry)

    results = session.query(*fields).filter(getattr(ormclass, osmkey) == osmval).all()

    for id_, osmid, geom in results:

        properties = {'id': id_, 'osm_id': osmid, 'key': osmkey,
                      'value': osmval, 'radius_of_buffer': radius}

        features.append(Feature(
            geometry=shape.to_shape(geom), properties=properties))

# dump to file
filepath = config['directories']['data'] + 'noisemap.geojson'
with open(filepath, 'w') as outfile:
        json.dump(FeatureCollection(features), outfile, indent=2)
