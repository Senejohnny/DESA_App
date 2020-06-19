from flask import Flask, flash, request, redirect, url_for, render_template, session
from flask_restful import Resource, Api
from werkzeug.utils import secure_filename
import os
import pandas as pd
ALLOWED_EXTENSIONS = {'csv', 'xls'}

app = Flask(__name__)
api = Api(app)
app.secret_key = 'session_key'

class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/api')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detectdelimiter(file): 
    """
    this will detect the famous delimiters [',', ';', ':', '|', '\t'] 
    """
    import csv
    from detect_delimiter import detect
    with open(file, newline='') as f: 
        filecsv = csv.reader(f)
        first_line = list(filecsv)[0][0]
    return detect(first_line)

def toDataframe(file):
    if file.filename.rsplit('.', 1)[1].lower() == 'csv':
        return pd.read_csv(file, sep=f'{detectdelimiter(file)}')
    if file.filename.rsplit('.', 1)[1].lower() == 'xls':
        return pd.read_excel(file)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            # return render_template('home.html')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print('file name is', filename)
            print(file)
            # secure_filename is needed whenever we want to save a file in our directory
            # file.save(secure_filename(file.filename))
            df = pd.read_csv(file, sep=';')
            session['HLA_data'] = df.to_json()
            df_json = session.get('HLA_data')
            df = pd.read_json(df_json, dtype=False)
            print(df)
            return render_template('home.html', posts=f'Dataset {file.filename} successfully oploaded', dataframe=df.to_html())
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)