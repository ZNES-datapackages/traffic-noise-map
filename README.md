# Traffic-Noise-Map

Based on an osm data file a datapackage can be build containing buffered geodata of streets in 
the GeoJSON format. For each value of the highway tag a different buffer radius can be applied. 

## Warning

* This repository only provides a way of building a datapackage without shipping data. The license does obviously not apply to any data.

* The buffer radius is applied in meter on the PostGIS Geography type. That is why geodata should not fall within different UTM zones or cross the dateline. For more information see `http://www.postgis.net/docs/ST_Buffer.html'.

## Requirements

To build the datapackage a PostgreSQL database server has to be installed.
The following extensions should be loaded into the database: postgis, hstore.

To check loaded extensions:

    psql -c '\dx' databasename

To install them:

    psql -c 'CREATE extension postgis;' databasename
    psql -c 'CREATE extension hstore;' databasename

Furthermore you have to install required python packages. It is advised to use
a virtual environment.

    pip install -r requirements

The build script calls osm2pgsql for transferring data to the database. On ubuntu
you can call the apt-get command to install osm2pgsql.

    sudo apt-get install osm2pgsql

## Preperation

Update the database connection options and specify the url of an
osm data file in pbf format in `config.yml`. OSM data extracts can be found on https://download.geofabrik.de/. To apply different buffers use buffer.yml .

## Build

        python scripts/build.py
