from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from query_factory import (get_tune_given_name, get_pattern_search_query,
                           advanced_search, get_most_common_patterns_for_a_tune,
                           get_neighbour_patterns_by_tune, get_neighbour_tunes_by_pattern,
                           get_tune_data, get_tune_family_members)

from fuzzy_search import FuzzySearch

app = Flask(__name__)
CORS(app)

BLAZEGRAPH_URL = 'https://polifonia.disi.unibo.it/fonn/sparql'
EMPTY_SEARCH_RESPONSE = {"head":{"vars":["tune_name", "tuneType", "key", "signature", "id"]},"results":{"bindings":[]}}
fuzzy_search = FuzzySearch(BLAZEGRAPH_URL)


@app.route('/api/search', methods=['GET'])
def search():
    # Get the query parameters from the GET request
    query_params = request.args.to_dict()
    # Compostion Title based search
    search_type = query_params['searchType']
    sparql_query = ""
    if search_type == "title":
        search_term = query_params['searchTerm']
        fuzzy_title_matches = fuzzy_search.get_title_best_match(search_term)
        if not fuzzy_title_matches:
            # If there are no matched titles, return an empty response.
            return jsonify(EMPTY_SEARCH_RESPONSE), 200
        else:
            # Generate the SPARQL query
            sparql_query = get_tune_given_name(fuzzy_title_matches)
    # Patters based search
    elif search_type == "pattern":
        search_term = query_params['searchTerm']
        sparql_query = get_pattern_search_query(search_term)
    # Advanced search
    elif search_type == "advanced":
        matched_tuples = []
        if query_params['title']:
            search_term = query_params['title']
            matched_tuples = fuzzy_search.get_title_best_match(search_term)
        if query_params['title'] and not matched_tuples:
            # If a title is searched for and there are no matched titles, return an empty response.
            return jsonify(EMPTY_SEARCH_RESPONSE), 200
        else:
            sparql_query = advanced_search(query_params, matched_tuples)
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
    # Check the response status
    if response.status_code != 200:
        print(f"Error executing Sparql Query = {sparql_query}")
        print(response.json())
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


@app.route('/api/tunes_by_pattern', methods=['GET'])
def getTunesContainingPattern():
    # Get the query parameters from the GET request
    query_params = request.args.to_dict()
    # Generate the SPARQL query
    #print(query_params)
    sparql_query = get_pattern_search_query(query_params['pattern'])
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


if __name__ == "__main__":
    app.run(debug=True)
    #app.run(host='192.168.0.94')
    #app.run(host='10.226.144.193')
