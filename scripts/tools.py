import math
import subprocess
import pyproj

from functools import partial
from shapely.ops import transform
from urllib.parse import urlparse
from sqlalchemy import create_engine, MetaData, func, cast
from sqlalchemy.orm import sessionmaker

def update_search_path(session, rolename, search_path):
    sql = "ALTER ROLE %s SET search_path TO %s;" % (rolename, search_path)
    session.execute(sql)
    session.commit()
    return

def add_primary_key(session, tablename, schema):
    sql = "ALTER TABLE %s.%s ADD COLUMN id SERIAL PRIMARY KEY;" % (schema, tablename)
    session.execute(sql)
    session.commit()
    return

def _walk(config):
    """ Walks on buffer configuration file """
    for osmtab, _ in config.items():
        for e in _:
            for osmkey, __ in e.items():
                for osmval, radius in __.items():
                    yield (osmtab, osmkey, osmval, radius)


def osm2pgsql(filepath, username='postgres', password='', db='postgres',
              host='localhost', port='5432', cache='800', schema='public',
              hstore=True, latlon=True,
              style='/usr/share/osm2pgsql/default.style'):
    """ Wrapper for osm2pgsql call

    Notes
    -----
    https://gis.stackexchange.com/questions/242813/loading-openstreetmap-data-to-a-custom-postgresql-schema-via-osm2pgsql
    """

    session = sessionmaker(
        bind=create_engine(
            'postgresql+psycopg2://' + username + ':' + password + '@' + host +
            ':' + port + '/' + db))()

    arguments = ['-W', '-P', port, '-U', username, '-d', db, '-H', host, '--cache', cache]

    if hstore:
        arguments.append('--hstore')
    if latlon:
        arguments.append('-l')

    if schema != 'public':
        search_path_stored = session.execute("SHOW search_path;").first()[0]
        update_search_path(session, username, schema + ', public')
        subprocess.call(['osm2pgsql', *arguments, filepath])
        update_search_path(session, username, search_path_stored)
    else:
        subprocess.call(['osm2pgsql', *arguments, filepath])

    return
