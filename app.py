from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
from query_factory import get_tune_given_name

app = Flask(__name__)
CORS(app)

BLAZEGRAPH_URL = 'https://polifonia.disi.unibo.it/fonn/sparql'
MOCK = True


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
    # Get the query parameters from the GET request
    query_params = request.args.to_dict()

    if MOCK:
        return mock_data(query_params)

    # Generate the SPARQL query
    sparql_query = get_tune_given_name(query_params['query'])

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


@app.route('/api/similarity-measures', methods=['GET'])
def similarity_measures_api():
    # Return a list of similarity measures
    return jsonify(["Measure 1", "Measure 2", "Measure 3"]), 200


if __name__ == "__main__":
    app.run(debug=True)
