import datetime
import pandas as pd
import flask
from sqlalchemy import create_engine

def extract(file_name):
    df = pd.read_csv(f"./files/{file_name}.csv")
    return df

def transform_region(df, region_filter):
    #getting coordinates on indivitual lat and lon columns
    df['origin_coord_lat'] = df['origin_coord'].str.extract(r"(?<=POINT \()(.*)(?=\))")
    df['origin_coord_lat'] = df['origin_coord_lat'].str.split(' ')
    df['origin_coord_lat'] = pd.to_numeric(df['origin_coord_lat'].str[0])

    df['origin_coord_lon'] = df['origin_coord'].str.extract(r"(?<=POINT \()(.*)(?=\))")
    df['origin_coord_lon'] = df['origin_coord_lon'].str.split(' ')
    df['origin_coord_lon'] = pd.to_numeric(df['origin_coord_lon'].str[1])

    df['destination_coord_lat'] = df['destination_coord'].str.extract(r"(?<=POINT \()(.*)(?=\))")
    df['destination_coord_lat'] = df['destination_coord_lat'].str.split(' ')
    df['destination_coord_lat'] = pd.to_numeric(df['destination_coord_lat'].str[0])

    df['destination_coord_lon'] = df['destination_coord'].str.extract(r"(?<=POINT \()(.*)(?=\))")
    df['destination_coord_lon'] = df['destination_coord_lon'].str.split(' ')
    df['destination_coord_lon'] = pd.to_numeric(df['destination_coord_lon'].str[1])

    #converts to datetime
    df['datetime'] = pd.to_datetime(df['datetime'])

    #group by similar origin/destination/time
    df = df.groupby(df.columns.tolist(), as_index=False).size()

    #filter by region
    df = df[df['region'] == region_filter]

    #groupBy region
    df['datetime'] = pd.to_datetime(df['datetime']) - pd.to_timedelta(7, unit='d')
    df = df.groupby(['region', pd.Grouper(key='datetime', freq='W-MON')])['size']\
    .sum()\
    .reset_index()\
    .sort_values('datetime')

    df['size'] = df['size'] / 7

    df.rename(columns={'datetime':'week', 'size':'week_average'}, inplace=True)

    return df

def transform_coordinates(df, origin_dest, upper_value_lat, lower_value_lat, upper_value_lon, lower_value_lon):
    #getting coordinates on indivitual lat and lon columns
    df['origin_coord_lat'] = df['origin_coord'].str.extract(r"(?<=POINT \()(.*)(?=\))")
    df['origin_coord_lat'] = df['origin_coord_lat'].str.split(' ')
    df['origin_coord_lat'] = pd.to_numeric(df['origin_coord_lat'].str[0])

    df['origin_coord_lon'] = df['origin_coord'].str.extract(r"(?<=POINT \()(.*)(?=\))")
    df['origin_coord_lon'] = df['origin_coord_lon'].str.split(' ')
    df['origin_coord_lon'] = pd.to_numeric(df['origin_coord_lon'].str[1])

    df['destination_coord_lat'] = df['destination_coord'].str.extract(r"(?<=POINT \()(.*)(?=\))")
    df['destination_coord_lat'] = df['destination_coord_lat'].str.split(' ')
    df['destination_coord_lat'] = pd.to_numeric(df['destination_coord_lat'].str[0])

    df['destination_coord_lon'] = df['destination_coord'].str.extract(r"(?<=POINT \()(.*)(?=\))")
    df['destination_coord_lon'] = df['destination_coord_lon'].str.split(' ')
    df['destination_coord_lon'] = pd.to_numeric(df['destination_coord_lon'].str[1])

    #converts to datetime
    df['datetime'] = pd.to_datetime(df['datetime'])

    #group by similar origin/destination/time
    df = df.groupby(df.columns.tolist(), as_index=False).size()

    #replace if values came with comma instead of dot
    upper_value_lat = float(upper_value_lat.replace(',', '.'))
    lower_value_lat = float(lower_value_lat.replace(',', '.'))
    upper_value_lon = float(upper_value_lon.replace(',', '.'))
    lower_value_lon = float(lower_value_lon.replace(',', '.'))

    #checks whether origin or dest
    if origin_dest == 'origin':
        df = df[(df['origin_coord_lat'] >= lower_value_lat)
                & (df['origin_coord_lat'] <= upper_value_lat)
                & (df['origin_coord_lon'] <= upper_value_lon)
                & (df['origin_coord_lon'] >= lower_value_lon)
        ]
    if origin_dest == 'dest':
        df = df[(df['dest_coord_lat'] >= lower_value_lat)
                & (df['dest_coord_lat'] <= upper_value_lat)
                & (df['dest_coord_lon'] <= upper_value_lon)
                & (df['dest_coord_lon'] >= lower_value_lon)
        ]

    #groupBy region
    df['datetime'] = pd.to_datetime(df['datetime']) - pd.to_timedelta(7, unit='d')
    df = df.groupby(['region', pd.Grouper(key='datetime', freq='W-MON')])['size']\
    .count()\
    .reset_index()\
    .sort_values('datetime')

    df['size'] = df['size']/7

    df.rename(columns={'datetime':'week', 'size':'week_average'}, inplace=True)

    return df

def load(df, table_name):
    engine = create_engine('sqlite:////database/trips.db', echo=True)
    sqlite_connection = engine.connect()
    df.to_sql(table_name, sqlite_connection, if_exists='replace') #change here to 'append' if you want to load multiple different files.
    sqlite_connection.close()
    return True

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/coordinates/<origindest>/<upper_v_lat>/<lower_v_lat>/<upper_v_lon>/<lower_v_lon>/<file_name>', methods=['GET'])
def tolerance_func(origindest, upper_v_lat, lower_v_lat, upper_v_lon, lower_v_lon,file_name):
    table_name = "weekly_trips_by_coordinates"
    df = extract(file_name)
    df = transform_coordinates(df, origindest, upper_v_lat, lower_v_lat, upper_v_lon, lower_v_lon)
    load(df, table_name)
    return f"<h1>Load Trips Data</h1><p>Load has completed with defined parameters for {origindest}</p>"

@app.route('/region/<region>/<file_name>', methods=['GET'])
def region_func(region,file_name):
    table_name = "weekly_trips_by_region"
    df = extract(file_name)
    df = transform_region(df, region)
    load(df, table_name)
    return f"<h1>Load Trips Data</h1><p>Load has completed with defined parameters for {region}</p>"

