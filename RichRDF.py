from flask import Flask, render_template, request, after_this_request, make_response, send_from_directory, send_file
import werkzeug
import os
import itertools
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import numpy
import hashlib
import nltk
from nltk.corpus import wordnet
import requests
from bs4 import BeautifulSoup
import json
import re
import os
import shutil
import time
import addContext
import entityEtra
import relations
import semanticSimi
import relatedImages
import pureImages

app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

context = ''
relationToUse = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
mainSim, hashOut = 0, 0
subToUse, objToUse = '', ''


def createTemp(filename):
    with open(filename) as reader:
        with open('temp.nt', 'w+') as writer:
            for line in reader:
                writer.write(line)

@app.route('/database', methods=['GET', 'POST'])
def upload_file():
    global context
    if request.method == 'POST':
        contexT = request.form['context']
        context = contexT
        f = request.files['file']
        f.save(werkzeug.secure_filename(f.filename))
        # Finaldata = readFile(f.filename)
        Finaldata = addContext.readFile(f.filename, contexT)
        createTemp(f.filename)
        filename = Finaldata

        @after_this_request
        def remove_file(response):
            try:
                os.remove(f.filename)
                # readDate.readerIn.close()
            except Exception as error:
                app.logger.error("Error removing or closing downloaded file handle", error)
            return response

        def download(response):
            response = make_response(Finaldata)
            response.headers["Content-Disposition"] = "attachment; filename=result.txt"
            render_template('upload.html', filename=filename)
            return response

        return render_template('upload.html', filename=filename)




@app.route('/extractEntity')
def extractEntity():
    filename = entityEtra.readFile('temp.nt', context)
    return render_template('upload.html', filename=filename)


@app.route('/relationships')
def relationships():
    filename = relations.readFile('temp.nt', context)
    return render_template('upload.html', filename=filename)


@app.route('/semanticSimilarity')
def semanticSimilarity():
    filename = semanticSimi.readFile('temp.nt', context)
    return render_template('upload.html', filename=filename)


@app.route('/relImages')
def relImages():
    filename = relatedImages.readFile('temp.nt', context)
    return render_template('upload.html', filename=filename)



@app.route('/pImages')
def pImages():
    filename = pureImages.readFile('temp.nt', context)
    return render_template('upload.html', filename=filename)


@app.route('/allfeatures')
def allfeatures():
    filename = pureImages.readFile('temp.nt', context)
    return render_template('upload.html', filename=filename)



@app.route('/database_download', methods=['GET', 'POST'])
def download_file():
    if request.method == 'POST':
        text = request.form['text']
        text = text.replace("&lt;", '<').replace('&gt;', '>').replace("</br>", "\n")
        response = make_response(text)
        response.headers["Content-Disposition"] = "attachment; filename=result.txt"
        return response
        render_template('upload.html')
    else:
        render_template('upload.html')

    render_template('upload.html')


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/aboutUs')
def aboutUs():
    return render_template('aboutUs.html')


def readFileQuery():
    data = ''
    print("bring data to Queries page from:", os.getcwd())
    os.system('cp output.nq files/input.nq')
    with open('files/input.nq') as reader:
        data = reader.read()
        data = data.split('\n')
    return data

def readFileResult():
    data = ''
    with open('/Users/mohamedghribi/Desktop/richRDF/files/output.nq') as reader:
        data = reader.read()
        data = data.split('\n')
    return data


@app.route('/queryOutput', methods=['GET', 'POST'])
def queryOutput():
    data = readFileQuery()
    return render_template('queryOutput.html', data=data)


@app.route('/queryData', methods=['GET', 'POST'])
def queryData():
    if request.method == 'POST':
        try:
            os.chdir('/Users/mohamedghribi/Desktop/richRDF/files/')
            query = request.form['text']
            writer = open('query.sparql', 'w+')
            writer.write(query)
            writer.flush()
            writer.close()
            if 'outFinal' in os.listdir('/Users/mohamedghribi/Desktop/richRDF/files'):
                shutil.rmtree('/Users/mohamedghribi/Desktop/richRDF/files/outFinal')
            os.system('./../apache-jena-3.8.0/bin/tdbloader2 --loc /Users/mohamedghribi/Desktop/richRDF/files/outFinal /Users/mohamedghribi/Desktop/richRDF/files/input.nq')
            os.system('./../apache-jena-3.8.0/bin/tdbquery --loc /Users/mohamedghribi/Desktop/richRDf/files/outFinal --query /Users/mohamedghribi/Desktop/richRDF/files/query.sparql > /Users/mohamedghribi/Desktop/richRDF/files/output.nq')
            print("Tst")
            data = readFileResult()
        except Exception as e:
            print(e)
        if not data:
            data = 'You entered an empty or a wrong query! Keep trying...'

    return render_template('queryOutput.html', data=data)


@app.route('/downloadData', methods=['GET', 'POST'])
def downloadData():
    if request.method == 'POST':
        data1 = ''
        with open('/Users/mohamedghribi/Desktop/richRDF/files/output.nq') as reader:
            data1 = reader.read().replace('&lt', '<').replace('&gt', '>').replace('<br>', '\n')
        print("Donloaded fileeeeeeeee is", data1[:20])
        print(os.getcwd())
        return send_file('/Users/mohamedghribi/Desktop/richRDF/files/output.nq', as_attachment=True)
        render_template('queryOutput.html')
    else:
        render_template('queryOutput.html')
    render_template('queryOutput.html')


if __name__ == '__main__':
    app.run(debug="True")
