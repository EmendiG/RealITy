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
import numpy as np
from pandas.api.types import is_numeric_dtype

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



app = DjangoDash(
                'MapGraph', 
                id='city_name', 
                add_bootstrap_links=True,  

                config={
                    'responsive': True
                },
                style={
                    'width': 'auto', 
                    "overflow":"hidden",   
                    "overflow-y":"hidden"
                },
                external_stylesheets=[dbc.themes.SLATE], 
                meta_tags=[{
                        "name": "viewport", 
                        "content": "width=device-width, initial-scale=1"
                }
                ]
)

external_stylesheets = [{
'external_url': 'https://fonts.googleapis.com/css?family=Montserrat:400,700',
'external_url': '/static/thema/css/main.css', 
# 'external_url': '../static/thema/css/main.css', 
},
]
for stylesheet in external_stylesheets:
	app.css.append_css(stylesheet)

app.layout = html.Div(
    [   
        dcc.Input(id='city_name', type='hidden', value='warszawa'),
        html.H1('Wybierz dzielnicę i sprawdź informacje:',  
                id="content-desktop",
                style={
                        "font-weight": "700", 
                        "margin-bottom":"0.5rem", 
                        "font-size":"2.5rem", 
                        "line-height":"1.2", 
                        "font-family":'"Montserrat", sans-serif, Segoe UI'
                }
        ),
        html.H1('Wybierz dzielnicę i sprawdź informacje:',  
                id="content-mobile",
                style={
                        "font-size":"4vw",
                        "font-weight":"700",
                        "line-height":"1.2", 
                        "font-family":'"Montserrat", sans-serif, Segoe UI'
                }
        ),

        html.Div(
            dcc.Graph(
                id='map-graph',
                className="mapka_plotly",
                style={
                    "backgroundColor": "#1a2d46", 
                    'color': '#ffffff', 
                    "width":"auto"
                },
            )
        ),

        html.Div([
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.P(
                                    'Wybierz szukaną cechę na powyższej mapie:'
                                ),
                            dcc.Dropdown(
                                id='df_dropdown_type',
                                options=[
                                    {'label': 'Cena za m2', 'value': 'Price_per_metr'},
                                    {'label': 'Powierzchnia', 'value': 'Area'},
                                    {'label': 'Cena calkowita', 'value': 'Price'},
                                    {'label': 'Rok', 'value': 'Rok_zabudowy'},
                                    {'label': 'Liczba pokoi', 'value': 'Liczba_pokoi'},
                                    {'label': 'Pietro', 'value': 'Pietro'}
                                ],
                                value='Price_per_metr'
                            )
                        ],
                        width=4
                    ),
                    dbc.Col(
                        [
                            html.P(
                                    'Wybierz typ miarę cechy na powyższej mapie:'
                                ),
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
                            html.P(
                                    'Wybierz dokładność na powyższej mapie:'
                                ),
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

        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.P(
                                    'Wybierz oś Y na poniższym grafie:'
                                ),
                                dcc.Dropdown(
                                    id='scatter_y',
                                    options=[
                                        {'label': 'Cena za m2', 'value': 'Price_per_metr'},
                                        {'label': 'Powierzchnia', 'value': 'Area'},
                                        {'label': 'Cena calkowita', 'value': 'Price'},
                                        {'label': 'Rok', 'value': 'Rok_zabudowy'},
                                        {'label': 'Liczba pokoi', 'value': 'Liczba_pokoi'},
                                        {'label': 'Pietro', 'value': 'Pietro'}
                                    ],
                                    value='Price_per_metr'
                                )
                            ],
                            width=4
                        ),
                        dbc.Col(
                            [
                                html.P(
                                    'Wybierz oś X na poniższym grafie:'
                                ),
                                dcc.Dropdown(
                                    id='scatter_x',
                                options=[
                                        {'label': 'Cena za m2', 'value': 'Price_per_metr'},
                                        {'label': 'Powierzchnia', 'value': 'Area'},
                                        {'label': 'Cena calkowita', 'value': 'Price'},
                                        {'label': 'Rok', 'value': 'Rok_zabudowy'},
                                        {'label': 'Liczba pokoi', 'value': 'Liczba_pokoi'},
                                        {'label': 'Pietro', 'value': 'Pietro'}
                                    ],
                                    value='Area'
                                )
                            ],
                            width=4
                        ),
                        dbc.Col(
                            [
                                html.P(
                                    'Wybierz zmienną koloru na poniższym grafie:'
                                ),
                                dcc.Dropdown(
                                    id='scatter_color',
                                options=[
                                        {'label': 'Cena za m2', 'value': 'Price_per_metr'},
                                        {'label': 'Powierzchnia', 'value': 'Area'},
                                        {'label': 'Cena calkowita', 'value': 'Price'},
                                        {'label': 'Rok', 'value': 'Rok_zabudowy'},
                                        {'label': 'Liczba pokoi', 'value': 'Liczba_pokoi'},
                                        {'label': 'Pietro', 'value': 'Pietro'}
                                    ],
                                    value='Price'
                                )
                            ],
                            width=4
                        )
                    ]
                )
            ], style={"width":"98vw", "padding-left":"2vw", "padding-top":"1vw", "padding-bottom":"1vw"}
        ),

        html.Div(
            [
                dcc.Graph(
                    id='scatter-graph',
                    className="scatter_plotly",
                    style={
                            "backgroundColor": "#1a2d46", 
                            'color': '#ffffff', 
                            "width":"auto",
                    },
                )
            ],  
        ),
        
        
    ], style={'width': 'auto', "height":"100%", "overflow-y":"hidden", "overflow-x":"hidden"} # 
)
# TODO: I would suggest using dbc.Row and dbc.Col to control the layout rather than setting float property !!!!!!!
# https://community.plotly.com/t/how-to-get-a-responsive-layout/18029/6


@app.callback(
                Output('map-graph', 'figure'),
                [
                Input('df_dropdown_type', 'value'),
                Input('df_dropdown_options', 'value'),
                Input('df_dropdown_accuracy', 'value'),
                Input('city_name', 'value')
                ]
)
def display_value(drop_type ,dropdown, accuracy, city):
    script_dir = os.path.dirname(__file__)
    rel_path = f"districts/{city}.json"
    abs_file_path = os.path.join(script_dir, rel_path)
    with open(abs_file_path) as response:
        counties = json.load(response)
    conn = PostgreSQL_connectSQLalchemy()
    global how_many_times
    how_many_times = 0
    global df_zero
    df_zero = pd.read_sql( f"""SELECT * FROM "oferty_merged" WHERE "oferty_merged"."Miasto"='{city}' """, con=conn )
    df_raw = df_zero.copy()
    if drop_type not in ['Price_per_metr', 'Area', 'Price']:
        df_raw = df_raw[df_raw[f'{drop_type}'].apply(lambda x: str(x).isdigit())]
        df_raw[f'{drop_type}'] = pd.to_numeric(df_raw[f'{drop_type}'])
    df_raw = df_raw[df_raw[f'{drop_type}'] < np.percentile(df_raw[f'{drop_type}'],99)]
    df_raw = df_raw[df_raw[f'{drop_type}'] > np.percentile(df_raw[f'{drop_type}'], 2)]
    df = df_raw.groupby(['Dzielnica'], as_index=False).agg(
                                                        mean            = (f'{drop_type}', 'mean'),
                                                        count           = (f'{drop_type}', 'count'),
                                                        min             = (f'{drop_type}', np.min,),
                                                        percentile_25   = (f'{drop_type}', lambda x: np.percentile(x, q = 25)), 
                                                        median          = (f'{drop_type}', np.median),
                                                        percentile_75   = (f'{drop_type}', lambda x: np.percentile(x, q = 75)),
                                                        percentile_90   = (f'{drop_type}', lambda x: np.percentile(x, q = 90)), 
                                                        max             = (f'{drop_type}', np.max)
                                                    )
    latlonDict = {
                    'warszawa':     [52.237, 21.017,  9.5], 
                    'krakow':       [50.05,  19.985, 10.1],
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

    fig = go.Figure(go.Choroplethmapbox(
                                        geojson=counties, 
                                        featureidkey='properties.name', 
                                        locations=df['Dzielnica'], 
                                        zmin=df[f'{dropdown}'].min(),
                                        z=df[f'{dropdown}'], 
                                        zmax=df[f'{dropdown}'].max(),
                                        colorscale="YlOrRD", 
                                        marker_opacity=0.5, 
                                        marker_line_width=0.5,
                                        hovertemplate= '<b>%{customdata[0]}</b>' + 
                                                       f'<br><b>{labels[dropdown]}</b>:' + 
                                                       '<br>Liczba pomiarow:' + 
                                                       '<br>Min:' +
                                                       '<br>Mediana:' +
                                                       '<br>Max:' +

                                                       "<extra><br></extra>"
                                                       '<extra><b>%{z:.' +f"{accuracy}" + "f}</b></extra>"+
                                                       '<br><extra>%{customdata[1]:.' +f"{accuracy}" + "f}</extra>"+
                                                       '<br><extra>%{customdata[2]:.' +f"{accuracy}" + "f}</extra>"+
                                                       '<br><extra>%{customdata[3]:.' +f"{accuracy}" + "f}</extra>"+
                                                       '<br><extra>%{customdata[4]:.' +f"{accuracy}" + "f}</extra>",
                                        customdata=df.loc[:, ['Dzielnica', 'count', 'min','median', 'max']],
                                        colorbar={ 
                                            'x':0.04
                                        },                                        
                                        
                    )
    )
    fig.update_layout(
                        mapbox_style="open-street-map",
                        mapbox_zoom=latlonDict[city][2], 
                        mapbox_center = {"lat": latlonDict[city][0], "lon": latlonDict[city][1]},
                        autosize=True,
                        margin={"r":0,"t":0,"l":0,"b":20}
    )
    return fig

@app.callback(
                Output('scatter-graph', 'figure'),
                [
                Input('map-graph', 'clickData'),
                Input('scatter_x', 'value'),
                Input('scatter_y', 'value'), 
                Input('scatter_color', 'value'),
                ]
)
def change_value(selectedData, chosen_X, chosen_y, chosen_color):
    if type(selectedData) is not type(None):
        district = selectedData['points'][0].get('location')
        global df_zero
        global how_many_times
        
        how_many_times += 1
        if how_many_times == 1:
            df_zero = df_zero[df_zero[f'{chosen_X}'] < np.percentile(df_zero[f'{chosen_X}'],99)]
            df_zero = df_zero[df_zero[f'{chosen_X}'] > np.percentile(df_zero[f'{chosen_X}'], 2)]
            df_zero = df_zero[df_zero[f'{chosen_y}'] < np.percentile(df_zero[f'{chosen_y}'],99)]
            df_zero = df_zero[df_zero[f'{chosen_y}'] > np.percentile(df_zero[f'{chosen_y}'], 2)]
        
        if not is_numeric_dtype(df_zero[f'{chosen_X}']):
            df_zero = df_zero[df_zero[f'{chosen_X}'].apply(lambda x: str(x).isdigit())]
            df_zero[f'{chosen_X}'] = pd.to_numeric(df_zero[f'{chosen_X}'])
            df_zero = df_zero[df_zero[f'{chosen_X}'] < np.percentile(df_zero[f'{chosen_X}'],99)]
            df_zero = df_zero[df_zero[f'{chosen_X}'] > np.percentile(df_zero[f'{chosen_X}'], 2)]
        
        if not is_numeric_dtype(df_zero[f'{chosen_y}']):
            df_zero = df_zero[df_zero[f'{chosen_y}'].apply(lambda x: str(x).isdigit())]
            df_zero[f'{chosen_y}'] = pd.to_numeric(df_zero[f'{chosen_y}'])
            df_zero = df_zero[df_zero[f'{chosen_y}'] < np.percentile(df_zero[f'{chosen_y}'],99)]
            df_zero = df_zero[df_zero[f'{chosen_y}'] > np.percentile(df_zero[f'{chosen_y}'], 2)]

        if not is_numeric_dtype(df_zero[f'{chosen_color}']):
            df_zero = df_zero[df_zero[f'{chosen_color}'].apply(lambda x: str(x).isdigit())]
            df_zero[f'{chosen_color}'] = pd.to_numeric(df_zero[f'{chosen_color}'])
            df_zero = df_zero[df_zero[f'{chosen_color}'] < np.percentile(df_zero[f'{chosen_color}'],99)]
            df_zero = df_zero[df_zero[f'{chosen_color}'] > np.percentile(df_zero[f'{chosen_color}'], 2)]

        labeltrans={
            'Price_per_metr':'Cena za m2',
            'Area':'Powierzchnia',
            'Price':'Cena calkowita',
            'Rok_zabudowy':'Rok',
            'Liczba_pokoi':'Liczba pokoi',
            'Pietro':'Pietro'
        }
        labelsuffix = {
            'Price_per_metr':'PLN/m2',
            'Area':'m2',
            'Price':'PLN',
            'Rok_zabudowy':'rok',
            'Liczba_pokoi':'pokoi',
            'Pietro':'pietro'
        }
        fig = go.Figure(data=go.Scatter(
                                        x=df_zero[df_zero['Dzielnica'] == district][f'{chosen_X}'],
                                        y=df_zero[df_zero['Dzielnica'] == district][f'{chosen_y}'],
                                        mode='markers',
                                        marker={
                                            'color':df_zero[df_zero['Dzielnica'] == district][f'{chosen_color}'],
                                            'colorscale':"Sunsetdark",
                                            'colorbar':{
                                                'x':0.95
                                            }
                                        },
                                        hovertemplate=
                                                       '%{y:.1f}' + f' {labelsuffix.get(chosen_y)}'+
                                                       '<br>%{x:.1f}' + f' {labelsuffix.get(chosen_X)}' +
                                                       "<extra></extra>",
                        )
        )

        fig.update_layout(
                        autosize=True,
                        margin={"r":0,"t":40,"l":0,"b":20},
                        title={
                            'text': '<b>'+ district +'</b>',
                            'xanchor': 'center',
                            'yanchor': 'top',
                            'x':0.5,
                            'font':{
                                'size':20
                            }
                        },
                        xaxis_title=labeltrans.get(chosen_X),
                        yaxis_title=labeltrans.get(chosen_y),
        )
        fig.layout.plot_bgcolor = '#fff'
        fig.layout.paper_bgcolor = '#fff'
        fig.update_xaxes(showline=True, linewidth=2, linecolor='black', gridwidth=0.1, gridcolor='Lightgrey')
        fig.update_yaxes(showline=True, linewidth=2, linecolor='black', gridwidth=0.1, gridcolor='Lightgrey')
        return fig
    else:
        fig = go.Figure(data=go.Scatter())
        fig.update_layout(
                        autosize=True,
                        margin={"r":0,"t":20,"l":0,"b":20}
        )
        fig.layout.plot_bgcolor = '#fff'
        fig.layout.paper_bgcolor = '#fff'
        fig.update_xaxes(showline=True, linewidth=2, linecolor='black')
        fig.update_yaxes(showline=True, linewidth=2, linecolor='black')
        return fig