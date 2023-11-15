from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from query_factory import (get_tune_given_name, get_all_tune_names,
                           get_pattern_search_query,
                           advanced_search, get_most_common_patterns_for_a_tune,
                           get_neighbour_patterns_by_tune, get_neighbour_tunes_by_pattern,
                           get_tune_data, get_tune_family_members)

app = Flask(__name__)
CORS(app)

MOCK = False
LOCALSERVER = False

if LOCALSERVER:
    BLAZEGRAPH_URL = 'http://localhost:9999/bigdata/sparql'
    #BLAZEGRAPH_URL = 'http://localhost:9999/blazegraph/sparql'
else:
    BLAZEGRAPH_URL = 'https://polifonia.disi.unibo.it/fonn/sparql'

all_names = None


# Return a list of all tune names
def dl_tune_names():
    global all_names
    # Generate the SPARQL query
    sparql_query = get_all_tune_names()
    # Execute the SPARQL query
    response = requests.post(
        BLAZEGRAPH_URL,
        data={
            'query': sparql_query,
            'format': 'json'
        }
    )
    #print(sparql_query)
    #print(response.text)
    # Check the response status
    if response.status_code != 200:
        print('Failed to execute SPARQL query')
        #TODO: Correctly handle this error.
    else:
        namesJSON = response.json()
        #all_names = [item['title']['value'] for item in namesJSON['results']['bindings']]
        all_names = [[item[var]['value'] for item in namesJSON['results']['bindings']] for var in ['title', 'id']]
        #print(all_names)
        #print(all_names[0][200])
        #print(all_names[1][200])

def mock_data(query_params):
    # Mock data
    data = {
        "tunes": [
            {
                "id": "1",
                "name": "Spring",
                "year": 1723,
                "composer": "Antonio Vivaldi",
                "midiUrl": "http://example.com/vivaldi/spring.mid",
                "notationUrl": "http://example.com/vivaldi/spring.pdf",
                "otherInfo": {
                    "part": "Allegro",
                    "composition": "The Four Seasons"
                }
            },
            {
                "id": "2",
                "name": "Summer",
                "year": 1723,
                "composer": "Antonio Vivaldi",
                "midiUrl": "http://example.com/vivaldi/summer.mid",
                "notationUrl": "http://example.com/vivaldi/summer.pdf",
                "otherInfo": {
                    "part": "Presto",
                    "composition": "The Four Seasons"
                }
            },
            {
                "id": "3",
                "name": "Canon in D",
                "year": 1680,
                "composer": "",
                "midiUrl": "http://example.com/pachelbel/canon.mid",
                "notationUrl": "http://example.com/pachelbel/canon.pdf",
                "otherInfo": {}
            },
            {
                "id": "4",
                "name": "Toccata and Fugue in D minor",
                "year": "",
                "composer": "Johann Sebastian Bach",
                "midiUrl": "http://example.com/bach/toccata.mid",
                "notationUrl": "http://example.com/bach/toccata.pdf",
                "otherInfo": {}
            }
            # More mock data can be added here
        ],
        "query_params": query_params
    }
    return jsonify(data), 200


@app.route('/api/search', methods=['GET'])
def search():
    global all_names
    # Get the query parameters from the GET request
    query_params = request.args.to_dict()
    if MOCK:
        return mock_data(query_params)
    if(query_params['searchType'] == "title"):
        # Generate the SPARQL query
        sparql_query = get_tune_given_name(query_params['searchTerm'], all_names)
    elif(query_params['searchType'] == "pattern"):
        sparql_query = get_pattern_search_query(query_params['searchTerm'])
        #print(sparql_query)
    elif(query_params['searchType'] == "advanced"):
        #print(query_params)
        sparql_query = advanced_search(query_params, all_names)
    else:
        # Error message.
        return jsonify({'error': 'Invalid search type.'}), 501
    # Execute the SPARQL query
    response = requests.post(
        BLAZEGRAPH_URL,
        data={
            'query': sparql_query,
            'format': 'json'
        }
    )
    #print(sparql_query)
    #print(response.text)
    # Check the response status
    if response.status_code != 200:
        return jsonify({'error': 'Failed to execute SPARQL query'}), 500
    # Return the JSON data
    return jsonify(response.json()), 200


@app.route('/api/similarity-measures', methods=['GET'])
def similarity_measures_api():
    # Return a list of similarity measures
    return jsonify(["Measure 1", "Measure 2", "Measure 3"]), 200


@app.route('/api/patterns', methods=['GET'])
def getPatterns():
    # Get the query parameters from the GET request
    query_params = request.args.to_dict()
    # Generate the SPARQL query
    #print(query_params)
    sparql_query = get_most_common_patterns_for_a_tune(query_params['id'],
                                                       query_params['excludeTrivialPatterns'])
    # Execute the SPARQL query
    response = requests.post(
        BLAZEGRAPH_URL,
        data={
            'query': sparql_query,
            'format': 'json'
        }
    )
    #print(sparql_query)
    #print(response.text)
    # Check the response status
    if response.status_code != 200:
        return jsonify({'error': 'Failed to execute SPARQL query'}), 500
    # Return the JSON data
    return jsonify(response.json()), 200


@app.route('/api/neighbour_patterns', methods=['GET'])
def getNeighbourPatterns():
    # Get the query parameters from the GET request
    query_params = request.args.to_dict()
    # Generate the SPARQL query
    #print(query_params)
    sparql_query = get_neighbour_patterns_by_tune(query_params['id'],
                                                  query_params['excludeTrivialPatterns'])
    # Execute the SPARQL query
    response = requests.post(
        BLAZEGRAPH_URL,
        data={
            'query': sparql_query,
            'format': 'json'
        }
    )
    #print(sparql_query)
    #print(response.text)
    # Check the response status
    if response.status_code != 200:
        return jsonify({'error': 'Failed to execute SPARQL query'}), 500
    # Return the JSON data
    return jsonify(response.json()), 200


@app.route('/api/neighbour_tunes', methods=['GET'])
def getNeighbourTunes():
    # Get the query parameters from the GET request
    query_params = request.args.to_dict()
    # Generate the SPARQL query
    #print(query_params)
    sparql_query = get_neighbour_tunes_by_pattern(query_params['id'])
    # Execute the SPARQL query
    response = requests.post(
        BLAZEGRAPH_URL,
        data={
            'query': sparql_query,
            'format': 'json'
        }
    )
    #print(sparql_query)
    #print(response.text)
    # Check the response status
    if response.status_code != 200:
        return jsonify({'error': 'Failed to execute SPARQL query'}), 500
    # Return the JSON data
    return jsonify(response.json()), 200


@app.route('/api/tune_by_id', methods=['GET'])
def getTuneData():
    # Get the query parameters from the GET request
    query_params = request.args.to_dict()
    # Generate the SPARQL query
    #print(query_params)
    sparql_query = get_tune_data(query_params['id'])
    # Execute the SPARQL query
    response = requests.post(
        BLAZEGRAPH_URL,
        data={
            'query': sparql_query,
            'format': 'json'
        }
    )
    #print(sparql_query)
    #print(response.text)
    # Check the response status
    if response.status_code != 200:
        return jsonify({'error': 'Failed to execute SPARQL query'}), 500
    # Return the JSON data
    return jsonify(response.json()), 200


@app.route('/api/tuneFamilyMembers', methods=['GET'])
def getTuneFamilyMembers():
    # Get the query parameters from the GET request
    query_params = request.args.to_dict()
    # Generate the SPARQL query
    #print(query_params)
    sparql_query = get_tune_family_members(query_params['family'])
    # Execute the SPARQL query
    response = requests.post(
        BLAZEGRAPH_URL,
        data={
            'query': sparql_query,
            'format': 'json'
        }
    )
    print(sparql_query)
    print(response.text)
    # Check the response status
    if response.status_code != 200:
        return jsonify({'error': 'Failed to execute SPARQL query'}), 500
    # Return the JSON data
    return jsonify(response.json()), 200


app.setup = [(None, dl_tune_names())]

if __name__ == "__main__":
    app.run(debug=True)
