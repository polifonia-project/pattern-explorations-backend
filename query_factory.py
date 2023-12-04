import requests

NUM_NODES = 5

def get_pattern_search_query(pattern):
    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm:<http://w3id.org/polifonia/ontology/music-meta/>
                        PREFIX ptn:<http://w3id.org/polifonia/resource/pattern/>
                        SELECT distinct ?tune_name ?tuneType ?key ?signature ?id
                        WHERE
                        {
	                        ?obs jams:ofPattern ptn:""" + pattern + """.
                            ?annotation jams:includesObservation ?obs.
                            ?annotation jams:isJAMSAnnotationOf ?musicalComposition.
                            ?musicalComposition jams:tuneId ?id.
                            OPTIONAL {?musicalComposition mm:title ?tune_name}
                            OPTIONAL {?musicalComposition jams:tuneType ?tuneType}
                            OPTIONAL {?musicalComposition jams:key ?key}
                            OPTIONAL {?musicalComposition jams:timeSignature ?signature}
                        } ORDER BY ?tune_name"""
    return sparql_query


def get_most_common_patterns_for_a_tune(id, excludeTrivialPatterns):
    sparql_query =   """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm: <http://w3id.org/polifonia/ontology/music-meta/>
                        SELECT ?pattern (count(?pattern) as ?patternFreq)
                        {
                            ?tune jams:tuneId \"""" + id + """\".
                            ?xx jams:isJAMSAnnotationOf ?tune.
                            ?xx jams:includesObservation ?observation .
                        """
    if excludeTrivialPatterns == "true":
        sparql_query += """ ?observation jams:hasPatternComplexity ?comp .
                            FILTER (?comp > "0.4"^^xsd:float) .
                        """
    sparql_query +=     """?observation jams:ofPattern ?pattern .
                        } group by ?pattern
                        order by DESC (?patternFreq) LIMIT 10"""
    return sparql_query


def get_patterns_in_common_between_two_tunes(id, prev):
    sparql_query =   """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm: <http://w3id.org/polifonia/ontology/music-meta/>
                        SELECT ?pattern
                        {
                            ?tune1 jams:tuneId \"""" + id + """\".
                            ?xx1 jams:isJAMSAnnotationOf ?tune1.
                            ?xx1 jams:includesObservation ?observation1 .
                            ?observation1 jams:ofPattern ?pattern .
                            ?tune2 jams:tuneId \"""" + prev + """\".
                            ?xx2 jams:isJAMSAnnotationOf ?tune2.
                            ?xx2 jams:includesObservation ?observation2 .
                            ?observation2 jams:ofPattern ?pattern .
                        } group by ?pattern
                        order by DESC (count(?pattern)) ?pattern LIMIT 10"""
    return sparql_query


def get_tune_given_name(matched_ids):
    sparql_query =   """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm: <http://w3id.org/polifonia/ontology/music-meta/>
                        SELECT DISTINCT ?tune_name ?tuneType ?key ?signature ?id
                        {
                            ?tune mm:title ?tune_name.
                            ?tune jams:tuneId ?id.
                            OPTIONAL {?tune jams:tuneType ?tuneType}
                            OPTIONAL {?tune jams:key ?key}
                            OPTIONAL {?tune jams:timeSignature ?signature}
                            VALUES (?title ?match_strength ?id) { ( \""""
    sparql_query += "\" ) ( \"".join(['\" \"'.join(map(str,tup)) for tup in matched_ids])
    sparql_query += "\" ) }\n} ORDER BY DESC(xsd:integer(?match_strength)) ?title"
    return sparql_query


# Advanced search
def advanced_search(query_params, matched_ids):
    sparql_query = """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm:<http://w3id.org/polifonia/ontology/music-meta/>
                        PREFIX ptn:<http://w3id.org/polifonia/resource/pattern/>
                        PREFIX ttype:<http://w3id.org/polifonia/resource/tunetype>
                        PREFIX key:<http://w3id.org/polifonia/resource/key>
                        PREFIX tsig:<http://w3id.org/polifonia/resource/timeSignature>
                        PREFIX prov:<http://www.w3.org/ns/prov#>
                        SELECT distinct ?tune_name ?tuneType ?key ?signature ?id
                        WHERE
                        {
                        """

    if query_params['pattern']:
        sparql_query +=     "?obs jams:ofPattern ptn:" + query_params['pattern'] + """.
                            ?annotation jams:includesObservation ?obs.
                            ?annotation jams:isJAMSAnnotationOf ?tune.
                            """

    if query_params['corpus']:
        sparql_query +=     """?file prov:wasDerivedFrom ?corpus .
                            FILTER (CONTAINS(?corpus, \""""+ query_params['corpus'] + """\")) .
                            ?tune prov:wasDerivedFrom ?file.
                            """

    if query_params['tuneType']:
        sparql_query +=     "?tune jams:tuneType ttype:" + query_params['tuneType'] + " .\n"
    else:
        sparql_query +=     "OPTIONAL {?tune jams:tuneType ?tuneType}\n"

    if query_params['key']:
        sparql_query +=     "?tune jams:key key:" + query_params['key'] + " .\n"
    else:
        sparql_query +=     "OPTIONAL {?tune jams:key ?key}\n"

    if query_params['timeSignature']:
        sparql_query += "   ?tune jams:timeSignature tsig:" + query_params['timeSignature'] + " .\n"
    else:
        sparql_query += "   OPTIONAL {?tune jams:timeSignature ?signature}\n"

    if query_params['title']:
        sparql_query +=  """?tune mm:title ?tune_name .
                            VALUES(?title ?match_strength ?id) {( \""""
        sparql_query += "\" ) ( \"".join(['\" \"'.join(map(str,tup)) for tup in matched_ids])
        sparql_query += "\" ) }\n"
    else:
        sparql_query += "   OPTIONAL {?tune mm:title ?tune_name}\n"

    sparql_query +=     "?tune jams:tuneId ?id.}"
    if query_params['title']:
        sparql_query += " ORDER BY DESC(xsd:integer(?match_strength)) ?title"
    else:
        sparql_query += " ORDER BY ?tune_name"
    return sparql_query


def get_all_tune_names():
    sparql_query =   """PREFIX mm: <http://w3id.org/polifonia/ontology/music-meta/>
                        PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        SELECT DISTINCT ?title ?id
                        {
                            ?tune mm:title ?title.
                            ?tune jams:tuneId ?id.
                        }
                     """
    return sparql_query


# Get the pattern node data for the network visualisation.
def get_neighbour_patterns_by_tune(id, click_num, excludeTrivialPatterns):
    offset = NUM_NODES*int(click_num)
    sparql_query =   """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm: <http://w3id.org/polifonia/ontology/music-meta/>
                        SELECT ?pattern (count(?pattern) as ?patternFreq)
                        {
                            ?tune jams:tuneId \"""" + id + """\".
                            ?xx jams:isJAMSAnnotationOf ?tune.
                            ?xx jams:includesObservation ?observation .
                            ?observation jams:hasPatternComplexity ?comp .
                        """
    if excludeTrivialPatterns == "true":
        sparql_query += """ FILTER (?comp > "0.4"^^xsd:float) .
                        """
    sparql_query +=     """?observation jams:ofPattern ?pattern .
                        } group by ?pattern order by DESC (?patternFreq) ?comp
                        OFFSET """ + str(offset) + " LIMIT " + str(NUM_NODES)
    return sparql_query


# Get the tune node data for the network visualisation.
def get_neighbour_tunes_by_pattern(pattern, click_num):
    offset = NUM_NODES*int(click_num)
    sparql_query =       """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                            PREFIX mm:<http://w3id.org/polifonia/ontology/music-meta/>
                            PREFIX ptn:<http://w3id.org/polifonia/resource/pattern/>
                            SELECT distinct ?title ?id ?family
                            WHERE
                            {
                                ?obs jams:ofPattern ptn:""" + pattern + """.
                                ?annotation jams:includesObservation ?obs.
                                ?annotation jams:isJAMSAnnotationOf ?musicalComposition.
                                ?musicalComposition jams:tuneId ?id.
                                ?musicalComposition jams:tuneFamily ?family.
                                OPTIONAL {?musicalComposition mm:title ?title}
                            }  ORDER BY ?title
                            OFFSET """ + str(offset) + " LIMIT " + str(NUM_NODES)
    return sparql_query


def get_tune_data(id):
    sparql_query =   """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                        PREFIX mm:<http://w3id.org/polifonia/ontology/music-meta/>
                        SELECT ?title ?tuneFamily
                        {
                            ?tune jams:tuneId \"""" + id + """\".
                            ?tune mm:title ?title.
                            ?tune jams:tuneFamily ?tuneFamily.
                        }"""
    return sparql_query


def get_tune_family_members(family):
    sparql_query =       """PREFIX jams:<http://w3id.org/polifonia/ontology/jams/>
                            PREFIX mm:<http://w3id.org/polifonia/ontology/music-meta/>
                            PREFIX fam:<http://w3id.org/polifonia/resource/tunefamily/>
                            SELECT distinct ?title ?id ?type
                            WHERE
                            {
                                ?tune jams:tuneFamily fam:"""+family+""".
                                OPTIONAL {?tune mm:title ?title}
                                OPTIONAL {?tune jams:tuneId ?id}
                                OPTIONAL {?tune jams:tuneType ?type}
                            } ORDER BY ASC (?title)"""
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
