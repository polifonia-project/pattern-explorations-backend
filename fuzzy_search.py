from query_factory import get_all_tune_names
import requests

BLAZEGRAPH_URL = 'https://polifonia.disi.unibo.it/fonn/sparql'

class fuzzySearch:
    def __init__(self):
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
        # Check the response status
        if response.status_code != 200:
            print('Failed to execute SPARQL query')
            #TODO: Correctly handle this error.
        else:
            namesJSON = response.json()
            self.names = {item['id']['value']: item['title']['value'] for item in namesJSON['results']['bindings']}
