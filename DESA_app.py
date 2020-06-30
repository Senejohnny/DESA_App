import base64
import datetime
import io
import sys
import pandas as pd
# from urllib.parse import quote 

import dash
from dash import no_update
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame


from app.Dash import parse_contents, upload_file
from app.DESA import DataPreparation, Analysis
from app.DESA.Loading import load_EpitopeDB 

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
# server = Flask(__name__)
# app = dash.Dash(server=server)  #, external_stylesheets=external_stylesheets)

app = dash.Dash(__name__) #, external_stylesheets=external_stylesheets)

# ######################################################################
# Pre Layout variabels & functions
# ######################################################################

all_EpitopeDB_options = {
    'Epitope DB Exposure': {'Opts': ['Exposed', 'All'], 'Path': './data/Epitope_DB_Expossure.xlsx'},
    'Epitope DB ElliPro':  {'Opts': ['High', 'Intermediate', 'Low', 'Very Low'], 'Path': './data/Epitope_BD_ElliPro.xlsx'}
}

# ######################################################################
# Layout
# ######################################################################
app.layout = html.Div(
    [
        html.Div(className='row',
        children=[
            html.Div(className='four columns div-left-panel',
            children=
            [
                #Title
                html.H3("Finding DESA for Graft Transplantation"),
                html.Hr(),
                # Upload HLA & MFI Files
                html.H5(['Upload HLA & Luminex Data [.csv & .xlsx]']),
                    html.Div([
                        upload_file('HLA', id='upload-HLA-data'),
                        upload_file('Luminex', id='upload-MFI-data'),
                    ], style={'padding': 0, 'columnCount': 1},
                    ),
                # html.Div(id='output-MFI-data_upload'), 
                html.Hr(),
                #--------------------------------------------------------
                # Epitope DataBase selection
                #--------------------------------------------------------
                # Epitope DB type
                html.Label('Epitope Database'),
                html.Div([
                    dcc.RadioItems(
                        id='EpitopeDB-dropdown',
                        options=
                            [
                            {'label': i, 'value': i} for i in all_EpitopeDB_options.keys()
                            ],
                        value='Epitope DB Exposure',
                    ),
                ], style={'padding': 0, 'columnCount': 2},
                ),
                    html.Br(),
                # DB options
                html.Div([
                html.Label('Database Options'),
                    dcc.Dropdown(
                        id='EpitopeDB-More-Opts-dropdown',
                        placeholder="Select",
                    ),
                ], style={'padding': 0, 'columnCount': 1},
                ),
                html.Br(),
                # Epitope Reactivity
                html.Label('Epitope Reactivity'),
                html.Div(
                [ 
                    dcc.RadioItems(id='reactivity-radio',
                        options=[
                            {'label': 'Confirmed', 'value': 'Confirmed'},
                            {'label': 'All', 'value': 'All'}
                        ],
                        value='All',
                    ),
                ], style={'padding': 1, 'columnCount': 2}, ),
                html.Br(),
                # Allel type
                html.Label('Alleles Type'),
                html.Div(
                [ 
                    dcc.RadioItems(id='alleltype-radio',
                        options=[
                            {'label': 'Luminex Alleles', 'value': 'Luminex Alleles'},
                            {'label': 'All Alleles', 'value': 'All Alleles'}
                        ],
                        value='All Alleles',
                    ),
                ], style={'padding': 1, 'columnCount': 2}, ),
            html.Br(),
            html.Button(id='submit-button-state', n_clicks=0, children='Start Analysis'),
            ],),
            # Middle Section
            html.Div(className='four columns div-for-charts bg-grey',
                children=
                [
                    html.H3('Output Console:'),
                    html.Div(id='output-HLA-data-upload'),
                    html.Div(id='output-MFI-data-upload'),
                    html.Div(id='output-state'),
                    # Hidden div inside the app that stores the intermediate value
                    html.Div(id='hidden-MFI-data', style={'display': 'none'}),
                    html.Div(id='hidden-HLA-data', style={'display': 'none'}),
                    html.Div(id='hidden-Results', style={'display': 'none'}),
                    # progress bar
                    dbc.Progress(id="progress", value=0, striped=True, animated=True),
                    # Download the results in csv File
                    html.H2("Download Results"),
                    html.Div([
                        html.Button("Download", id="download-buttion"), 
                        Download(id="download"),
                    ]),
                ]),
            # Right Section 
            html.Div(className='four columns div-for-about',
                children=[
                    html.H3('About'),
                    html.P('The luminex data only takes into account the DP locus')
            ],),
        ],),
    ],)


######################################################################
# Callbacks
######################################################################

@app.callback(
    Output('EpitopeDB-More-Opts-dropdown', 'options'),
    [Input('EpitopeDB-dropdown', 'value')],)
def set_EpitopeDB_options(EpitopeDB):
    return  [{'label': i, 'value': i} for i in all_EpitopeDB_options[EpitopeDB]['Opts']]

@app.callback(
    [Output('EpitopeDB-More-Opts-dropdown', 'value'),
    Output('EpitopeDB-More-Opts-dropdown', 'multi'), ],
    [Input('EpitopeDB-More-Opts-dropdown', 'options'), 
    Input('EpitopeDB-dropdown', 'value'), ])
def set_EpitopeDB_More_Opts_value(available_options, value):
    multi = False if value == 'Epitope DB Exposure' else True
    return available_options[0]['value'], multi

@app.callback([Output('hidden-HLA-data', 'children'),
            Output('output-HLA-data-upload', 'children'),], 
            [Input('upload-HLA-data', 'contents'),],
            [State('upload-HLA-data', 'filename'),])
def update_output_HLA_data(contents, filename):
    if contents is not None:
        df_json, children = parse_contents(contents, filename, 'HLA')
        return df_json, children
    else:
        return no_update,  html.Div(['No HLA data is uploaded'])

@app.callback([Output('hidden-MFI-data', 'children'),
            Output('output-MFI-data-upload', 'children'),],
            [Input('upload-MFI-data', 'contents'),],
            [State('upload-MFI-data', 'filename'),])
def update_output_MFI_data(contents, filename):
    if contents is not None:
        df_json, children = parse_contents(contents, filename, 'Luminex')
        return df_json, children
    else:
        return no_update,  html.Div(['No MFI data is uploaded'])


@app.callback([Output('output-state', 'children'),
            Output('hidden-Results', 'children'),],
            [Input('submit-button-state', 'n_clicks')],
            [State('EpitopeDB-dropdown', 'value'), 
            State('EpitopeDB-More-Opts-dropdown', 'value'),
            State('reactivity-radio', 'value'),
            State('alleltype-radio', 'value'),
            State('hidden-HLA-data', 'children'),
            State('hidden-MFI-data', 'children'),])
def Main_Analysis(n_clicks, EpitopeDB_type, DB_Opts, Reactivity, Allel_type, HLA, MFI):
    if n_clicks != 0:
        if MFI == None or HLA == None:
            return html.P(f""" No MFI or HLA file is uploaded """), no_update
        path = all_EpitopeDB_options[EpitopeDB_type]['Path']
        EpitopeDB = load_EpitopeDB(path)
        EpitopeDB = DataPreparation.prep_EpitopeDB(EpitopeDB)
        EpitopeDB_filtered = DataPreparation.filter_EpitopeDB(EpitopeDB, Allel_type, DB_Opts, Reactivity)
        HLAvsEpitope = DataPreparation.EpvsHLA2HLAvsEp(EpitopeDB_filtered, Allel_type)
        MFI = pd.read_json(MFI, orient='split')
        MFI = DataPreparation.prep_MFI(MFI, Exclude_Locus=['DP'])
        HLA = pd.read_json(HLA, orient='split')
        HLA = DataPreparation.prep_HLA(HLA)
        final_df = Analysis.write_DESAdf(HLA, MFI, HLAvsEpitope) #, TxIDs=[4811])
        return f"""{EpitopeDB_type} is selected with options:
                {DB_Opts} Epotiopes, {Reactivity} reactivity, and {Allel_type}
                """, final_df.to_json(orient='split')
    else:
        return no_update, no_update


@app.callback(Output("download", "data"), 
            [Input("download-buttion", "n_clicks")],
            [State('hidden-Results', 'children'),
            State('EpitopeDB-dropdown', 'value'),])
def generate_csv(n_clicks, final_df, EpitopeDB_type): 
    if n_clicks != 0:
        if final_df is not None:
            final_df = pd.read_json(final_df, orient='split')
            return send_data_frame(final_df.to_csv, filename=f"DESA, {EpitopeDB_type}.csv")


if __name__ == '__main__':
    app.run_server(debug=True)