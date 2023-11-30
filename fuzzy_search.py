from singleton_decorator import singleton
from query_factory import get_all_tune_names
import requests
from fuzzywuzzy import process as fuzzy_process


@singleton
class FuzzySearch:
    def __init__(self, blazegraph_url):
        # Generate the SPARQL query
        sparql_query = get_all_tune_names()
        # Execute the SPARQL query
        response = requests.post(
            blazegraph_url,
            data={
                'query': sparql_query,
                'format': 'json'
            }
        )
        # Check the response status
        if response.status_code != 200:
            raise ConnectionError(f"Unable to get all composition names from SPARQL endpoint: {blazegraph_url}.\n"
                                  f"Server response code: {response.status_code}\n"
                                  f"Server response: {response.text}")

        namesJSON = response.json()
        self.names = {item['id']['value']: item['title']['value'] for item in namesJSON['results']['bindings']}

    def get_title_best_match(self, title, score_cutoff=60, limit=50, retry_till_match=True, max_retries=3):
        best_matches = fuzzy_process.extractBests(title, self.names,
                                                  score_cutoff=score_cutoff,
                                                  limit=limit)
        if not best_matches and retry_till_match:
            retry_count = 0
            while not best_matches and retry_count < max_retries:
                retry_count += 1
                score_cutoff /= 2
                best_matches = fuzzy_process.extractBests(title, self.names,
                                                          score_cutoff=score_cutoff,
                                                          limit=limit)
        return best_matches
