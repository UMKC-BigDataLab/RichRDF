# RichRDF
</br>
RichRDF is a web-based tool that works on enriching the existing Food, Energy, and Water (FEW) datasets with semantically related facts and images.
</br></br>

[A video to show how RichRDF works](https://youtu.be/vyHgh4LgKCo/)

# References
1. Mohamed Gharibi, Praveen Rao, Nouf Alrasheeh. "RichRDF: A Tool for Enriching Food, Energy, and Water Datasets with Semantically Related Facts and Images." To appear in the [17th International Semantic Web Conference (ISWC 2018)](http://iswc2018.semanticweb.org), 4 pages, Monterrey, CA, 2018. (demo)

2. Praveen Rao, Anas Katib, Daniel E. Barron Lopez. "A Knowledge Ecosystem for the Food, Energy, and Water System." In the KDD 2016 Workshop on Data Science for Food, Energy and Water (DSFEW), 4 pages, San Francisco, CA, 2016. (position paper)



</br>

**Simple input:**</br>
`<http://catalog.data.gov/dataset=?food/ft,VITD,cheese,&ft> <http://www.w3.org/1999/02/22-rdf-syntax-ns#water_(g)> "14.03" .
<http://catalog.data.gov/dataset=?food/ft,butter,mlcrm&salt> <http://www.w3.org/1999/02/22-rdf-syntax-ns#water_(g)> "12.23" .`


**Output:**</br>
`<http://catalog.data.gov/dataset=?food/ft,VITD,cheese,&ft> <http://www.w3.org/1999/02/22-rdf-syntax-ns#water_(g)> "14.03" <https://catalog.data.gov/dataset=?food$food_ABBREV> .
<http://catalog.data.gov/dataset=?food/ft,VITD,cheese,&ft> <http://www.w3.org/1999/02/22-rdf-syntax-ns#isA> <http://catalog.data.gov/dataset=?food/VITD,CHEESE> <https://catalog.data.gov/dataset=?food$food_ABBREV> .
<http://catalog.data.gov/dataset=?food/ft,butter,mlcrm&salt> <http://www.w3.org/1999/02/22-rdf-syntax-ns#water_(g)> "12.23" <https://catalog.data.gov/dataset=?food$food_ABBREV> .
<http://catalog.data.gov/dataset=?food/ft,butter,mlcrm&salt> <http://www.w3.org/1999/02/22-rdf-syntax-ns#isA> <http://catalog.data.gov/dataset=?food/BUTTER,MLCRM> <https://catalog.data.gov/dataset=?food$food_ABBREV> .
<http://catalog.data.gov/dataset=?food/ft,VITD,cheese,&ft> <http://www.w3.org/1999/02/22-rdf-syntax-ns#RelatedTo> <http://catalog.data.gov/dataset=?food/ft,butter,mlcrm&salt> <https://catalog.data.gov/dataset=?food$food_ABBREV> .
<http://catalog.data.gov/dataset=?food/ft,VITD,cheese,&ft> <http://www.w3.org/1999/02/22-rdf-syntax-ns#RelatedTo> _:99036406 <https://catalog.data.gov/dataset=?food$food_ABBREV> .
<http://catalog.data.gov/dataset=?food/ft,butter,mlcrm&salt> <http://www.w3.org/1999/02/22-rdf-syntax-ns#RelatedTo> _:99036406 <https://catalog.data.gov/dataset=?food$food_ABBREV> .
_:99036406 <http://www.w3.org/1999/02/22-rdf-syntax-ns#Semantic_Similarity> "0.42" <https://catalog.data.gov/dataset=?food$food_ABBREV> .
_:99036406 <http://www.w3.org/1999/02/22-rdf-syntax-ns#IURLs_cheese> <http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n07850329> <https://catalog.data.gov/dataset=?food$food_ABBREV> .
_:99036406 <http://www.w3.org/1999/02/22-rdf-syntax-ns#IURLs_butter> <http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=n07848338> <https://catalog.data.gov/dataset=?food$food_ABBREV> .`


**References:** </br>
[NLTK](https://www.nltk.org/)</br>
[ConceptNet](http://conceptnet.io/)</br>
[WordNet](https://wordnet.princeton.edu/)</br>
[DBPedia](https://wiki.dbpedia.org/)</br>
[ImageNet](http://www.image-net.org/)</br>
[Flask](http://flask.pocoo.org/)</br>



