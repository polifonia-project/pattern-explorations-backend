import random
from locust import HttpUser, task, between

BLAZEGRAPH_URL = 'https://polifonia.disi.unibo.it/fonn/sparql'

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


class ApiUser(HttpUser):
    wait_time = between(1, 2)  # Wait between 1 to 2 seconds between tasks
    names = ["Maggie", "Johnny", "DE RUITER", "Foxhunters", "First Of May", "College Groves", "Gilderoy", "PINKSTERLIED I"]

    @task
    def make_api_calls(self):
        idxs = list(range(len(self.names)))
        random.shuffle(idxs)

        query = get_tune_given_name2(self.names[idxs[0]])
        response = self.client.post(
            BLAZEGRAPH_URL,
            data={
                'query': query,
                'format': 'json'
            }
        )
