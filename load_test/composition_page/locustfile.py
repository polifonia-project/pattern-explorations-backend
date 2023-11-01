# Composition page load test
# For each user make 4-5 queries about pairwise similarity between tunes + get all patterns from tunes

from locust import HttpUser, task, between



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


class ApiUser(HttpUser):
    wait_time = between(1, 2)  # Wait between 1 to 2 seconds between tasks

    @task
    def make_api_calls(self):
        # Simulating 5 simultaneous API calls
        self.client.get("/api1")
        self.client.get("/api2")
        self.client.get("/api3")
        self.client.get("/api4")
        self.client.get("/api5")
