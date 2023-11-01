import requests
from fuzzywuzzy import process

BLAZEGRAPH_URL = 'https://polifonia.disi.unibo.it/fonn/sparql'


# BLAZEGRAPH_URL = 'https://localhost:9999/bigdata/sparql'


def get_pattern_search_query(pattern):
    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm:<http://w3id.org/polifonia/ontology/music-meta/>
                        PREFIX ptn:<http://w3id.org/polifonia/resource/pattern/>
                        SELECT distinct ?tune_name ?tuneType ?key ?signature
                        WHERE
                        {
	                        ?obs jams:ofPattern ptn:""" + pattern + """.
                            ?annotation jams:includesObservation ?obs.
                            ?annotation jams:isJAMSAnnotationOf ?musicalComposition.
                            OPTIONAL {?musicalComposition mm:title ?tune_name}
                            OPTIONAL {?musicalComposition jams:tuneType ?tuneType}
                            OPTIONAL {?musicalComposition jams:key ?key}
                            OPTIONAL {?musicalComposition jams:timeSignature ?signature}
                        }"""
    return sparql_query


def get_most_common_patterns_for_a_tune(tune):
    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm: <http://w3id.org/polifonia/ontology/music-meta/>
                        SELECT ?tune_name ?pattern (count(?pattern) as ?patternFreq)
                        {
                            ?tune_file mm:title ?tune_name.
                            FILTER (?tune_name = \"""" + tune + """\").
                            ?xx jams:isJAMSAnnotationOf ?tune_file.
                            ?xx jams:includesObservation ?observation .
                            ?observation jams:ofPattern ?pattern .
                        } group by ?tune_name ?pattern
                        order by DESC (?patternFreq )"""
    return sparql_query


# Fuzzy Search
def get_tune_given_name(query_name, all_names):
    matched_tuples = process.extractBests(query_name, all_names, score_cutoff=60, limit=100)
    print(matched_tuples)
    matched_names = [x[0] for x in matched_tuples]
    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm: <http://w3id.org/polifonia/ontology/music-meta/>
                        SELECT DISTINCT ?tune_name ?tuneType ?key ?signature
                        {
                            ?tune mm:title ?tune_name.
                            OPTIONAL {?tune jams:tuneType ?tuneType}
                            OPTIONAL {?tune jams:key ?key}
                            OPTIONAL {?tune jams:timeSignature ?signature}
                            FILTER (?tune_name = \""""
    sparql_query += "\" || ?tune_name = \"".join(matched_names)
    sparql_query += "\").}"
    return sparql_query


# Old version
def get_tune_given_name2(name):
    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm: <http://w3id.org/polifonia/ontology/music-meta/>
                        SELECT DISTINCT ?tune_name ?tuneType ?key ?signature
                        {
                            ?tune mm:title ?tune_name.
                            ?tune jams:tuneType ?tuneType.
                            ?tune jams:key ?key.
                            ?tune jams:timeSignature ?signature .
                            FILTER (CONTAINS( ?tune_name, \"""" + name + """\" )).
                        } LIMIT 10
                     """
    return sparql_query


# Advanced search
def advanced_search(query_params, all_names):
    if query_params['composition']:
        matched_tuples = process.extractBests(query_params['composition'], all_names, score_cutoff=60, limit=100)
        # print(matched_tuples)
        matched_names = [x[0] for x in matched_tuples]
        title_query = True
    else:
        title_query = False

    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm:<http://w3id.org/polifonia/ontology/music-meta/>
                        PREFIX ptn:<http://w3id.org/polifonia/resource/pattern/>
                        SELECT distinct ?tune_name ?tuneType ?key ?signature
                        WHERE
                        {
	                        ?obs jams:ofPattern ptn:""" + query_params['pattern'] + """.
                            ?annotation jams:includesObservation ?obs.
                            ?annotation jams:isJAMSAnnotationOf ?musicalComposition.
                            ?musicalComposition mm:title ?tune_name.
                            OPTIONAL {?tune jams:tuneType ?tuneType}
                            OPTIONAL {?tune jams:key ?key}
                            OPTIONAL {?tune jams:timeSignature ?signature}"""
    if title_query:
        sparql_query += """FILTER (?tune_name = \""""
        sparql_query += "\" || ?tune_name = \"".join(matched_names)
        sparql_query += "\").}"
    else:
        sparql_query += "}"
    return sparql_query


def get_all_tune_names():
    sparql_query = """PREFIX mm: <http://w3id.org/polifonia/ontology/music-meta/>
                        SELECT DISTINCT ?tune_name
                        {
                            ?tune_file mm:title ?tune_name.
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
