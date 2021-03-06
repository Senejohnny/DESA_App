import io 
import base64
import pandas as pd


import dash
from dash import no_update
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from app.DESA.utils import detectdelimiter


#####################################################################################
# File Upload
#####################################################################################
def upload_file(Data_Type:str, id:str = ''):
    return dcc.Upload(id=id,
                children=html.Div(
                [
                    # f'Drag and Drop {Data_Type} Data ',
                    html.A(f'Upload {Data_Type} File')
                ]),
                style={
                    'width': '60%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '20px'
                },
                # Allow multiple files to be uploaded
                multiple=False,
           )


#####################################################################################
# Parse Uploaded file
#####################################################################################
def parse_contents(contents, filename, Data_type:str):

    if '.' not in filename:
        return html.Div(f"""Error: filename {filename} does not contain extension. Make sure filename contains
        supported file extension e.g. .csv, .xlsx.""")

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string) # decode byte-like object or ASCII into bytes 
    try:
        if filename.rsplit('.', 1)[1].lower() == 'csv':
            # Assume that the user uploaded a CSV file
            string = decoded.decode('utf-8') # decode bytes into string 
            file = io.StringIO(string)    # StringIO is an in-memory stream for text I/O
            delimiter = detectdelimiter(file) # find the delimiter of the csv file
            df = pd.read_csv(file, sep=delimiter)
            file.close()                       # close StringIO object
        elif filename.rsplit('.', 1)[1].lower() in ['xls', 'xlsx']:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))     #BytesIO is an in-memory stream for text I/O
    except Exception as e:
        print(e)
        return no_update, html.Div(["""
                                There was an error processing this file. 
                                File extension might not supported. 
                                Supported file extensions .csv, .xls, .xlsx
                                """])
    return df.to_json(orient='split'), html.Div([
                            html.Div([
                                f"""
                                {Data_type} data is successfully uploaded as {filename} !
                                """
                            ]),
                            html.Label('--' * 40),  # horizontal line
                        ])


