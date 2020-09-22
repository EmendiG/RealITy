import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from django_plotly_dash import DjangoDash
# from dash import callback_context
import dash
import dpd_components as dpd
import dash_bootstrap_components as dbc

import pandas as pd
import geopandas as gpd
import numpy as np
import re

from sqlalchemy import create_engine
import psycopg2
import os

import plotly.express as px
import plotly.graph_objects as go
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



app = DjangoDash('MapGraph', id='city_name', add_bootstrap_links=True,  meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])


app.layout = html.Div([
    html.H1('Wybierz dzielnicę i sprawdź informacje:', style={"font-weight": "700", "margin-bottom":"0.5rem", "font-size":"2.5rem", "line-height":"1.2", "font-family":'"Montserrat", Segoe UI, Roboto, Helvetica Neue'}),
    dcc.Graph(
        id='slider-graph',
        style={
            "backgroundColor": "#1a2d46", 
            'color': '#ffffff', 
            "height":"60vh",
            "width":"auto",
        },
    ),
 
    html.Div([
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='df_dropdown_type',
                            options=[
                                {'label': 'Cena za m2', 'value': 'Price_per_metr'},
                                {'label': 'Powierzchnia', 'value': 'Area'},
                                {'label': 'Cena calkowita', 'value': 'Price'},
                                {'label': 'Rok', 'value': 'Rok_zabudowy'},
                                {'label': 'Liczba_pokoi', 'value': 'Liczba_pokoi'},
                                {'label': 'Pietro', 'value': 'Pietro'}
                            ],
                            value='Price_per_metr'
                        )
                    ],
                    width=4
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='df_dropdown_options',
                            options=[
                                {'label': 'Srednia wartosc', 'value': 'mean'},
                                {'label': 'Liczba pomiarow', 'value': 'count'},
                                {'label': 'Wartosc minimalna', 'value': 'min'},
                                {'label': 'Percentyl 25%', 'value': 'percentile_25'},
                                {'label': 'Mediana', 'value': 'median'},
                                {'label': 'Percentyl 75%', 'value': 'percentile_75'},
                                {'label': 'Percentyl 90%', 'value': 'percentile_90'},
                                {'label': 'Wartosc maksymalna', 'value': 'max'},
                            ],
                            value='mean'
                        )
                    ],
                    width=4
                ),
                dbc.Col(
                    [
                        dcc.Dropdown(
                            id='df_dropdown_accuracy',
                            options=[
                                {'label': 'Dokladnosc do calosci', 'value': "0"},
                                {'label': 'Dokladnosc 0.1', 'value': "1"},
                                {'label': 'Dokladnosc 0.2', 'value': "2"},
                                {'label': 'Dokladnosc 0.3', 'value': "3"},
                            ],
                            value="0"
                        )
                    ],
                    width=4
                )
            ]
        )
    ], style={"width":"98vw", "padding-left":"2vw"}),
    
    dcc.Input(id='city_name', type='hidden', value='warszawa')
])


@app.callback(
                Output('slider-graph', 'figure'),
                [
                Input('df_dropdown_type', 'value'),
                Input('df_dropdown_options', 'value'),
                Input('df_dropdown_accuracy', 'value'),
                Input('city_name', 'value')
                ]
)
def display_value(df_type ,dropdown, accuracy, city):
    script_dir = os.path.dirname(__file__)
    rel_path = f"districts/{city}.json"
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path) as response:
        counties = json.load(response)
    conn = PostgreSQL_connectSQLalchemy()
    df = pd.read_sql( f"""SELECT * FROM "oferty_merged" WHERE "oferty_merged"."Miasto"='{city}' """, con=conn )
    if df_type not in ['Price_per_metr', 'Area', 'Price']:
        df = df[df[f'{df_type}'].apply(lambda x: str(x).isdigit())]
        df[f'{df_type}'] = pd.to_numeric(df[f'{df_type}'])
    df = df[df[f'{df_type}'] < np.percentile(df[f'{df_type}'],99)]
    df = df[df[f'{df_type}'] > np.percentile(df[f'{df_type}'], 2)]
    df = df.groupby(['Dzielnica'], as_index=False).agg(
                                                        mean            = (f'{df_type}', 'mean'),
                                                        count           = (f'{df_type}', 'count'),
                                                        min             = (f'{df_type}', np.min,),
                                                        percentile_25   = (f'{df_type}', lambda x: np.percentile(x, q = 25)), 
                                                        median          = (f'{df_type}', np.median),
                                                        percentile_75   = (f'{df_type}', lambda x: np.percentile(x, q = 75)),
                                                        percentile_90   = (f'{df_type}', lambda x: np.percentile(x, q = 90)), 
                                                        max             = (f'{df_type}', np.max)
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
    labels={
            'mean':'Srednia wartosc',
            'count':'Liczba pomiarow',
            'min':'Wartosc minimalna',
            'percentile_25':'Percentyl 25%',
            'median':'Mediana',
            'percentile_75':'Percentyl 75%',
            'percentile_90':'Percentyl 90%',
            'max':'Wartosc maksymalna'
    }

    fig = go.Figure(go.Choroplethmapbox(geojson=counties, 
                                        featureidkey='properties.name', 
                                        locations=df['Dzielnica'], 
                                        zmin=df[f'{dropdown}'].min(),
                                        z=df[f'{dropdown}'], 
                                        zmax=df[f'{dropdown}'].max(),
                                        colorscale="YlOrRD", 
                                        marker_opacity=0.5, 
                                        marker_line_width=0.1,
                                        hovertemplate= '<b>%{customdata[0]}</b>' + 
                                                       f'<br><b>{labels[dropdown]}</b>:' +  
                                                       '<br>Min:' +
                                                       '<br>Mediana:' +
                                                       '<br>Max:' +

                                                       "<extra><br></extra>"
                                                       '<extra><b>%{z:.' +f"{accuracy}" + "f}</b></extra>"+
                                                       '<br><extra>%{customdata[1]:.' +f"{accuracy}" + "f}</extra>"+
                                                       '<br><extra>%{customdata[2]:.' +f"{accuracy}" + "f}</extra>"+
                                                       '<br><extra>%{customdata[3]:.' +f"{accuracy}" + "f}</extra>",
                                        customdata=df.loc[:, ['Dzielnica', 'min','median', 'max']],
                                        colorbar={ 
                                            #'xanchor':'right', 
                                            #'xpad':60,
                                            'x':0.04
                                        },                                        
                                        
                    )
    )
    fig.update_layout(mapbox_style="open-street-map",
                      mapbox_zoom=latlonDict[city][2], 
                      mapbox_center = {"lat": latlonDict[city][0], "lon": latlonDict[city][1]},
                      margin={"r":0,"t":0,"l":0,"b":20}
    )
    return fig