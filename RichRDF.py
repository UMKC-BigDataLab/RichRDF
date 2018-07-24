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

context = "https://catalog.data.gov/dataset=?food$food_ABBREV"
relationToUse = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
mainSim, hashOut = 0, 0
subToUse, objToUse = '', ''


def get_continuous_chunks(text):
    chunked = ne_chunk(pos_tag(word_tokenize(text)))
    prev = None
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
        if type(i) == Tree:
            current_chunk.append(" ".join([token for token, pos in i.leaves()]))
        elif current_chunk:
            named_entity = " ".join(current_chunk)
            if named_entity not in continuous_chunk:
                continuous_chunk.append(named_entity)
                current_chunk = []
        else:
            continue
    return continuous_chunk


def calSimilarity(subject, object, writer, sub1, sub2):
    global mainSim
    global hashOut
    try:
        rel = requests.get('http://api.conceptnet.io/query?node=/c/en/{}&other=/c/en/{}'.format(subject, object)).json()
        relation = rel['edges'][0]['@id'].split('/')[4]
        print("suuub1 is: ", sub1)
        writer.write('<{}> <{}{}> <{}> <{}> .'.format(sub1, relationToUse, relation, sub2, context))
        writer.write("\n")
    except Exception as e:
        pass
    else:
        # print("NO error")
        try:
            Similarity = requests.get(
                'http://api.conceptnet.io/related/c/en/{}?filter=/c/en/{}'.format(subject, object)).json()
            Similarity = Similarity['related'][0]['weight']
            mainSim = Similarity
            to_hash = '{} {}'.format(subject, object)
            hashed_output = abs(hash(to_hash)) % (10 ** 8)
            hashOut = hashed_output
            writer.write('<{}> <{}{}> _:{} <{}> .'.format(sub1, relationToUse, relation, hashed_output, context))
            writer.write('\n')
            writer.write('<{}> <{}{}> _:{} <{}> .'.format(sub2, relationToUse, relation, hashed_output, context))
            writer.write('\n')
            writer.write('_:{} <{}Concept_Similarity> "{}" <{}> .'.format(hashed_output, relationToUse, str(Similarity),
                                                                          context))
            writer.write('\n')
            # writer.write(get_continuous_chunks(my_sent))
        except Exception as e:
            pass
        else:
            # print("YAAAAAAAAAAAAAAAAAAs")
            pass


def imageURLS(word, hashed_output, writer, relationToUse):
    print("Inside the first functionnnns")
    try:
        myWord = wordnet.synsets(word)[0]
        concept_offset = myWord.offset()
        generated_id = len(str(concept_offset))
    except Exception as e:
        print(e)
    else:
        if generated_id != 8:
            image_URL = "http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n0{}".format(concept_offset)
            writer.write('_:{} <{}IURLs_{}> <{}> <{}> .'.format(hashed_output, relationToUse, word, image_URL, context))
            writer.write('\n')
        else:
            image_URL = "http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n{}".format(concept_offset)
            writer.write('_:{} <{}IURLs_{}> <{}> <{}> .'.format(hashed_output, relationToUse, word, image_URL, context))
            writer.write('\n')


def specificImageURLs(word, hashed_output, writer, relationToUse):
    print("Inside the secooond functionnnns")
    try:
        syns = wordnet.synsets('{}'.format(word))[0]
        syn_offset = syns.offset()
        page = requests.get('http://www.image-net.org/search?q={}'.format(word))
        soup = BeautifulSoup(page.content, 'html.parser')
    except Exception as e:
        print(e)
    else:
        if len(str(syn_offset)) == 7:
            try:
                for link in soup.find_all('a', {'href': 'synset?wnid=n0{}'.format(syn_offset)}):
                    writer.write(
                        '_:{} <{}{}_Images> "http://www.image-net.org/{}" <{}> .'.format(hashed_output, relationToUse,
                                                                                         word, link.img['src'],
                                                                                         context))
                    writer.write('\n')
            except Exception as e:
                pass
        else:
            try:
                for link in soup.find_all('a', {'href': 'synset?wnid=n{}'.format(syn_offset)}):
                    writer.write(
                        '_:{} <{}{}_Images> "http://www.image-net.org/{}" <{}> .'.format(hashed_output, relationToUse,
                                                                                         word, link.img['src'],
                                                                                         context))
                    writer.write('\n')
            except Exception as e:
                pass


def readFile(fileName):
    start_time = time.time()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)

    try:
        reader = open(fileName, "r")
        writer = open('output.nq', 'w+')
    except Exception as e:
        print(e)
    else:
        parity = itertools.cycle([True, False])
        for line in reader:
            if line.startswith("_:"):
                writer.write('{} <{}> .'.format(line.strip().rstrip(' .'), context))
                writer.write('\n')
                continue
            if line.isspace():
                continue
            if next(parity):
                line1 = line
                writer.write('{} <{}> .'.format(line1.strip().rstrip(' .'), context))
                writer.write('\n')

                line1 = re.findall('<([^>]*)>', line)
                if len(line1) == 3:
                    sub_line1, rel_line1, obj_line1 = line1[0], line1[1], line1[2]
                elif len(line1) == 2:
                    sub_line1, rel_line1 = line1[0], line1[1]
                    obj_line1 = re.findall('"([^"]*)"', line)[0]
                else:
                    pass

                finalSub = ''
                sub1 = sub_line1
                sub_line1 = sub_line1.split('/')[-1].upper()
                try:
                    extractedSub = get_continuous_chunks(sub_line1.upper())
                    print("sub ext", extractedSub)
                    extractedSubLength = len(extractedSub)
                except Exception as e:
                    print(e)
                else:
                    # print("NLTK works perfectly")
                    if extractedSubLength == 0:
                        pass
                    elif extractedSubLength == 1:
                        finalSub = extractedSub[0]
                    else:
                        writer.write(
                            '<{}> <{}isA> <{}> <{}> .'.format(sub1, relationToUse,
                                                              '/'.join(sub1.split('/')[:-1]) + '/' + ','.join(
                                                                  extractedSub),
                                                              context))
                        writer.write('\n')
                    # writer.write('{}'.format(extractedSub))



            else:
                line2 = line
                writer.write('{} <{}> .'.format(line2.strip().rstrip(' .'), context))
                writer.write('\n')

                line2 = re.findall('<([^>]*)>', line)
                if len(line2) == 3:
                    sub_line2, rel_line2, obj_line2 = line2[0], line2[1], line2[2]
                elif len(line2) == 2:
                    sub_line2, rel_line2 = line2[0], line2[1]
                    obj_line2 = re.findall('"([^"]*)"', line)[0]
                else:
                    pass

                # writer.write("Both line: {}{}".format(line1, line2))

                finalObj = ''
                sub2 = sub_line2
                sub_line2 = sub_line2.split('/')[-1].upper()
                try:
                    extractedObj = get_continuous_chunks(sub_line2.upper())
                    print("obj ext", extractedObj)
                    extractedObjLength = len(extractedObj)
                except Exception as e:
                    print(e)
                else:
                    # print("NLTK works perfectly")
                    if extractedObjLength == 0:
                        pass
                    elif extractedObjLength == 1:
                        finalObj = extractedObj[0]
                    else:
                        writer.write('<{}> <{}isA> <{}> <{}> .'.format(sub2, relationToUse,
                                                                       '/'.join(sub2.split('/')[:-1]) + '/' + ','.join(
                                                                           extractedObj), context))
                        writer.write('\n')

                sub_line1, sub_line2 = sub_line1.lower(), sub_line2.lower()

                # Calculating the similarity between two normal words that have not been changed
                finalSub, finalObj = finalSub.lower(), finalObj.lower()
                extractedSub = [i.lower() for i in extractedSub]
                extractedObj = [i.lower() for i in extractedObj]

                if extractedSubLength == 0:
                    if extractedObjLength == 0:
                        calSimilarity(sub_line1, sub_line2, writer, sub1, sub2)
                        subToUse, objToUse = sub_line1, sub_line2
                    elif extractedObjLength == 1:
                        calSimilarity(sub_line1, finalObj, writer, sub1, sub2)
                        subToUse, objToUse = sub_line1, finalObj
                    else:
                        for everyObj in extractedObj:
                            calSimilarity(sub_line1, everyObj, writer, sub1, sub2)
                            subToUse, objToUse = sub_line1, everyObj
                            if mainSim != 0:
                                break

                elif extractedSubLength == 1:
                    if extractedObjLength == 0:
                        calSimilarity(finalSub, sub_line2, writer, sub1, sub2)
                        subToUse, objToUse = finalSub, sub_line2
                    elif extractedObjLength == 1:
                        calSimilarity(finalSub, finalObj, writer, sub1, sub2)
                        subToUse, objToUse = finalSub, finalObj
                    else:
                        for everyObj1 in extractedObj:
                            calSimilarity(finalSub, everyObj1, writer, sub1, sub2)
                            subToUse, objToUse = finalSub, everyObj1
                            if mainSim != 0:
                                break

                else:
                    if extractedObjLength == 0:
                        for everySub in extractedSub:
                            calSimilarity(everySub, sub_line2, writer, sub1, sub2)
                            subToUse, objToUse = everySub, sub_line2
                            if mainSim != 0:
                                break
                    elif extractedObjLength == 1:
                        for everySub1 in extractedSub:
                            calSimilarity(everySub1, finalObj, writer, sub1, sub2)
                            subToUse, objToUse = everySub1, finalObj
                            if mainSim != 0:
                                break
                    else:
                        for everySub2 in extractedSub:
                            for everyObj2 in extractedObj:
                                calSimilarity(everySub2, everyObj2, writer, sub1, sub2)
                                subToUse, objToUse = everySub2, everyObj2
                                if mainSim != 0:
                                    break

                print("sim is: ", mainSim)
                if mainSim != 0:
                    print("Insssside the first if")

                    imageURLS(subToUse, hashOut, writer, relationToUse)
                    imageURLS(objToUse, hashOut, writer, relationToUse)
                    print("After first 2 Functions")
                    # specificImageURLs(subToUse, hashOut, writer, relationToUse)
                    # specificImageURLs(objToUse, hashOut, writer, relationToUse)
                    # print("DONNNNNNNNe ALL")
                    # continue

        print("timmmmmmme is :", "--- %s seconds ---" % (time.time() - start_time))
        writer.flush()
        writer.close()

        readIn = open('output.nq')
        data = readIn.read().replace('<', '&lt;').replace('>', '&gt;').replace('\n', '</br>')
        readIn.close()
        return data

    # finally:
    #     writer.flush()
    #     writer.close()

def createTemp(filename):
    with open(filename) as reader:
        with open('temp.nt', 'w+') as writer:
            for line in reader:
                writer.write(line)

@app.route('/database', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(werkzeug.secure_filename(f.filename))
        # Finaldata = readFile(f.filename)
        Finaldata = addContext.readFile(f.filename)
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
    filename = entityEtra.readFile('temp.nt')
    return render_template('upload.html', filename=filename)


@app.route('/relationships')
def relationships():
    filename = relations.readFile('temp.nt')
    return render_template('upload.html', filename=filename)


@app.route('/semanticSimilarity')
def semanticSimilarity():
    filename = semanticSimi.readFile('temp.nt')
    return render_template('upload.html', filename=filename)


@app.route('/relImages')
def relImages():
    filename = relatedImages.readFile('temp.nt')
    return render_template('upload.html', filename=filename)



@app.route('/pImages')
def pImages():
    filename = pureImages.readFile('temp.nt')
    return render_template('upload.html', filename=filename)


@app.route('/allfeatures')
def allfeatures():
    filename = relatedImages.readFile('temp.nt')
    return render_template('upload.html', filename=filename)


















@app.route('/database_download', methods=['GET', 'POST'])
def download_file():
    if request.method == 'POST':
        print("Gooooot hereeeee")
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
    with open('output.nq') as reader:
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
            os.chdir('/home/gharibi/Desktop/forPaper/apache-jena-3.6.0/bin')
            query = request.form['text']
            writer = open('query.sparql', 'w+')
            writer.write(query)
            writer.flush()
            writer.close()
            if 'outFinal' in os.listdir('/home/gharibi/Desktop/'):
                shutil.rmtree('/home/gharibi/Desktop/outFinal')
            os.system('./tdbloader2 --loc ~/Desktop/outFinal ~/Desktop/forPaper/output.nq')
            os.system(
                './tdbquery --loc ~/Desktop/outFinal --query ~/Desktop/forPaper/apache-jena-3.6.0/bin/query.sparql > output.nq')
            data = readFileQuery()
        except Exception as e:
            print(e)
        if not data:
            data = 'You entered an empty or a wrong query! Keep trying...'

    return render_template('queryOutput.html', data=data)


@app.route('/downloadData', methods=['GET', 'POST'])
def downloadData():
    if request.method == 'POST':
        data1 = ''
        with open('output.nq') as reader:
            data1 = reader.read().replace('&lt', '<').replace('&gt', '>').replace('<br>', '\n')
        return send_file('/home/gharibi/Desktop/forPaper/apache-jena-3.6.0/bin/output.nq', as_attachment=True)
        render_template('queryOutput.html')
    else:
        render_template('queryOutput.html')
    render_template('queryOutput.html')


if __name__ == '__main__':
    app.run(debug="True")
