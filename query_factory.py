import requests
from flask import jsonify

BLAZEGRAPH_URL = 'https://polifonia.disi.unibo.it/fonn/sparql'


def get_pattern_search_query(pattern):
    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
PREFIX mc: <http://w3id.org/polifonia/ontology/musical-composition/>
SELECT distinct ?tuneName ?tuneType
WHERE
{
VALUES ?Pattern
{<http://w3id.org/polifonia/resource/pattern/""" + pattern + """>}
?observation jams:ofPattern ?pattern.
?tuneFile jams:includesObservation ?observation.
?tuneFile jams:isJAMSAnnotationOf ?musicalComposition.
?musicalComposition mc:title ?tuneName.
} limit 100"""
    return sparql_query


def get_most_common_patterns_for_a_tune(tune):
    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
PREFIX mc: <http://w3id.org/polifonia/ontology/musical-composition/>
SELECT ?tune_name ?pattern (count(?pattern) as ?patternFreq)
{
?tune_file mc:title ?tune_name.
FILTER (?tune_name = \"""" + tune + """\").
?xx jams:isJAMSAnnotationOf ?tune_file.
?xx jams:includesObservation ?observation .
?observation jams:ofPattern ?pattern .
} group by ?tune_name ?pattern
order by DESC (?patternFreq )"""
    return sparql_query


def get_tune_given_name(name):
    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
PREFIX mc: <http://w3id.org/polifonia/ontology/musical-composition/>
SELECT ?tune_name
{
?tune_file mc:title ?tune_name.
FILTER (?tune_name = \"""" + name + """\").
}
"""
    return sparql_query


if __name__ == "__main__":
    # Generate the SPARQL query
    sparql_query = get_tune_given_name("Yankee Doodle")

    # Execute the SPARQL query
    response = requests.post(
        BLAZEGRAPH_URL,
        data={
            'query': sparql_query,
            'format': 'json'
        }
    )

    # Return the JSON data
    data = response.json()
    print(data)
