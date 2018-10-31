import os
import shutil
import time
import itertools
import re
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.corpus import wordnet
from nltk.tree import Tree
import requests
import entityEtra


dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

relationToUse = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
mainSim, hashOut = 0, 0
subToUse, objToUse = '', ''


def calSimilarity(subject, object, writer, sub1, sub2, context):
    global mainSim
    global hashOut
    try:
        rel = requests.get('http://api.conceptnet.io/query?node=/c/en/{}&other=/c/en/{}'.format(subject, object)).json()
        relation = rel['edges'][0]['@id'].split('/')[4]
        s = "/".join(sub1.split('/')[:-1])
        o = "/".join(sub2.split('/')[:-1])
        writer.write('<{}> <{}{}> <{}> <{}> .'.format(s + '/' + subject.capitalize(), relationToUse, relation,
                                                      o + '/' + object.capitalize(), context))
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
            writer.write('_:{} <{}Concept_Similarity> "{}" <{}> .'.format(hashed_output, relationToUse, str(Similarity),context))
            writer.write('\n')
        except Exception as e:
            pass
        else:
            # print("YAAAAAAAAAAAAAAAAAAs")
            pass

def imageURLS(word, hashed_output, writer, relationToUse, context):
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




def readFile(fileName, context):
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
            line = line.replace('%20', ',').replace('%2C', ',')
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
                    extractedSub = entityEtra.get_continuous_chunks(sub_line1.upper())
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
                    extractedObj = entityEtra.get_continuous_chunks(sub_line2.upper())
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
                        calSimilarity(sub_line1, sub_line2, writer, sub1, sub2, context)
                        subToUse, objToUse = sub_line1, sub_line2
                    elif extractedObjLength == 1:
                        calSimilarity(sub_line1, finalObj, writer, sub1, sub2, context)
                        subToUse, objToUse = sub_line1, finalObj
                    else:
                        for everyObj in extractedObj:
                            calSimilarity(sub_line1, everyObj, writer, sub1, sub2, context)
                            subToUse, objToUse = sub_line1, everyObj
                            if mainSim != 0:
                                break

                elif extractedSubLength == 1:
                    if extractedObjLength == 0:
                        calSimilarity(finalSub, sub_line2, writer, sub1, sub2, context)
                        subToUse, objToUse = finalSub, sub_line2
                    elif extractedObjLength == 1:
                        calSimilarity(finalSub, finalObj, writer, sub1, sub2, context)
                        subToUse, objToUse = finalSub, finalObj
                    else:
                        for everyObj1 in extractedObj:
                            calSimilarity(finalSub, everyObj1, writer, sub1, sub2, context)
                            subToUse, objToUse = finalSub, everyObj1
                            if mainSim != 0:
                                break

                else:
                    if extractedObjLength == 0:
                        for everySub in extractedSub:
                            calSimilarity(everySub, sub_line2, writer, sub1, sub2, context)
                            subToUse, objToUse = everySub, sub_line2
                            if mainSim != 0:
                                break
                    elif extractedObjLength == 1:
                        for everySub1 in extractedSub:
                            calSimilarity(everySub1, finalObj, writer, sub1, sub2, context)
                            subToUse, objToUse = everySub1, finalObj
                            if mainSim != 0:
                                break
                    else:
                        for everySub2 in extractedSub:
                            for everyObj2 in extractedObj:
                                calSimilarity(everySub2, everyObj2, writer, sub1, sub2, context)
                                subToUse, objToUse = everySub2, everyObj2
                                if mainSim != 0:
                                    break

                print("sim is: ", mainSim)
                if mainSim != 0:
                    print("Insssside the first if")

                    imageURLS(subToUse, hashOut, writer, relationToUse, context)
                    imageURLS(objToUse, hashOut, writer, relationToUse, context)


        writer.flush()
        writer.close()

        readIn = open('output.nq')
        data = readIn.read().replace('<', '&lt;').replace('>', '&gt;').replace('\n', '</br>')
        readIn.close()
        return data