import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
# from dash import callback_context
import dash

import pandas as pd
import geopandas as gpd
import numpy as np

from sqlalchemy import create_engine
import psycopg2
import os

import plotly.express as px
from urllib.request import urlopen
import json
import pathlib

POSTGRES_HOST = os.environ.get('POSTGRES_HOST', default="postgres")
POSTGRES_USER = os.environ.get('POSTGRES_USER', default="realityadmin")
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', default="Reality1!")
db_dane = {
            'name': POSTGRES_USER, 
            'password': POSTGRES_PASSWORD, 
            'hostname': POSTGRES_HOST, 
            'db_name': 'realestate_zero'
}

def PostgreSQL_connectSQLalchemy():
    db_connection_str = 'postgresql://{name}:{password}@{hostname}/{db_name}'.format(**db_dane)
    db_connection = create_engine(db_connection_str)
    return db_connection.connect()

def PostgreSQL_connectPsycopg2():
    con = psycopg2.connect(user=db_dane['name'], password=db_dane['password'], host=db_dane['hostname'],
                           database=db_dane['db_name'])
    return con



app = DjangoDash('MapGraph', id='city_name')

app.layout = html.Div([
    html.H2('Dane na temat dzielnic'),
    dcc.Graph(id='slider-graph', animate=True, style={"backgroundColor": "#1a2d46", 'color': '#ffffff', "height":"60vh"}),
    dcc.Input(id='city_name', type='hidden', value='warszawa')
])


@app.callback(
               Output('slider-graph', 'figure'),
              [Input('city_name', 'value')])
def display_value(city):
    script_dir = os.path.dirname(__file__)
    rel_path = f"districts/{city}.json"
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path) as response:
        counties = json.load(response)
    conn = PostgreSQL_connectSQLalchemy()
    df = pd.read_sql( f"""SELECT * FROM "oferty_merged" WHERE "oferty_merged"."Miasto"='{city}' """, con=conn )
    df = df[df['Price_per_metr'] < np.percentile(df['Price_per_metr'],98)]
    df = df[df['Price_per_metr'] > np.percentile(df['Price_per_metr'], 3)]
    df = df.groupby(['Dzielnica'], as_index=False).agg(
                                                        mean            = ('Price_per_metr', 'mean'),
                                                        count           = ('Price_per_metr', 'count'),
                                                        min             = ('Price_per_metr', np.min),
                                                        percentile_25   = ('Price_per_metr', lambda x: np.percentile(x, q = 25)), 
                                                        median          = ('Price_per_metr', np.median),
                                                        percentile_75   = ('Price_per_metr', lambda x: np.percentile(x, q = 75)),
                                                        percentile_90   = ('Price_per_metr', lambda x: np.percentile(x, q = 90)), 
                                                        max             = ('Price_per_metr', np.max)
                                                    )
    latlonDict = {
                    'warszawa':     [52.237, 21.017,  9.5], 
                    'krakow':       [50.05,  19.985,  10.1],
                    'lodz':         [51.76,  19.457,   10],  
                    'wroclaw':      [51.108, 17.039,   10], 
                    'poznan':       [52.409, 16.932,  9.7], 
                    'gdansk':       [54.372, 18.638,  9.6], 
                    'szczecin':     [53.428, 14.553,  9.6], 
                    'bydgoszcz':    [53.123, 18.008, 10.2], 
                    'lublin':       [51.216, 22.568, 10.2],
                    'bialystok':    [53.128, 23.126, 10.5]
    }
    fig = px.choropleth_mapbox(df, geojson=counties, featureidkey='properties.name', locations='Dzielnica', color='mean',
                                color_continuous_scale="Viridis",
                                range_color=(df['mean'].min(), df['mean'].max()),
                                mapbox_style="open-street-map",
                                zoom=latlonDict[city][2], center = {"lat": latlonDict[city][0], "lon": latlonDict[city][1]},
                                opacity=0.5,
                                labels={
                                    'mean':'Srednia cena za m2',
                                    'count':'Liczba ofert',
                                    'min':'Cena minimalna',
                                    'percentile_25':'Percentyl 25%',
                                    'median':'Mediana',
                                    'percentile_75':'Percentyl 75%',
                                    'percentile_90':'Percentyl 90%',
                                    'max':'Cena maksymalna'
                                    }
                                )
    return fig